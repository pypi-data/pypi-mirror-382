"""
Automatically assign resources to resource groups based on AWS resource types.

Cfdoc plugin to automatically categorise Cloudformation resources where a
resource group has not been manually assigned. The group is taken from the
reource type. So a resource type of `AWS::EC2::*` will yield a group of EC2.

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

from cfdoc.plugins import plugin

__author__ = 'Murray Andrews'

LOG = logging.getLogger()


# ------------------------------------------------------------------------------
@plugin('autogroup')
def cfd_plugin(cfdoc, **kwargs):
    """
    Automatically group resources that have not been manually categorised.

    :param cfdoc:   A CFdoc object.
    :param kwargs:  Soak up any unrecognised parameters.

    """

    if kwargs:
        LOG.error('Plugin %s: Unexpected arguments ignored: %s', cfd_plugin.name, ', '.join(kwargs))

    # Go through the None resource group and try to get a resource group for
    # each entry.

    try:
        ungrouped_resources = cfdoc.resource_groups[None]['Members']
    except KeyError:
        # No ungrouped resources - nothing to do.
        return

    remaining_ungrouped = []
    for rsrc_id in ungrouped_resources:
        rsrc_info = cfdoc.resources[rsrc_id]

        try:
            _, rsrc_group, _ = rsrc_info['Type'].split('::')
        except (KeyError, ValueError):
            # No resource type or resource type is not a recognised format.
            # Cloudformation template malformed. This should be handled by the
            # main program, so ignore and move on.
            remaining_ungrouped.append(rsrc_id)
            continue

        rsrc_info['Group'] = rsrc_group
        if rsrc_group not in cfdoc.resource_groups:
            LOG.info('%s: Resource %s: adding new resource group %s', __name__, rsrc_id, rsrc_group)
            cfdoc.resource_groups[rsrc_group] = {'Name': rsrc_group + ' Resources', 'Members': []}

        cfdoc.resource_groups[rsrc_group]['Members'].append(rsrc_id)

    # Update the None resource group with a list of any remaining unallocated resources
    if remaining_ungrouped:
        cfdoc.resource_groups[None]['Members'] = remaining_ungrouped
    else:
        # Nothing left to group.
        del cfdoc.resource_groups[None]
