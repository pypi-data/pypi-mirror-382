"""Handler for registry stop command."""

from __future__ import annotations

from argparse import Namespace

import docker

from jindr.docker import find_registry_container, garbage_collect_registry
from .__common__ import CliCommand

__author__ = 'Murray Andrews'


# ------------------------------------------------------------------------------
@CliCommand.register('stop', 'down')
class Stop(CliCommand):
    """Stop the registry container."""

    # --------------------------------------------------------------------------
    def add_arguments(self) -> None:
        """Add arguments to the command handler."""

        self.argp.add_argument(
            '-G',
            '--no-gc',
            dest='gc',
            action='store_false',
            help='Do not garbage collect on exit.',
        )

    # --------------------------------------------------------------------------
    @staticmethod
    def execute(args: Namespace) -> int:
        """Execute the command."""

        client = docker.from_env()

        print(f'Looking for registry container for {args.registry} ... ', end='', flush=True)
        try:
            registry_container = find_registry_container(args.registry, client)
        except Exception:
            print('failed')
            raise
        print(f'found "{registry_container.name}"')

        if args.gc:
            try:
                print(garbage_collect_registry(registry_container))
            except Exception as e:
                # Even if garbage collection failed, we want to still stop the container.
                print(f'Garbage collection failed: {e}')

        print(f'Stopping "{registry_container.name}" ... ', end='', flush=True)
        try:
            registry_container.stop()
        except Exception:
            print('failed')
            raise ()
        print('done')

        return 0
