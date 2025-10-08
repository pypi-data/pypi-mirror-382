"""
Add links to AWS documentation for Cloudformation resources.

Since AWS rearranged their doco its much harder to scrape the links so now
we just cheat and use Google or Duck Duck Go.

Lookup the Cloudformation documentation on the AWS website and extract URLs
for documentation. The information is added to the plugins element of the
CFdoc structure. Its up to the rendering template to use it appropriately.

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

import logging
import re

from cfdoc.plugins import plugin

__author__ = 'Murray Andrews'

LOG = logging.getLogger()

AWS_CFDOC_SITE = 'docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide'
AWS_CFDOC_DETAIL = f'https://{AWS_CFDOC_SITE}/aws-resource-{{service}}-{{resource}}.html'

SEARCH_URL = {
    'google': 'https://www.google.com/search?q={query}&btnI=Search&as_sitesearch=' + AWS_CFDOC_SITE,
    'duckduckgo': 'https://duckduckgo.com/?k1=-1&q=!ducky+{query}+site%3A' + AWS_CFDOC_SITE,
}

# Keys in the dict of links extracted from AWS
K_INDEX = 'index'
K_RESOURCES = 'resources'

# Extract interesting bits from a CFN resource type
CFN_RESOURCE_RE = re.compile(r'AWS::(?P<service>\w+)::(?P<resource>\w+)', re.IGNORECASE)

# ------------------------------------------------------------------------------
TIME_UNITS = {
    'w': 60 * 60 * 24 * 7,
    'd': 60 * 60 * 24,
    'h': 60 * 60,
    'm': 60,
    's': 1,
    '': 1,  # Default is seconds
}


# ------------------------------------------------------------------------------
@plugin('awsdoc')
def cfd_plugin(cfdoc, search: str = None, **kwargs):
    """
    Augment cfdoc with links for AWS Cloudformation documentation.

    :param cfdoc:       A CFdoc object.
    :param search:      Search engine to use -- google or duckduckgo
    :param kwargs:      Soak up any unrecognised parameters.

    """

    if kwargs:
        LOG.error('Plugin %s: Unexpected arguments ignored: %s', cfd_plugin.name, ', '.join(kwargs))

    resource_types = {r['Type'] for r in cfdoc.resources.values()}

    if not search:
        links = {}
        for r in resource_types:
            if not (m := CFN_RESOURCE_RE.match(r.lower())):
                raise Exception(f'Bad resource type: {r}')
            links[r] = AWS_CFDOC_DETAIL.format(**m.groupdict())

        cfdoc.plugins[cfd_plugin.name] = {
            'index': f'https://{AWS_CFDOC_SITE}',
            'resources': links,
        }
        return

    # Need to try using search engines.
    try:
        search_url = SEARCH_URL[search]
    except KeyError:
        raise Exception(
            f'Unknown search engine {search}. Choose one of {", ".join(sorted(SEARCH_URL))}.'
        )

    cfdoc.plugins[cfd_plugin.name] = {
        'index': 'https://' + AWS_CFDOC_SITE,
        'resources': {r: search_url.format(query=r) for r in resource_types},
    }
