#!/usr/bin/env python3

"""Simple CLI to interact with a local docker registry."""

from __future__ import annotations

import sys
from argparse import ArgumentParser, Namespace
from importlib import resources

from jindr.commands import CliCommand
from jindr.docker import DockerRegistryRef, REGISTRY
from jindr.exceptions import JinDrInternalError
from jindr.version import __version__

__author__ = 'Murray Andrews'

PROG = resources.files('jindr').name


# ------------------------------------------------------------------------------
def process_cli_args() -> Namespace:
    """
    Process the command line arguments.

    :return:    The args namespace.
    """

    argp = ArgumentParser(prog=PROG, description='Interact with a local docker registry.')
    argp.add_argument('-v', '--version', action='version', version=__version__)

    argp.add_argument(
        '-r',
        '--registry',
        action='store',
        default=REGISTRY,
        help=f'The source registry to use. Default is {REGISTRY}.',
    )

    # ----------------------------------------
    # Add the sub-commonads
    subp = argp.add_subparsers(required=True)
    for cmd in sorted(CliCommand.commands.values(), key=lambda c: c.name):
        cmd(subp).add_arguments()

    args = argp.parse_args()
    args.registry = DockerRegistryRef.from_str(args.registry)  # noqa

    if not hasattr(args, 'handler'):
        raise JinDrInternalError('Args namespace missing handler entry')

    try:
        args.handler.check_arguments(args)
    except ValueError as e:
        argp.error(str(e))

    return args


# ------------------------------------------------------------------------------
def main() -> int:
    """Show time."""
    try:
        args = process_cli_args()
        args.handler.execute(args)
        return 0
    except Exception as e:
        # Uncomment for debugging
        # raise  # noqa: ERA001
        print(f'{PROG}: {e}', file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print(f'{PROG}: Interrupt', file=sys.stderr)
        return 2


# ------------------------------------------------------------------------------
# This only gets used during dev/test. Once deployed as a package, main() gets
# imported and run directly.
if __name__ == '__main__':
    exit(main())
