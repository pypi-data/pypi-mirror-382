# CFdoc - AWS CloudFormation Template Documentation Tool

**CFdoc** automatically generates hyperlinked documentation from
AWS CloudFormation templates.

[![PyPI version](https://img.shields.io/pypi/v/cfdoc)](https://pypi.org/project/cfdoc/?x)
[![Python versions](https://img.shields.io/pypi/pyversions/cfdoc)](https://pypi.org/project/cfdoc/?x)
![PyPI - Format](https://img.shields.io/pypi/format/cfdoc?x)
![PyPI - License](https://img.shields.io/pypi/l/cfdoc?x)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

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
    (with limitations) CloudFormation templates.
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

See the [repo](https://bitbucket.org/murrayandrews/cfdoc/src/master/) for
full details.

Basic usage is available in the man page (see [Installation](#installation) above)
and with:

```bash
cfdoc --help
```
