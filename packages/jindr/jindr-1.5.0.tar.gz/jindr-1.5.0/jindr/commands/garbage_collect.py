"""Handler for gabage collect command."""

from __future__ import annotations

from argparse import Namespace

import docker

from jindr.docker import find_registry_container, garbage_collect_registry
from .__common__ import CliCommand

__author__ = 'Murray Andrews'


# ------------------------------------------------------------------------------
@CliCommand.register('gc')
class GarbageCollect(CliCommand):
    """Garbage collect and restart the registry container."""

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

        print(garbage_collect_registry(registry_container))
        # It's a good idea to restart the container at this point
        print('Restarting registry container ... ', end='', flush=True)
        registry_container.restart()
        print('done')

        return 0
