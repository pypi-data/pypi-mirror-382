"""Handler for copy to ECR command."""

from __future__ import annotations

from argparse import Namespace
from subprocess import run

from jindr.docker import DockerObjectRef, DockerRegistryRef, list_images
from jindr.exceptions import JinDrError
from .__common__ import CliCommand

__author__ = 'Murray Andrews'


# ------------------------------------------------------------------------------
@CliCommand.register('cp', 'copy')
class Copy(CliCommand):
    """Copy an image from the local registry to another docker registry."""

    # --------------------------------------------------------------------------
    def add_arguments(self) -> None:
        """Add arguments to the command handler."""

        self.argp.add_argument('image', help='Image to copy.')
        self.argp.add_argument(
            'dst_registry', metavar='registry', help='Destination docker registry.'
        )

        self.argp.add_argument(
            'tag',
            nargs='*',
            help=(
                'Copy all of the specified image tags for the image in addition to'
                ' whatever is specified in the image argument.'
            ),
        )

    # --------------------------------------------------------------------------
    # noinspection PyBroadException
    @staticmethod
    def execute(args: Namespace) -> int:
        """Execute the command."""

        # ------------------------------
        # Validate source images first
        base_image = DockerObjectRef.from_str(args.image, registry=args.registry, tag='latest')
        source_images = {base_image}
        for tag in args.tag:
            img = DockerObjectRef.from_str(args.image, registry=args.registry)
            img.tag = tag
            source_images.add(img)

        # The tag part of the base image will be ignored and we'll get a list of
        # all tags available in the repo to check the requested tags exist.
        available_images = set(list_images(base_image))
        missing_images = source_images - available_images
        if missing_images:
            raise JinDrError(
                f'Images not found: {", ".join(sorted(str(img) for img in missing_images))}'
            )

        # ------------------------------
        # OK ... ready to copy

        dst_registry = DockerRegistryRef.from_str(args.dst_registry)
        for src_img in source_images:
            dst_img = DockerObjectRef(registry=dst_registry, name=src_img.name, tag=src_img.tag)
            print(f'Copying {src_img} -> {dst_img}')
            cmd = ['docker', 'buildx', 'imagetools', 'create', '--tag', str(dst_img), str(src_img)]
            result = run(cmd)
            if result.returncode != 0:
                raise JinDrError(f'Image copy failed with status {result.returncode}')
        return 0
