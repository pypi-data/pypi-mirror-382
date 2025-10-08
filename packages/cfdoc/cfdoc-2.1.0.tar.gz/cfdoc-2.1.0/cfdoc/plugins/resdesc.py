"""
Use Description/GroupDescription/AlarmDescription resource properties where available.

Cfdoc plugin to grab a "Description" or "GroupDescription" tag from a resource
where no other description has been provided in the metadata tag. Only a few
resource types have these Description tags.

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

from cfdoc.lib.misc import mget, paragraphs
from cfdoc.plugins import plugin

__author__ = 'Murray Andrews'

LOG = logging.getLogger()

ALT_DESCRIPTION_KEYS = ('Description', 'GroupDescription', 'AlarmDescription')


# ------------------------------------------------------------------------------
@plugin('resdesc')
def cfd_plugin(cfdoc, **kwargs):
    """
    Grab description tags from the resource properties.

    This desciption is used for those resources where this is available and no
    other description has been provided in the metadata tag.

    :param cfdoc:       A CFdoc object.
    :param kwargs:      Soak up any unrecognised parameters.
    """

    if kwargs:
        LOG.error('Plugin %s: Unexpected arguments ignored: %s', cfd_plugin.name, ', '.join(kwargs))

    # Go through each resource doc entry, look for ones with no description
    # and see if the resource properties can supply one.

    cf_resources = cfdoc.template.get('Resources')

    for rsrc_id in cfdoc.resources:
        rsrc_info = cfdoc.resources[rsrc_id]

        try:
            if not rsrc_info.get('Description'):
                # No description present in metadata tag
                properties = cf_resources[rsrc_id].get('Properties', {})
                rsrc_info['Description'] = paragraphs(mget(properties, ALT_DESCRIPTION_KEYS))
        except ValueError:
            # This can happen if the description uses a CFN intrinsic function
            # which will be a dict at this point.
            pass
