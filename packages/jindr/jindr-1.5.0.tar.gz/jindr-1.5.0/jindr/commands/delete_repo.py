"""Handler for delete images command."""

from __future__ import annotations

from argparse import Namespace

from jindr.docker import DockerObjectRef, delete_image, list_images
from .__common__ import CliCommand

__author__ = 'Murray Andrews'


# ------------------------------------------------------------------------------
@CliCommand.register('rmr', 'delrepo')
class DelRepos(CliCommand):
    """Delete all images in the specified repositories."""

    # --------------------------------------------------------------------------
    def add_arguments(self) -> None:
        """Add arguments to the command handler."""

        self.argp.add_argument('repo', nargs='+', help='Repos from which to delete all images.')

    # --------------------------------------------------------------------------
    @staticmethod
    def execute(args: Namespace) -> int:
        """Execute the command."""

        deleted = set()
        for r in args.repo:
            repo = DockerObjectRef.from_str(r, registry=args.registry)
            images = list_images(repo)
            for image in images:
                print(f'{image} ... ', end='', flush=True)
                if (image.registry, image.name, image.digest) in deleted:
                    print('already gone')
                else:
                    delete_image(image)
                    print('deleted')
                    deleted.add((image.registry, image.name, image.digest))
        return 0
