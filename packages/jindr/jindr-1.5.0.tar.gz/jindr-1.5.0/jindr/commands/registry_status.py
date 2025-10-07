"""Handler for registry stop command."""

from __future__ import annotations

from argparse import Namespace

import docker

from jindr.docker import find_registry_container
from .__common__ import CliCommand

__author__ = 'Murray Andrews'


# ------------------------------------------------------------------------------
@CliCommand.register('stat', 'status')
class Status(CliCommand):
    """Get status of the registry container (exit status 0 if running, 1 otherwise)."""

    # --------------------------------------------------------------------------
    @staticmethod
    def execute(args: Namespace) -> int:
        """Execute the command."""

        client = docker.from_env()

        print(f'Looking for registry container for {args.registry} ... ', end='', flush=True)
        # noinspection PyBroadException
        try:
            registry_container = find_registry_container(args.registry, client)
        except Exception:
            print('not running')
            return 1
        print(f'running as "{registry_container.name}"')
        return 0
