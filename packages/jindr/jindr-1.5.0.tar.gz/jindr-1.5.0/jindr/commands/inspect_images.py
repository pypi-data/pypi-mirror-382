"""Handler for inspect images command."""

from __future__ import annotations

from argparse import Namespace

from tabulate import tabulate

from jindr.docker import DockerImageInfo, DockerObjectRef
from .__common__ import CliCommand

__author__ = 'Murray Andrews'


# ------------------------------------------------------------------------------
@CliCommand.register('ins', 'inspect')
class InspectImages(CliCommand):
    """Inspect specified images."""

    # --------------------------------------------------------------------------
    def add_arguments(self) -> None:
        """Add arguments to the command handler."""

        self.argp.add_argument('image', nargs='+', help='Images to inspect.')

    # --------------------------------------------------------------------------
    @staticmethod
    def execute(args: Namespace) -> int:
        """Execute the command."""

        table_data = []
        for img_name in args.image:
            image = DockerObjectRef.from_str(img_name, registry=args.registry, tag='latest')
            image_info = DockerImageInfo.from_registry(image)
            table_data.append(
                [f'{image.registry}/{image.name}', image.tag, None, image_info.content_digest]
            )

            for mf in image_info.manifests:
                # Skip non platform manifests (usually annotations)
                if all(v == 'unknown' for v in mf['platform'].values()):
                    continue
                table_data.append(
                    [None, None, '{os}/{architecture}'.format(**mf['platform']), mf['digest']]
                )

        if table_data:
            print()
            print(tabulate(table_data, headers=('IMAGE', 'TAG', 'PLATFORM', 'DIGEST')))
            print()

        return 0
