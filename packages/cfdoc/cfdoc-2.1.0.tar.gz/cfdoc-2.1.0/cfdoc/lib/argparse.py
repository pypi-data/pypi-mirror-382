"""Argparse utilties."""

from __future__ import annotations

import argparse


# ------------------------------------------------------------------------------
class StoreNameValuePair(argparse.Action):
    """
    Store argparse values from options of the form `--option name=value`.

    The destination (self.dest) will be created as a dict {name: value}. This
    allows multiple name-value pairs to be set for the same option.

    Usage is:

        argparser.add_argument('-x', metavar='key=value', action=StoreNameValuePair)

    """

    # --------------------------------------------------------------------------
    def __call__(self, parser, namespace, values, option_string=None):
        """Process a name=value argument."""
        try:
            n, v = values.split('=')
        except ValueError:
            raise argparse.ArgumentError(self, 'Argument must be key=value')
        if not hasattr(namespace, self.dest) or not getattr(namespace, self.dest):
            setattr(namespace, self.dest, {})
        getattr(namespace, self.dest)[n] = v
