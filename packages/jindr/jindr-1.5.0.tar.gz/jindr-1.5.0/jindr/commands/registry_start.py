"""Handler for registry start command."""

from __future__ import annotations

from argparse import Namespace
from pathlib import Path

import docker

from jindr.docker import (
    JinDrError,
    REGISTRY_ENVIRONMENT,
    REGISTRY_IMAGE,
    REGISTRY_INTERNAL_DIR,
    REGISTRY_INTERNAL_PORT,
    find_registry_container,
)
from .__common__ import CliCommand

__author__ = 'Murray Andrews'


STORAGE_AREA_DEFAULT = '~/.jindr'


# ------------------------------------------------------------------------------
@CliCommand.register('start', 'up')
class Start(CliCommand):
    """Start a registry container."""

    # --------------------------------------------------------------------------
    def add_arguments(self) -> None:
        """Add arguments to the command handler."""

        self.argp.add_argument(
            '-d',
            '--data',
            metavar='DIRECTORY',
            default=STORAGE_AREA_DEFAULT,
            help=(
                'Use the specified directory as persistent storage for the registry.'
                f' Will be created if it does not exist. Defaults to {STORAGE_AREA_DEFAULT}.'
            ),
        )

        self.argp.add_argument(
            '-n',
            '--name',
            help='Container name. If not specified, a random name is generated.',
        )

    # --------------------------------------------------------------------------
    @staticmethod
    def execute(args: Namespace) -> int:
        """Execute the command."""

        if args.registry.host not in ('localhost', '127.0.0.1'):
            raise JinDrError('Can only start a registry container on localhost')

        client = docker.from_env()

        # noinspection PyBroadException
        try:
            registry_container = find_registry_container(args.registry, client)
        except Exception:
            pass
        else:
            print(
                f'A registry container for {args.registry} is already running as'
                f' "{registry_container.name}"'
            )
            return 0

        data_path = Path(args.data or STORAGE_AREA_DEFAULT).expanduser()
        data_path.mkdir(exist_ok=True, parents=True)

        run_args = {
            'image': REGISTRY_IMAGE,
            **({'name': args.name} if args.name else {}),
            'environment': REGISTRY_ENVIRONMENT,
            'remove': True,
            'detach': True,
            'ports': {f'{REGISTRY_INTERNAL_PORT}/tcp': ('127.0.0.1', args.registry.port or 443)},
            'volumes': {str(data_path.absolute()): {'bind': REGISTRY_INTERNAL_DIR, 'mode': 'rw'}},
        }

        print(f'Starting registry container for {args.registry} ... ', end='', flush=True)
        container = client.containers.run(**run_args)
        print(f'{container.name} started')

        return 0
