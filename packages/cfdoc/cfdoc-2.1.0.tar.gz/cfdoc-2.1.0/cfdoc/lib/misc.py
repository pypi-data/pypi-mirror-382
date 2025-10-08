"""Miscellaneous utilities."""

from __future__ import annotations

import importlib
from collections.abc import Hashable, Sequence
from typing import Any


# ------------------------------------------------------------------------------
def import_by_name(name: str, parent: str = None):
    """
    Import a named module from within the named parent.

    :param name:            The name of the sender module.
    :param parent:          Name of parent module. Default None.

    :return:                The sender module.

    :raise ImportError:     If the import fails.
    """

    if parent:
        name = parent + '.' + name

    return importlib.import_module(name)


# ------------------------------------------------------------------------------
def mget(d: dict, keys: Sequence[Hashable], default: Any = None) -> Any:
    """
    Find first non-None value in a dictionary.

    :param d:           A dict.
    :param keys:        An iterable containing possible keys for dict d.
    :param default:     Value to return if none of the keys are present.
                        Default None.

    :return:            The value for the first avaiable key or the default.
    """

    for k in keys:
        v = d.get(k)
        if v is not None:
            return v

    return default


def paragraphs(s: str | list[str]) -> list[str]:
    """
    Convert a string or list of strings into a list of paragraphs.

    An empty string denotes start of a new paragraph.

    :param s:       A string or list of strings. If None, treat it as an empty
                    paragraph.
    :return:        A list of paragraph strings.
    """

    if not s:
        return []

    if isinstance(s, str):
        s = [s]
    elif not isinstance(s, list):
        raise ValueError(f'Expected list of strings, got {type(s)}')

    para_list = []
    para = []

    for line in s:
        if not isinstance(line, str):
            raise TypeError(f'Expected a string, got {type(line)}: {line}')
        line = line.strip()
        if line:
            para.append(line)
        elif para:
            # Start a new paragraph
            para_list.append(' '.join(para))
            para = []

    if para:
        para_list.append(' '.join(para))

    return para_list
