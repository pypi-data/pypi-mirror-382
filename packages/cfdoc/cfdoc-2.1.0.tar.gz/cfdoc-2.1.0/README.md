# CFdoc - AWS CloudFormation Template Documentation Tool

**CFdoc** automatically generates hyperlinked documentation from
AWS CloudFormation templates.

[TOC]

## Overview

One of the limitations of AWS CloudFormation is the difficulty of embedding
comments or other documentation within the JSON used to construct CloudFormation
templates. While YAML can contain comments, it can be a tedious process to
extract and format useful documentation from them.

CloudFormation templates are not easy to read at the best of times and the
inability to properly describe them with embedded documentation makes them
difficult to analyse and maintain. That's where **CFdoc** comes in.

CFdoc exploits the ability to embed `Metadata` keys containing whatever you want
into the CloudFormation JSON. `Metadata` keys can be placed in:

* the top level of the CloudFormation template
* within each resource specification in the template.

CFdoc uses descriptive information placed in these keys, together with other
information derived from the template to automatically generate documentation.

Even where no special information has been embedded in the CloudFormation
template, CFdoc can generate linked documentation for the template that can be
much easier to comprehend than the template itself.

## Features

*   Automatically generates basic documentation from unmodified JSON or YAML
    CloudFormation templates.
*   Generated documentation covers CloudFormation template parameters,
    resources and outputs.
*   Processes embedded documentation / comments within the CloudFormation
    template to generate more comprehensive, unified documentation.
*   Embedded documentation can contain multi-line / multi-paragraph strings.
*   Embedded documentation has no impact on normal CloudFormation operation.
*   Will find and use _Description_ and _Group Description_ keys in
    CloudFormation parameter, resource and output specifications. (Only a few
    resource types support any form of description key.)
*   Supports plugins written in Python to process / extend the documentation
    content prior to rendering. e.g. one of the bundled plugins links AWS
    resource types to the corresponding AWS CloudFormation documentation.
*   Can support multiple documentation output contents, styles and formats
    using [Jinja2](http://jinja2.pocoo.org) rendering templates. A standard HTML
    rendering template is included.
*   Requires Python 3.

## Package Build

CFdoc is setup as a Python package. To build the package as a source tarball in
`dist/`:

```bash
make pkg
```

As part of the build process, it will also generate a man page,
`cfdoc/man/cfdoc.1` using the
[ronn](https://manpages.ubuntu.com/manpages/xenial/man1/ronn.1.html) utility.
A docker image containing **ronn** will be built as needed.

The package can be pushed to a PyPI server using:

```bash
make pypi
```

The default index server is labelled `pypi` which must be defined in `~/.pypirc`.
See the Makefile for details.

## Installation

```bash
pip install cfdoc
```

This will not install the man page. To do that, copy the provided `cfdoc.1` man
page to `/usr/local/share/man/man1/`.

The `cfdoc.1` file location can be found thus:

```bash
python3 -c 'from importlib import resources; print(resources.files("cfdoc") / "man/cfdoc.1")'
```

## Usage

Full details are given below.

Basic usage is available in the man page (see [Installation](#installation) above)
and with:

```bash
cfdoc --help
```

## Embedding Documentation in CloudFormation Templates

CloudFormation permits `Metadata` keys to be embedded both in the top level of
the CloudFormation template and also as a key within each resource specification
in the `Resources` section of the template. CloudFormation itself (mostly)
ignores the contents of the `Metadata` keys.

CFdoc exploits this to allow the CloudFormation template creator to embed more
comprehensive documentation. This is done by adding a `CFdoc` key within the
`Metadata` key and adding documentation related keys in `CFdoc`.

This is a skeleton of a CloudFormation template. Note the `Metadata` keys at the
document level and also within each resource specification.

```json
{
    "AWSTemplateFormatVersion": "version date",
    "Description": "JSON string",
    "Metadata": {
        template metadata
    },
    "Parameters": {
        set of parameters
    },
    "Mappings": {
        set of mappings
    },

    "Conditions": {
        set of conditions
    },
    "Resources": {
        "Logical ID": {
            "Type": "Resource type",
            "Metadata": {
                resource metadata
            }
            "Properties": {
                Set of properties
            }
        }
    }
    "Outputs": {
        set of outputs
    }
}
```

CFdoc uses the `Metadata` keys to allow the template author to embed
documentation by adding a `CFdoc` key within `Metadata`.

CFdoc recognises a set of standard keys within the `CFdoc` key but also
allows the template author to add non-standard keys of their own. Standard
and non-standard CFdoc keys are added to the generated documentation. 

Here is an example. 

```json
{
	"AWSTemplateFormatVersion": "2010-09-09",
	"Description": "CFdoc Demo Template",
	"Metadata": {
		"CFdoc": {
			"Description": "CloudFormation template fragment to demonstrate use of CFdoc",
			"Version": "1.0",
			"Author": "Fred Nurk",
			"Groups": [
                { "Id": "vpc", "Name": "VPC Related Resources" },
                { "Id": "S3", "Name": "S3 Resources" }
            ],
			"CustomKey": "This is an example of a user defined documentation key."
		}
	},
	"Parameters": {
		set of parameters
	},
	"Mappings": {
		set of mappings
	},
	"Conditions": {
		set of conditions
	},
	"Resources": {
		"myVPC": {
			"Type": "AWS::EC2:VPC",
			"Metadata": {
                    "CFdoc": {
                    "Description": [
                        "This is a sample VPC resource.",
                        "",
                        "This VPC resource demonstrates how multi-line/multi-paragraph",
                        "strings can be added as descriptions to resources. This description",
                        "will be interpreted as 2 paragraphs due to the blank line in the middle"
                    ],
                    "Group": "vpc"
                }
			},
			"Properties": {
				Set of properties for the VPC
			}
		},
		"myPolicy": {
			"Type": "AWS::IAM::ManagedPolicy",
			"Properties": {
			    "Description": "A sample IAM policy for CFdoc",
			    "PolicyDocument": {
			        Policy details
			    }
			}
		}
	}
	"Outputs": {
		set of outputs
	}
}
```

### Root Level Metadata

Note that a `Metadata` key has been added at the top level and a `CFdoc` key
within that. 
  
```json
"CFdoc": {
    "Description": "CloudFormation template fragment to demonstrate use of CFdoc",
    "Version": "1.0",
    "Author": "Fred Nurk",
    "Groups": [
        { "Id": "vpc", "Name": "VPC Related Resources" },
        { "Id": "S3", "Name": "S3 Resources" }
    ],
    "CustomKey": "This is an example of a user defined documentation key."
}
```

The `CFdoc` key contains some standard CFdoc keys and also a sample user defined
key `CustomKey`.

All of the keys are optional, although its a good idea to provide most of the
standard keys, particularly `Description`.  Standard root level CFdoc keys are:

*   Version
*   Description
*   Author
*   Licence (or License)
*   Prerequisites
*   Changes.

Apart from the `Groups` key which is handled differently, all of the other keys
are strings, or lists of strings, and will be rendered in the generated
documentation. The standard keys are rendered first in the order listed above,
followed by the user defined keys in alphabetic order.

When a list of strings is provided, the values are joined by CFdoc into a single
string. An empty string in the list denotes the start of a new paragraph.

It is possible to embed markup in the strings that is consistent with the
rendered documentation output format. So if the output format is HTML,
HTML markup can be included in the strings and will be rendered correctly
(including list structures).

#### The Groups Key

The optional `Groups` key is special. It is used to declare a set of resource
groups to which individual resources are then assigned for documentation
structuring purposes. Its value must be a list of dictionaries.  Each dictionary
must contain an `Id` and a `Name` key. The former is the group ID and can be
referenced by `Group` keys in the CFdoc entry for individual resources.  The
`Name` key should be a short display name for the group. Group IDs are case
sensitive.
 
```json
"Groups": [
    { "Id": "vpc", "Name": "VPC Related Resources" },
    { "Id": "S3", "Name": "S3 Resources" }
]
```

Typically, documentation rendering templates will present resource groups in the
order in which they are defined in the `Groups` list.

Any resource without an assigned group will be automatically assigned to an
_Ungrouped Resources_ group. One of the standard CFdoc plugins will automatically
assign resources to a group based on the resource type (S3, EC2 etc) if no
group is manually assigned. These auto-generated groups can still be listed
in the `Groups` object if its important to control the order in which they
are presented in the generated document.

### Resource Level Metadata

Each resource specification in a CloudFormation template can also include a
`Metadata` key, into which a `CFdoc` key can be placed for documentation
specific to the resource.

The sample JSON above includes two resources, the first one contains a `CFdoc`
key as shown below.

```json
"Resources": {
    "myVPC": {
        "Type": "AWS::EC2:VPC",
        "Metadata": {
            "CFdoc": {
                "Description": [
                    "This is a sample VPC resource.",
                    "",
                    "This VPC resource demonstrates how multi-line/multi-paragraph",
                    "strings can be added as descriptions to resources. This description",
                    "will be interpreted as 2 paragraphs due to the blank line in the middle"
                ],
                "Group": "vpc"
            }
        },
        "Properties": {
            Set of properties for the VPC
        }
    },
    ...
}
```

Note that the `Description` key is a list of strings which will be interpreted
as 2 paragraphs when rendered in the output documentation.

Once again, the resource level `CFdoc` can contain a set of standard keys as
well as user defined keys, all of which (with the exception of the special
`Group` key) will be rendered in the generated documentation.

The standard resource level keys are:

*   Description
*   Dependencies
*   Warnings.

Standard keys are rendered in the order shown above, followed by user defined
keys in alphabetic order.

As a second example, consider the following IAM managed policy resource. This
one does not contain a `CFdoc` key. However, this resource type is one of the
few that has a `Description` key within the standard AWS keys for the resource
properties. In this case, CFdoc will use that key for the description and will
automatically assign the resource to an IAM group in the generated
documentation.  Both of these actions are handled by CFdoc plugins. You can, of
course, supply CFdoc `Description` and `Group` keys to override these values.

```json
"Resources": {
    ...
    "myPolicy": {
        "Type": "AWS::IAM::ManagedPolicy",
        "Properties": {
            "Description": "A sample IAM policy for CFdoc",
            "PolicyDocument": {
                Policy details
            }
        }
    }
}
```

#### The Group Key

The `Group` key in the resource level `CFdoc` key has a string value that
references one of the resource group IDs in the document level CFdoc `Groups`
key. If no `Group` key is provided, one of the standard CFdoc plugins will
automatically assign a group based on the resource type category (IAM, EC2
etc.).

## Extending CFdoc

CFdoc can be extended by adding:

*   new [Jinja2](http://jinja2.pocoo.org) rendering templates to support
    different output styles and formats.
*   CFdoc plugins (written in Python) to augment the documentation structure
    prior to rendering.

If you do happen to attempt either of these, please let me know. If they're
of general interest, they can be included in the standard distribution.

### Rendering Templates

CFdoc uses [Jinja2](http://jinja2.pocoo.org) templates to render the final
documentation output.  A standard HTML template is provided. This produces a
single, fully self-contained HTML file (with the exception of links to AWS
documentation).

Users can add their own templates by adding a file of the form `myformat.jinja2`
in the `templates` directory. The template can be selected using the syntax:

```bash
cfdoc -f myformat ...
```

or

```bash
cfdoc --format myformat
```

Rendering templates are supplied with the following parameters:

|Parameter|Description|
|-|-|
|cfdoc|The CFdoc object instance containing the CloudFormation document object constructed by CFdoc. Its contents are described below.|
|common|An object containing the following general useful attributes.|
|common.prog|Name of the program (e.g. _cfdoc_). Template authors are requested to make this visible somewhere in the generated document.|
|common.project_url|A link to the CFdoc project page. Template authors are requested to make this visible somewhere in the generated document.|
|common.now_iso|The current local date and time in ISO 8601 format.|
|common.now_ctime|The current local date and time in ctime format.|
|common.utcnow_iso|The current UTC date and time in ISO 8601 format.|

### Plugins

The [CFdoc object instance](#the-cfdoc-object) described below
can be manipulated by plugins, including adding additional fields to the
information for individual resources and attributes defined below.

To add a plugin, write a Python module that implements the interface described
below and place it in the `plugins` directory. CFdoc will automatically discover
it. Plugins are invoked in alphabetic order, subject to control by command line
options.

#### Plugin Interface

Plugins must implement a callable (typically a function) that provides the
following signature:

```python
from cfdoc.plugins import plugin

@plugin('demo')
def cfd_plugin(cfdoc, **kwargs: str) -> None:
    """Demo plugin."""
    
    plugin_name = cfd_plugin.name  # cfd_plugin.name is added by the decorator
    ...
```

Named keyword arguments can be included, thus:

```python
import logging
from cfdoc.plugins import plugin

LOG = logging.getLogger()

@plugin('demo')
def cfd_plugin(cfdoc, arg: str=None, **kwargs: str):
    """Demo plugin."""
    
    if kwargs:
        # Report unexpected arguments but carry on.
        LOG.error('Plugin %s: Unexpected arguments ignored: %s', cfd_plugin.name, ', '.join(kwargs))

    ... 
```

Plugin keyword arguments are populated by command line arguments of the form `-d
plugin_name.arg=value`. The `**kwargs` argument should be present to soak up any
unrecognised parameters and avoid an exception. The plugin should emit an error
message if unrecognised parameters are provided.

Also:

*   The first line of the function docstring should be a brief summary of the
    functionality provided. This is used by the `--list-plugins` command line
    option.

*   Plugins should use the root logger from the `logging` module to produce
    debug, info, warning and error messages as appropriate. Messages should
    begin `Plugin plugin_name:`
  
*   Plugins must not write to stdout and should not write to stderr.

*   Plugins must not read from stdin.

*   Plugins are allowed to raise exceptions. These will be caught and reported
    by the main program.

*   Plugins may store information in the filesystem but only in a directory
    named `~/.cfdoc/plugin_name`.

### Bundled Plugins

CFdoc comes with a number of plugins bundled.

Some plugins accept arguments of their own. These are passed to the plugin
using the following command line syntax:

```bash
-d plugin_name.arg=value
```

or 

```bash
--define plugin_name.arg=value
```

#### autogroup

Automatically assign resources without a manually assigned resource group to a
group based on AWS resource types. For example a resource of type
`AWS::S3::Bucket` will be added to the `S3` group.

This plugin has no arguments.

#### awsdoc

Add links to AWS documentation for CloudFormation resources. CFdoc uses either
Google or Duck Duck Go to locate CloudFormation documentation.

The following arguments are accepted:

|Argument|Description|
|-|-|
|search|The search engine to use. Allowed values are `google` (default) or `duckduckgo`.|

#### resdesc

Use Description/GroupDescription resource properties where available. This will
be used to populate the `Description` key for the resource documentation where
no other value has been specified in a `Metadata.CFdoc` key.

This plugin has no arguments.

#### resjson

Extract the resource definition JSON from the CloudFormation template and format
it. A `JSON` key will be added to the documentation object for the resource.

The following arguments are accepted:

|Argument|Description|
|-|-|
|indent|Indent level for the JSON. Must be between 1 and 8 Default 4.|


### The CFdoc Object

Jinja2 rendering templates and plugins both receive an object of the `CFdoc`
class. The following instance attributes are potentially useful:

#### template

The data structure holding the full JSON of the CloudFormation base template.

This attribute cannot be changed by plugins.

#### name

Name of the template, typically derived from the name of the CloudFormation
template file.

#### title

Derived from the main `Description` key in the CloudFormation template.

#### overview

An ordered dictionary of data items extracted from the `CFdoc` key in the main
`Metadata` key for the CloudFormation template. There are a bunch of "standard"
items that are located first, then any other key the template author cares to
add will also be included. With the exception of the special key `Groups`, the
values of these keys must be either a string or a list of strings.

_Ordered_ here means:

1.  Standard keys in a fixed order.

2.  User defined keys in alphabetic order.

This is done so that the generated documentation always presents template
information in a fixed arrangement.

The optional `Groups` key is used to assign resources to resource groups for
documentation purposes. Its value must be a list of dictionaries. Each
dictionary must contain an `Id` and a `Name` key. The former is the group ID and
can be referenced by `Group` keys in the CFdoc entries for resources.  The
`Name` key should be a short display name for the group.  Typically,
documentation rendering templates will present resource groups in the order in
which they are defined in the `Groups` list.

#### parameters

An ordered dictionary of `Parameters` from the CloudFormation template. Keys are
parameter names and the values are ordered dictionaries containing `Type` and
`Description` keys.

The latter is derived from the parameter specification in the CloudFormation
template by combining the parameter `Description` and `ConstraintDescription`
elements.

#### resources

An ordered dictionary containing the documentation items for each resource in
the CloudFormation template. Keys are the resource names as given in the
CloudFormation template. Values are ordered dictionaries of information items
about the resource.

_Ordered_ in this case means:

1.  Type key first.

2.  Standard keys in a fixed order

3.  User defined keys in alphabetic order.

This is done so that the generated documentation always presents resource
information in a fixed arrangement for each resource.

The `Type` item is extracted from the `Type` key in the CloudFormation resource
specification. All other items are extracted from the CFdoc key in the Metadata
for the resource. With the exception of the Group key, the values for the items
in the CFdoc key must be a string or a list of strings. The value of the Group
key must be a string and should consist of one of the group IDs from the
`Groups` key in the main CloudFormation template `Metadata.CFdoc`.

#### resource_groups

An ordered dictionary of resource groups defined in the `Groups` key in the main
template `Metadata.CFdoc`. The order in which the groups were listed in the
`Groups` key is preserved. The value of each item is a dictionary containing a
`Name` key (the group Name) and a `Members` key. The latter is a list of
resource names in the group, sorted by resource name. This is also a key into
the `resources` attribute described above.

In addition to the explicitly specified groups, there may also be a group with a
key of _None_, holding resources not otherwise assigned to a defined group.
Plugins seeking to manipulate the group information must take care to maintain
referential integrity.

Note that some groups may have no members.

#### outputs

An (alphabetically) ordered dictionary of documentation for the `Outputs`
defined in the CloudFormation template. Keys are output names and values are
ordered dictionaries, currently, containing only a `Description` key with a
value derived from the CloudFormation template.

#### plugins

Plugins can also provide additional information in the `plugins` dictionary
attribute. Well behaved plugins will create an entry in the plugins dictionary
with the plugin name as the key. What happens under that is plugin specific.

## Release Notes

#### v2.1.0

*   Packaging changes for PyPI.
