"""Handler for registry ps command."""

from __future__ import annotations

from argparse import Namespace
from contextlib import suppress

import docker
from tabulate import tabulate

from jindr.docker import REGISTRY_INTERNAL_DIR, REGISTRY_INTERNAL_PORT
from jindr.lib.misc import get_dirsize
from .__common__ import CliCommand

__author__ = 'Murray Andrews'


# ------------------------------------------------------------------------------
@CliCommand.register('info', 'ps')
class RegistryInfo(CliCommand):
    """List registry containers and show their configuration."""

    # --------------------------------------------------------------------------
    @staticmethod
    def execute(args: Namespace) -> int:
        """Execute the command."""

        client = docker.from_env()

        registry_containers = client.containers.list(
            filters={'ancestor': 'registry', 'expose': REGISTRY_INTERNAL_PORT}
        )
        if not registry_containers:
            return 0

        table_data = []
        for container in registry_containers:
            port = container.ports[f'{REGISTRY_INTERNAL_PORT}/tcp'][0]['HostPort']
            mount, size = None, None
            for mount in container.attrs['Mounts']:
                if mount['Destination'] == REGISTRY_INTERNAL_DIR:
                    mount = mount['Source']
                    # Try to get storage area size but don't worry if we can't
                    with suppress(Exception):
                        size = get_dirsize(mount)
            table_data.append((f'localhost:{port}', container.name, container.status, mount, size))

        print()
        print(
            tabulate(
                table_data, headers=('REGISTRY', 'CONTAINER', 'STATUS', 'STORAGE AREA', 'SIZE')
            )
        )
        print()

        return 0
