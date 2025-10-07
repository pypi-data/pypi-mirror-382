"""Handler for copy to ECR command."""

from __future__ import annotations

from argparse import Namespace
from copy import deepcopy
from subprocess import run

import boto3

from jindr.docker import DockerObjectRef, DockerRegistryRef, list_images
from jindr.exceptions import JinDrError
from jindr.lib.aws import aws_account_id, ecr_create_repo, ecr_docker_login
from .__common__ import CliCommand

__author__ = 'Murray Andrews'

ECR_KEEP_UNTAGGED_DAYS = 1
ECR_KEEP_VERSIONS = 4

ECR_LIFECYCLE_POLICY_RULES = {
    'prune-untagged': {
        'rulePriority': 1,
        'description': 'Delete untagged images',
        'selection': {
            'tagStatus': 'untagged',
            'countType': 'sinceImagePushed',
            'countUnit': 'days',
            'countNumber': ECR_KEEP_UNTAGGED_DAYS,
        },
        'action': {'type': 'expire'},
    },
    'keep-versions': {
        'rulePriority': 2,
        'description': 'Prune old versions',
        'selection': {
            'tagStatus': 'any',
            'countType': 'imageCountMoreThan',
            'countNumber': '=== REPLACE THIS WITH A NUMBER ===',
        },
        'action': {'type': 'expire'},
    },
}


# ------------------------------------------------------------------------------
@CliCommand.register('cpe', 'copy2ecr')
class Copy2Ecr(CliCommand):
    """Copy an image from the local registry to AWS ECR."""

    # --------------------------------------------------------------------------
    def add_arguments(self) -> None:
        """Add arguments to the command handler."""

        self.argp.add_argument('image', help='Image to copy.')

        self.argp.add_argument(
            '--keep',
            type=int,
            metavar='VERSIONS',
            default=ECR_KEEP_VERSIONS,
            help=(
                'If the ECR repository needs to be created, a lifecycle rule will'
                ' be added that deletes untagged images after one day and prunes'
                ' old versions to the number specified by this option. The default'
                f' is {ECR_KEEP_VERSIONS}.'
            ),
        )
        self.argp.add_argument(
            '--region',
            dest='aws_region',
            nargs='?',
            help=(
                'Target AWS region. If not specified, the default region defined by'
                ' the AWS user profile is used.'
            ),
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
        # Login to ECR and prep the target repo
        aws_session = boto3.Session(region_name=args.aws_region)
        ecr = aws_session.client('ecr')
        ecr_registry = DockerRegistryRef(
            f'{aws_account_id(aws_session)}.dkr.ecr.{aws_session.region_name}.amazonaws.com'
        )

        print('Logging in to AWS ECR ...', flush=True, end='')
        try:
            ecr_docker_login(ecr)
        except Exception:
            print('failed')
        print('done')

        print(f'Checking ECR for repo {ecr_registry} ... ', flush=True, end='')
        lifecycle_rules = deepcopy(ECR_LIFECYCLE_POLICY_RULES)
        lifecycle_rules['keep-versions']['selection']['countNumber'] = args.keep
        try:
            result = ecr_create_repo(
                ecr, base_image.name, exist_ok=True, lifecycle_rules=list(lifecycle_rules.values())
            )
        except Exception:
            print('failed')
            raise
        print(result)

        # ------------------------------
        # OK ... ready to copy
        for src_img in source_images:
            dst_img = DockerObjectRef(registry=ecr_registry, name=src_img.name, tag=src_img.tag)
            print(f'Copying {src_img} -> {dst_img}')
            cmd = ['docker', 'buildx', 'imagetools', 'create', '--tag', str(dst_img), str(src_img)]
            result = run(cmd)
            if result.returncode != 0:
                raise JinDrError(f'Image copy failed with status {result.returncode}')
        return 0
