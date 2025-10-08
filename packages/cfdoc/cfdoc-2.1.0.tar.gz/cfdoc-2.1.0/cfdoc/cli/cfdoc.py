#!/usr/bin/env python3

"""
Extract documentation from a CloudFormation template.

Copyright (c) 2016, Murray Andrews
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

1.  Redistributions of source code must retain the above copyright notice, this
    list of conditions and the following disclaimer.

2.  Redistributions in binary form must reproduce the above copyright notice,
    this list of conditions and the following disclaimer in the documentation and/or
    other materials provided with the distribution.

3.  Neither the name of the copyright holder nor the names of its contributors
    may be used to endorse or promote products derived from this software without
    specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""

from __future__ import annotations

import argparse
import json
import logging.handlers
import os
import sys
from collections import OrderedDict
from datetime import UTC, datetime
from importlib import resources
from pathlib import Path
from typing import Any, TextIO

import jinja2
import yaml
from colorama import init

from cfdoc.lib.argparse import StoreNameValuePair
from cfdoc.lib.jinja2 import j2_escape_markdown, j2_md_xref, j2_re_match, j2_sort_multi_attributes
from cfdoc.lib.logging import ColourLogHandler, get_log_level
from cfdoc.lib.misc import mget, paragraphs
from cfdoc.plugins import plugins
from cfdoc.version import __version__

__author__ = 'Murray Andrews'

PROG = Path(sys.argv[0]).stem
CFDOCPATH = f':templates:{resources.files("cfdoc") / "templates"}:'
CFD_URL = 'https://bitbucket.org/murrayandrews/cfdoc'

# Keys containing documentation elements. A couple of variants are accepted but
# the first one is preferred. Must be in CloudFormation template Metadata.
K_CFDOC = ('CFdoc', 'Cfdoc', 'cfdoc')

LOG = logging.getLogger()

# Colorama init.
init()


# ------------------------------------------------------------------------------
class CFdoc:
    """
    Represents the documentation elements extracted from a CloudFormation template.

    This structure is loaded from a CloudFormation template file, then passed to
    any available and enabled plugins for manipulation, then sent to a (Jinja2)
    rendering engine.

    The following instance attributes are potentially useful to plugins and
    Jinja2 templates:

    template:   The data structure holding the full JSON of the CloudFormation
                base template.

    name:       Name of the template, typically derived from the name of the
                CloudFormation template file.

    title:      Derived from the main Description tag in the CF template.

    overview:   An ordered dictionary of data items extracted from the CFdoc
                tag in the main Metadata tag for the CF template. There are a
                bunch of "standard" items that are located first, then any
                other tag the template author cares to add will also be
                included. With the exception of the special tag 'Groups', the
                values of these keys must be either a string or a list of
                strings.

                "Ordered" here means:

                    - Standard keys in a fixed order.

                    - User defined keys in alphabetic order.

                This is done so that the generated documentation always presents
                template information in a fixed arrangement.

                The optional Groups tag is used to assign resources to resource
                groups for documentation purposes. Its value must be a list of
                dictionaries. Each dictionary must contain an 'Id' and a 'Name'
                key. The former is the group ID and can be referenced by 'Group'
                keys in the CFdoc entries for resources.  The 'Name' key should
                be a short display name for the group.  Typically, documentation
                rendering templates will render present resource groups in the
                order in which they are defined in the 'Groups' list.

    parameters: An ordered dictionary of parameters from the CloudFormation
                template. Keys are parameter names and the values are
                ordered dictionaries containing 'Type' and 'Description' keys.
                The latter is derived from the parameter specification in the
                CF template by combining the parameter 'Description' and
                'ConstraintDescription' elements.

    resources:  An ordered dictionary containing the documentation items for each
                resource in the CloudFormation template. Keys are the resource
                names as given in the CF template. Values are ordered dictionaries
                of information items about the resource. Ordered in this case
                means:

                    - Type key first.

                    - Standard keys in a fixed order

                    - User defined keys in alphabetic order.

                This is done so that the generated documentation always presents
                resource information in a fixed arrangement for each resource.

                The 'Type' item is extracted from the 'Type' key in the CF
                resoource specification. All other items are extracted from the
                CFdoc tag in the Metadata for the resource. With the exception
                of the Group key, the values for the items in the CFdoc tag
                must be a string or a list of strings. The value of the Group
                key must be a string and should consist of one of the group IDs
                from the 'Groups' tag in the main CF template Metadata/CFdoc.

    resource_groups:
                An ordered dictionary of resource groups defined in the 'Groups'
                key in the main template Metadata/CFdoc. The order in which
                the groups were listed in the 'Groups' key is preserved. The
                value of each item is a dictionary containing a 'Name' key
                (the group Name) and a 'Members' key. The latter is a list of
                resource names in the group, sorted by resource name. This is
                also a key into the resources attribute described above.

                In addition to the explicitly specified groups, there may also
                be a group with a key of None, holding resources not otherwise
                assigned to a defined group. Plugins seeking to manipulate
                the group information must take care to maintain referential
                integrity.

                Note that some groups may have no members.

    outputs:    An (alphabetically) ordered dictionary of documentation for the
                'Outputs' defined in the CloudFormation template. Keys are
                output names and values are ordered dictionaries, currently,
                containing only a 'Description' key with a value derived from
                the CF template.

    plugins:    The structures described above (apart from the template attribute)
                can be manipulated by plugins (including adding additional fields
                to the information for individual resources and parameters
                defined above).

                Plugins can also provide additional information in the plugins
                dictionary attribute. Well behaved plugins will create an entry
                in the plugins dictionary with the plugin name as the key. What
                happens under that is plugin specific.

    """

    # Standard template overview tags.
    OVERVIEW_TAGS = [
        'Version',
        'Description',
        'Author',
        'Licence',
        'License',
        'Prerequisities',
        'Changes',
    ]

    OVERVIEW_RESERVED_TAGS = ['Groups']

    # Standard template resource tags. Printed in the order given.
    RESOURCE_TAGS = ['Description', 'Dependencies', 'Warnings']

    RESOURCE_RESERVED_TAGS = ['Group']

    # --------------------------------------------------------------------------
    def __init__(self, name: str, template: dict[str, Any]):
        """
        Initialise cfdoc object.

        :param name:        The template name (typically a file name). Used only
                            for labelling so content is arbitrary.
        :param template:    A template object. Must be a dict containing the
                            elements expected in a CloudFormation template.
        :raise ValueError:  If the template is not a dict.
        """

        if not isinstance(template, dict):
            raise ValueError(f'Malformed template: expected dict, got {type(template)}')

        self._template = template
        self.name = name
        self.title = None
        self.resources = OrderedDict()  # The documentation components of each resource
        self.resource_groups = OrderedDict()  # Resource resource_groups
        self.overview = OrderedDict()  # Template level doc items
        self.parameters = OrderedDict()
        self.outputs = OrderedDict()
        self.plugins = {}  # Allow plugins to add their own data elements.

        self.resource_groups[None] = {'Name': 'Ungrouped Resources', 'Members': []}

        # ----------------------------------------
        # Make sure it is a CloudFormation template

        if not template.get('AWSTemplateFormatVersion'):
            raise ValueError(f'{name}: No AWSTemplateFormatVersion key')

        # ----------------------------------------
        # Process the template
        self._process_header()
        self._process_params()
        self._process_resources()
        self._process_outputs()

    # --------------------------------------------------------------------------
    def _process_header(self):
        """
        Process the header section of the template.

        This consists of the main "Description" key and the main "
        """

        LOG.debug('Processing CloudFormation template header')

        # ----------------------------------------
        # One line title is taken from the template "Description" tag.
        try:
            self.title = self._template['Description']
        except KeyError:
            LOG.warning('No template Description key')
            self.title = f'Template {self.name}'

        # ----------------------------------------
        # Look for a Metadata section containing a CFdoc key
        metadata = self._template.get('Metadata')
        if not metadata:
            LOG.warning('No template Metadata key')
            return

        doc = mget(metadata, K_CFDOC)
        if not doc:
            LOG.warning('No %s key in template metadata', K_CFDOC[0])
            return

        # ----------------------------------------
        # Retrieve the standard CFdoc tags. We do this first to preserve ordering
        for key in self.__class__.OVERVIEW_TAGS:
            if doc.get(key):
                self.overview[key] = paragraphs(doc.get(key))

        # Pickup any additional fields in alphabetical order (ignore reserved metatags)
        for key in sorted(
            set(doc) - set(self.overview) - set(self.__class__.OVERVIEW_RESERVED_TAGS)
        ):
            self.overview[key] = paragraphs(doc.get(key))

        # ----------------------------------------
        # Look for an optional resource groups key which is a list of resource
        # groups. Each element is an object containing "Id" and "Name" keys.
        # Individual resources can point to the Id.
        # There is a default None group for ungrouped resources.

        rsrc_group_list = doc.get('Groups', [])
        if not isinstance(rsrc_group_list, list):
            LOG.error('Malformed resource group list in main %s key', K_CFDOC[0])
        else:
            for group in rsrc_group_list:
                if not isinstance(group, dict):
                    LOG.error('Malformed resource group: %s', group)
                    continue
                rgrp_id = group.get('Id')
                if not rgrp_id:
                    print(80 * '[')
                    LOG.error('Resource group with no Id: %s', group)
                    continue
                self.resource_groups[rgrp_id] = {'Name': group.get('Name', rgrp_id), 'Members': []}

    # --------------------------------------------------------------------------
    def _process_params(self):
        """Process any CF template parameters."""

        LOG.debug('Processing CloudFormation template parameters')

        params = self._template.get('Parameters')
        if not params:
            return

        for p in sorted(params):
            v = params[p]
            self.parameters[p] = OrderedDict()
            self.parameters[p]['Type'] = v.get('Type', '?')
            self.parameters[p]['Description'] = paragraphs(v.get('Description')) + paragraphs(
                v.get('ConstraintDescription')
            )

    # --------------------------------------------------------------------------
    def _process_resources(self):
        """
        Process resource definitions in the CF template.

        These may have Group attribute to assign them to a resource group.
        """

        LOG.debug('Processing CloudFormation template resources')

        cf_resources = self._template.get('Resources')
        if not cf_resources:
            LOG.error('No Resources key')
            return

        for rsrc_id in sorted(cf_resources):
            if rsrc_id in self.resources:
                LOG.warning('Resource %s: duplicate ignored', rsrc_id)
                continue

            # ----------------------------------------
            # Extract the cfdoc for the resource from the metadata tag

            doc = {}
            rsrc = cf_resources[rsrc_id]
            if not isinstance(rsrc, dict):
                LOG.error('Resource %s: object expected - skipping', rsrc_id)
                continue

            metadata = rsrc.get('Metadata')
            if not metadata:
                LOG.info('Resource %s: no Metadata key', rsrc_id)
            else:
                doc = mget(metadata, K_CFDOC, {})
                if not doc:
                    LOG.info('Resource %s: no %s key in Metadata', rsrc_id, K_CFDOC[0])

            # ----------------------------------------
            # Create an empty dict for the resource documentation attributes.
            rsrc_info = OrderedDict()

            # ----------------------------------------
            # Extract the resource type
            rsrc_info['Type'] = rsrc.get('Type')
            if not rsrc_info['Type']:
                LOG.error('Resource %s: no resource type specified', rsrc_id)

            # ----------------------------------------
            # Get the resource group id for this resource. If its not a known group
            # we create a new resource group but issue a warning. The resource group may be None.
            rsrc_info['Group'] = rsrc_group = doc.get('Group')
            if rsrc_group not in self.resource_groups:
                LOG.warning('Resource %s: unknown resource group %s', rsrc_id, rsrc_group)
                self.resource_groups[rsrc_group] = {'Name': rsrc_group, 'Members': []}

            self.resource_groups[rsrc_group]['Members'].append(rsrc_id)

            # ----------------------------------------
            # Look for the cfdoc standard tags
            for key in self.__class__.RESOURCE_TAGS:
                rsrc_info[key] = paragraphs(doc.get(key))

            # Pickup any additional fields in alphabetical order (ignore reserved tags)
            for key in sorted(
                set(doc) - set(rsrc_info) - set(self.__class__.RESOURCE_RESERVED_TAGS)
            ):
                rsrc_info[key] = paragraphs(doc.get(key))

            self.resources[rsrc_id] = rsrc_info

    # --------------------------------------------------------------------------
    def _process_outputs(self):
        """Process output definitions in the CloudFormation template."""

        LOG.debug('Processing CloudFormation template outputs')

        outputs = self._template.get('Outputs')
        if not outputs:
            return

        for op in sorted(outputs):
            v = outputs[op]
            self.outputs[op] = OrderedDict()
            self.outputs[op]['Description'] = v.get('Description')
            self.outputs[op]['Export'] = v.get('Export', {}).get('Name')
            if not self.outputs[op]['Description']:
                LOG.warning('Output %s: no Description key', op)

    # --------------------------------------------------------------------------
    @property
    def template(self) -> dict[str, Any]:
        """Return the cloudformation template object."""

        return self._template

    # --------------------------------------------------------------------------
    def render(self, fmt: str) -> str:
        """
        Render the CFdoc object using the specified format.

        The format is used to determine the name of a Jinja2 template file.

        :param fmt:     Format name. A file 'fmt.jinja2' must exist in
                        the CFDOC path (specified by the environment variable
                        CFDOCPATH.
        """

        jtemplate = f'{fmt}.jinja2'
        jinja_path = os.environ.get('CFDOCPATH', CFDOCPATH).split(':')
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(jinja_path), autoescape=True)
        env.filters['re_match'] = j2_re_match
        env.filters['asort'] = j2_sort_multi_attributes
        env.filters['xref'] = j2_md_xref
        env.filters['e_md'] = j2_escape_markdown

        jtemplate = env.get_template(jtemplate)

        # Common parameters.
        common = {
            'prog': PROG,
            'project_url': CFD_URL,
            'now_iso': datetime.now().isoformat(),
            'now_ctime': datetime.now().ctime(),
            'utcnow_iso': datetime.now(UTC).isoformat(),
        }

        return jtemplate.render(cfdoc=self, common=common)


# ------------------------------------------------------------------------------
def dofile(
    ofmt: str,
    ifp: TextIO = None,
    ofp: TextIO = None,
    name: str = None,
    params: dict[str, dict[str, str]] = None,
    ifmt: str = 'JSON',
) -> None:
    """
    Process a CloudFormation template file.

    :param ofmt:    Required output format. There must be a file fmt.jinja2 in
                    the CFDOCPATH somewhere.
    :param ifp:     Input template file stream. Default stdin.
    :param ofp:     File stream for rendered output. Default stdout.
    :param name:    Template name. If None, the filename associated with the input
                    stream is used. Default None.
    :param params:  A dictionary of parameters for the plugins. The keys
                    are the plugin names. Values are a dictionary of parameters
                    for the plugin that will be passed as kwargs to the entry
                    point.
    :param ifmt:    Format of CloudFormation file -- either 'JSON' or 'YAML'.
                    Default 'JSON'.

    :raise Exception:   If the JSON template file is malformed.
    """

    if not ifp:
        ifp = sys.stdin
    if not ofp:
        ofp = sys.stdout

    # ----------------------------------------
    # Get a loader based on file format.
    if ifmt.upper() == 'YAML':
        loader = yaml.safe_load
    elif ifmt.upper() == 'JSON':
        loader = json.load
    else:
        raise ValueError(f'Unknown input format: {ifmt}')

    # ----------------------------------------
    # Load and analyse the CloudFormation template.
    try:
        template_obj = loader(ifp)
    except Exception as e:
        raise Exception(f'{ifp.name}: Could not load file - {e}')

    doc = CFdoc(name or ifp.name, template_obj)

    # ----------------------------------------
    # Run the plugins

    for p in plugins():
        LOG.debug('Running plugin %s', p.name)
        pp = params.get(p.name, {}) if params else {}
        try:
            p.func(doc, **pp)
        except Exception as e:
            raise Exception(f'Plugin {p.name}: {e}')

    # ----------------------------------------
    # Render the output
    LOG.debug('Rendering in format %s', ofmt)
    print(doc.render(fmt=ofmt), file=ofp)


# ------------------------------------------------------------------------------
def parse_cli_args() -> argparse.Namespace:
    """Parse command line args."""

    argp = argparse.ArgumentParser(
        prog=PROG,
        description='Extract documentation from an AWS CloudFormation template.',
        epilog=f'For more information: {CFD_URL}',
    )

    argp.add_argument(
        '-c',
        '--no-colour',
        '--no-color',
        dest='no_colour',
        action='store_true',
        default=False,
        help='Don\'t use colour in information messages.',
    )
    argp.add_argument(
        '-d',
        '--define',
        metavar='plugin.param=value',
        dest='plugin_params',
        action=StoreNameValuePair,
        help='Define params for plugins.',
    )
    argp.add_argument(
        '-f',
        '--format',
        action='store',
        default='html',
        help='Output format (default html). Must correspond to a'
        ' Jinja2 template named FORMAT.jinja2',
    )
    argp.add_argument(
        '-l',
        '--level',
        metavar='LEVEL',
        default='warning',
        help='Print messages of a given severity level or above.'
        ' The standard logging level names are available but info,'
        ' warning and error are most useful. The Default is warning.',
    )
    argp.add_argument(
        '--list-plugins',
        dest='list_plugins',
        action='store_true',
        help='List available plugins and exit.',
    )
    argp.add_argument(
        '-n',
        '--name',
        help='CloudFormation template name (not file name).'
        ' If not specified the name of the input file is used.',
    )
    argp.add_argument(
        '-v', '--version', action='version', version=__version__, help='Show version and exit.'
    )
    argp.add_argument(
        '-y',
        '--yaml',
        action='store_true',
        help='The CloudFormation template is in YAML format. This is'
        ' required when the format cannot be guessed from the'
        ' file suffix. JSON format is assumed by default.',
    )
    argp.add_argument(
        'template',
        nargs='?',
        type=argparse.FileType('r'),
        default=sys.stdin,
        help='CloudFormation template. Default stdin.',
    )

    return argp.parse_args()


# ------------------------------------------------------------------------------
def _main() -> int:
    """
    Show time.

    :return:    status
    """

    args = parse_cli_args()

    # Setup some logging
    LOG.addHandler(ColourLogHandler(colour=not args.no_colour))
    LOG.setLevel(get_log_level(args.level))
    LOG.debug('log level set to %s', LOG.getEffectiveLevel())

    if args.list_plugins:
        for p in plugins():
            print(f'{p.name}: {p.description}')
        return 0

    # Gather any plugin args. Each one must be of the form plugin.param=value.
    plugin_params = {p.name: {} for p in plugins()}
    if args.plugin_params:
        for plug_param in args.plugin_params:
            try:
                plugin_name, param_name = plug_param.split('.', 1)
            except ValueError:
                raise Exception(f'Invalid plugin parameter name: {plug_param}')

            try:
                plugin_params[plugin_name][param_name] = args.plugin_params[plug_param]
            except KeyError:
                raise Exception(
                    f'Plugin {plugin_name} is not loaded - cannot set parameters for it'
                )

    # ----------------------------------------
    # Do the business.

    ext = os.path.splitext(args.template.name)[1].lower()
    dofile(
        ofmt=args.format,
        ifp=args.template,
        ofp=sys.stdout,
        name=args.name,
        params=plugin_params,
        ifmt='YAML' if args.yaml or ext in ('.yml', '.yaml') else 'JSON',
    )
    return 0


# ------------------------------------------------------------------------------
def main() -> int:
    """Show time."""

    try:
        return _main()
    except KeyboardInterrupt:
        print('Interrupt', file=sys.stderr)
        exit(1)
    except Exception as ex:
        print(f'{PROG}: {ex}', file=sys.stderr)
        exit(1)


# ------------------------------------------------------------------------------
# This only gets used during dev/test. Once deployed as a package, main() gets
# imported and run directly.
if __name__ == '__main__':
    exit(main())
