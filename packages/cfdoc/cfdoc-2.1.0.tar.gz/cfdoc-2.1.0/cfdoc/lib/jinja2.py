"""Jinja2 filters etc."""

from __future__ import annotations

import operator
import re
from collections.abc import Iterable


MD_ESCAPE_CHARS_RE = re.compile(r'([\[\]`])')  # Replace [, ] and `


# ------------------------------------------------------------------------------
def j2_sort_multi_attributes(items: Iterable[str], *attrs):
    """
    Sort by multiple attributes.

    See: https://stackoverflow.com/questions/16143053/stable-sorting-in-jinja2

    Add to Jinja env:

        env = config.get_jinja2_environment()
        env.filters['asort'] = sort_multi_attributes

    Use in template:

        {{item_list|sort_multi('attr1','attr2')}}


    :param items:       The thing to sort.
    :param attrs:       The attributes of the list items on which to sort.
    :return:            A sorted copy of the list.
    """

    itemlist = list(items)
    itemlist.sort(key=operator.attrgetter(*attrs))
    return itemlist


# ------------------------------------------------------------------------------
def j2_md_xref(s: str, style: str, target: str = None) -> str:
    """
    Convert a header text to a markdwon cross reference.

    These used to be more variation in this stuff in the past. e.g. BitBucket
    had this weird #markdown-header-* crap. It's pretty much all a-b-c style
    now. There are some differences in handling non-alpha chars.

    Add to Jinja env:

        env = config.get_jinja2_environment()
        env.filters['xref'] = j2_md_xref

    Use in template:

        {{ header_text | xref('bitbucket', target='Some header') }}

    :param s:           The link text. Also used as the target header if
                        target is None.
    :param style:       Markdown style. Case insensitive. Either BitBucket (or
                        bb), Pandoc (pd) or anything else.
    :param target:      If not None, the target header
    :return:            A link construct [Text](#xref)
    """

    if not target:
        target = s

    style = style.lower()
    if style in ('bitbucket', 'bb'):
        # Not sure about this now
        xref = '-'.join(target.lower().split())
    elif style in ('pandoc', 'pd'):
        xref = '-'.join(re.sub(r'[^\w\s-]+', '', target).lower().split())
    else:
        xref = '-'.join(re.sub(r'[^\w\s:-]+', '', target).lower().split())
    return f'[{s}](#{xref})'


# ------------------------------------------------------------------------------
def j2_re_match(s: str, pattern: str) -> str | None:
    """
    Jinja2 filter to search a string and return the first capture group.

    If no match, returns None. If no capture group and there is a match, then the
    matched component is returned.

    WARNING: The parameters are the opposite way around from re.match() because
    of the way the Jinja2 extension API works.

    Add to Jinja env:

        env = config.get_jinja2_environment()
        env.filters['re_match'] = j2_re_match

    Use in template:

        {{ xxx | re_match(pattern) }}

    Note that re.search() is used so the pattern is not automatically anchored
    to the start of the string.

    :param s:       String to search.
    :param pattern: Regex.

    :return:        The matched component or None.
    """

    m = re.match(pattern, s)
    if not m:
        return None

    return m.group(1 if m.groups() else 0)


# ------------------------------------------------------------------------------
def j2_escape_markdown(s):
    """
    Jinja2 filter to replace Markdown special chars with escaped versions.

    Add to Jinja env:

        env = config.get_jinja2_environment()
        env.filters['e_md'] = j2_escape_markdown

    Use in template:

        {{ xxx | e_md }}


    :param s:       String to escape
    :type s:        str
    :return:        Escaped string
    :rtype:         str
    """

    return MD_ESCAPE_CHARS_RE.sub(r'\\\1', s)
