"""Handler for registry restart command."""

from __future__ import annotations

from argparse import Namespace

import docker

from jindr.docker import find_registry_container
from .__common__ import CliCommand

__author__ = 'Murray Andrews'


# ------------------------------------------------------------------------------
@CliCommand.register('restart')
class Restart(CliCommand):
    """Restart the registry container."""

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
        print(f'Restarting "{registry_container.name}" ... ', end='', flush=True)
        try:
            registry_container.restart()
        except Exception:
            print('failed')
            raise ()
        print('done')

        return 0
