# CFdoc(1) -- Extract documentation from an AWS CloudFormation Template

## SYNOPSIS

`cfdoc` \[options\] \[<template>\]

## DESCRIPTION

AWS CloudFormation templates are not easy to read at the best of times and the
inability to properly describe them with embedded documentation makes them
difficult to analyse and maintain.

**CFdoc** exploits the ability to embed <Metadata> keys containing whatever you
want into the CloudFormation JSON/YAML. <Metadata> keys can be placed in:

* the top level of the CloudFormation template
* within each resource specification in the template.

**CFdoc** uses decriptive information placed in <CFdoc> keys within the
<Metadata>, together with other information derived from the template to
automatically generate documentation.

Even where no special information has been embedded in the CloudFormation
template, **CFdoc** can generate basic documentation for the template that can
be easier to comprehend than the template itself.

## OPTIONS

*   <template>:
    File name of the CloudFormation template. If not specified, read from
    <stdin>.
  
*   `-h`, `--help`:
    Show help message and exit.

*   `-c`, `--no-colour`, `--no-color`:
    Don't use colour in information messages.

*   `-d` _plugin.param=value_, `--define` _plugin.param=value_:
    Define parameters for plugins. See [PLUGINS] below for more information.
  
*   `-f` <FORMAT>, `--format` <FORMAT>:
    Output format. Must correspond to a **Jinja2** template named
    _FORMAT.jinja2_.  See [DOCUMENT TEMPLATES] below.
   
*   `-l` <LEVEL>, `--level` <LEVEL>:
    Print messages of a given severity level or above. The standard
    logging level names are available but <info>, <warning> and <error>
    are most useful. The Default is <warning>.

*   `--list-plugins`: 
    List available plugins and exit.

*   `-n` <NAME>, `--name` <NAME>:
    CloudFormation template name (not file name). This may be used in
    the generated output document, depending on the output template.
    If not specified, the name of the input file is used.

*   `-v`, `--version`:
    Show version and exit.

*   `-y`, `--yaml`:
    The CloudFormation template is in YAML format. This is required when the
    format cannot be guessed from the file suffix. JSON format is assumed by
    default. See [LIMITATIONS] below.
  
## DOCUMENT TEMPLATES

**CFdoc** uses [Jinja2](http://jinja.pocoo.org) templates to render the
documentation. 

The template is selected using the `-f`, `--format` option. For a format <xxx>,
**CFdoc** will look for a file _xxx.jinja2_ in a fixed set of locations, unless
the <CFDOCPATH> environment variable specifies an alternative search path. See
[ENVIRONMENT] below.

The following templates are provided:

*   `html`:
    HTML format. This is the default if no format is specified.
    
*   `md`:
    Markdown format using standard conventions for cross-references within the
    file.
    
*   `mdbb`:
    Markdown format using [BitBucket](https://bitbucket.org) conventions for
    cross-references within the file.

*   `mdpd`:
    Markdown format using [Pandoc](http://pandoc.org) conventions for
    cross-references within the file.

## ENVIRONMENT

By default, *CFdoc* will search for templates in the following locations, unless
the <CFDOCPATH> environment variable specifies an alternative search path:

*   current directory
*   <templates> directory in the current directory
*   templates directory included in the **cfdoc** distribution.

This is equivalent to a <CFDOCPATH> setting of:

_:templates:/usr/local/lib/cfdoc/templates_
  
## PLUGINS

**CFdoc** supports plugins to manipulate and extend the extracted documentation.

Some plugins accept arguments of their own. These are passed to the plugin
using `-d`, `--define` command line options.

The following plugins are included with the distribution.

### autogroup

Automatically assign resources that don't have a manually assigned resource
group to a group based on AWS resource types. For example, a resource of type
_AWS::S3::Bucket_ will be added to the _S3_ group.

This plugin has no arguments.

### awsdoc

Add links to AWS documentation for CloudFormation resources.

By default, **CFdoc** will attempt to point directly to AWS CloudFormation
documentation by dead-reckoning. If this is producing useless links (e.g. because
AWS has changed the URL yet again), use the `search` option to generate indirect
links via either Google of Duck Duck Go for locating documentation.

The following arguments are accepted:
    
*   `search`:
    The search engine to use. Allowed values are `google` or `duckduckgo`.

### resdesc

Use <Description>/<GroupDescription> CloudFormation resource properties where
available. This will be used to populate the <Description> key for the resource
documentation where no other value has been specified in a _Metadata.CFdoc_ key.

This plugin has no arguments.

### resjson

Extract the resource definition from the CloudFormation template and format
it as JSON (even if the source template was YAML).

The following arguments are accepted:

*   `indent`:
    Indent level for the JSON. Must be between 1 and 8 Default 4.

## FILES

Plugins may store information in the filesystem in a directory named
_~/.cfdoc/plugin_.

## LIMITATIONS

Support for YAML formatted CloudFormation templates is limited. The
`!` prefixed short-form syntax is not currently supported.

## MORE INFORMATION

Details on how to embed **CFdoc** metadata in a CloudFormation template
can be found here.
[](https://bitbucket.org/murrayandrews/cfdoc)
    

## AUTHOR

Murray Andrews

## LICENCE

[BSD 3-clause licence](http://opensource.org/licenses/BSD-3-Clause).
