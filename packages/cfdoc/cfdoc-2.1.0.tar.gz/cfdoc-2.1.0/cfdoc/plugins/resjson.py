"""
Extract the resource definition JSON from the CloudFormation template and format it.

Any metadata tag in the resource definition is removed.

It creates a new JSON entry in the resource doc entries.

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

import json
import logging

from cfdoc.plugins import plugin

__author__ = 'Murray Andrews'

LOG = logging.getLogger()

INDENT = 4  # JSON indenting
INDENT_MAX = 8
INDENT_MIN = 1


# ------------------------------------------------------------------------------
@plugin('resjson')
def cfd_plugin(cfdoc, indent=INDENT, **kwargs):
    """
    Extract the resource JSON from the CloudFormation template.

    :param cfdoc:       A CFdoc object.
    :param indent:      Indent level for the JSON. If passed in from the main
                        program this will be a string.
    :param kwargs:      Soak up any unrecognised parameters.

    :type cfdoc:        CFdoc
    :type indent:       str | int

    """

    if kwargs:
        LOG.error('Plugin %s: Unexpected arguments ignored: %s', cfd_plugin.name, ', '.join(kwargs))

    try:
        indent = int(indent)
        if not INDENT_MIN <= indent <= INDENT_MAX:
            raise ValueError
    except ValueError:
        raise Exception(
            f'Plugin {cfd_plugin.name}:'
            f' indent must be an integer between {INDENT_MIN} and {INDENT_MAX}'
        )

    cf_resources = cfdoc.template.get('Resources')

    # ----------------------------------------
    # Go through each resource doc entry, look for ones with no description
    # and see if the resource properties can supply one.

    for rsrc_id in cfdoc.resources:

        rsrc_info = cfdoc.resources[rsrc_id]

        # Take a copy of the resource definition so we can delete metadara.
        # Shallow copy is ok.

        resource_def = cf_resources[rsrc_id].copy()
        if 'Metadata' in resource_def:
            del resource_def['Metadata']

        rsrc_info['JSON'] = json.dumps(
            resource_def, indent=indent, sort_keys=True, separators=(',', ': ')
        )
