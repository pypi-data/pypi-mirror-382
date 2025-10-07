"""Handler for list images command."""

from __future__ import annotations

from argparse import Namespace

from tabulate import tabulate

from jindr.docker import DockerImageInfo, DockerObjectRef, list_images, list_repos
from .__common__ import CliCommand

__author__ = 'Murray Andrews'


# ------------------------------------------------------------------------------
@CliCommand.register('lsi', 'images')
class ListImages(CliCommand):
    """List images in the specified repos."""

    # --------------------------------------------------------------------------
    def add_arguments(self) -> None:
        """Add arguments to the command handler."""

        self.argp.add_argument(
            'repos',
            metavar='REPO',
            nargs='*',
            help='The repos to list. If not specified, all repos are listed.',
        )

    # --------------------------------------------------------------------------
    @staticmethod
    def execute(args: Namespace) -> int:
        """Execute the command."""

        repos = (
            [DockerObjectRef.from_str(repo, registry=args.registry) for repo in args.repos]
            if args.repos
            else list_repos(args.registry)
        )

        table_data = []
        for repo in repos:
            for image in list_images(repo):
                info = DockerImageInfo.from_registry(image)
                table_data.append(
                    [
                        f'{image.registry}/{image.name}',
                        image.tag,
                        info.image_id,
                        ', '.join(sorted(info.platforms)),
                    ]
                )
        if table_data:
            print()
            print(tabulate(table_data, headers=('REPOSITORY', 'TAG', 'IMAGE ID', 'PLATFORMS')))
            print()
        return 0
