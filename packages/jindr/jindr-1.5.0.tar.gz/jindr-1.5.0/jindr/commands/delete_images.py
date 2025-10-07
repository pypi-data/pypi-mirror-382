"""Handler for delete images command."""

from __future__ import annotations

from argparse import Namespace

from jindr.docker import DockerObjectRef, delete_image
from .__common__ import CliCommand

__author__ = 'Murray Andrews'


# ------------------------------------------------------------------------------
@CliCommand.register('rmi', 'delimage')
class DelImages(CliCommand):
    """Delete specified images."""

    # --------------------------------------------------------------------------
    def add_arguments(self) -> None:
        """Add arguments to the command handler."""

        self.argp.add_argument('image', nargs='+', help='Images to delete.')

    # --------------------------------------------------------------------------
    @staticmethod
    def execute(args: Namespace) -> int:
        """Execute the command."""

        deleted = set()
        for img_name in args.image:
            image = DockerObjectRef.from_str(img_name, registry=args.registry, tag='latest')
            print(f'{image} ... ', end='', flush=True)
            if (image.registry, image.name, image.digest) in deleted:
                print('already gone')
            else:
                delete_image(image)
                print('deleted')
                deleted.add((image.registry, image.name, image.digest))
        return 0
