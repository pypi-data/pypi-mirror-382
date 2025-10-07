"""AWS related utilities."""

from __future__ import annotations

import json
from base64 import b64decode
from functools import lru_cache
from subprocess import run
from typing import Any

import boto3
from botocore.exceptions import ClientError

__author__ = 'Murray Andrews'


# ------------------------------------------------------------------------------
@lru_cache(maxsize=1)
def aws_caller_identity(aws_session: boto3.Session = None) -> dict[str, Any]:
    """Get the AWS caller identity."""
    return (aws_session or boto3.Session()).client('sts').get_caller_identity()


# ------------------------------------------------------------------------------
def aws_account_id(aws_session: boto3.Session = None) -> str:
    """Get the AWS account ID."""
    return aws_caller_identity(aws_session)['Account']


# ------------------------------------------------------------------------------
def ecr_create_repo(
    ecr_client, repo_name: str, exist_ok: bool = False, lifecycle_rules: list[dict] = None
) -> str:
    """
    Create an ECR repository.

    :param ecr_client:  A boto3 ECR client.
    :param repo_name:   The name of the repository.
    :param exist_ok:    If True, it's ok if the registry already exists.
    :param lifecycle_rules:  If specified, and if the repo needs to be created,
                        add the specified lifecycle rules to the repository. Note
                        that this is a list of rules -- not the lifecycle policy
                        itself.

    :return:            "created" if the repository was created successfully,
                        "exists" if it already exists.
    :raises Exception:  If the repository already exists and exist_ok is False.
    """

    try:
        ecr_client.describe_repositories(repositoryNames=[repo_name])
        if exist_ok:
            return 'exists'
        raise Exception(f'ECR repository {repo_name} already exists')
    except ClientError as e:
        if e.response['Error']['Code'] == 'RepositoryNotFoundException':
            ecr_client.create_repository(repositoryName=repo_name)
            if lifecycle_rules:
                ecr_client.put_lifecycle_policy(
                    repositoryName=repo_name,
                    lifecyclePolicyText=json.dumps({'rules': lifecycle_rules}),
                )
            return 'created'
        raise


# ------------------------------------------------------------------------------
def ecr_docker_login(ecr_client) -> None:
    """Login to ECR."""

    auth = ecr_client.get_authorization_token()['authorizationData'][0]
    user, passwd = b64decode(auth['authorizationToken']).split(b':', 1)
    result = run(
        ['docker', 'login', '-u', user, '--password-stdin', auth['proxyEndpoint']],
        input=passwd,
    )
    if result.returncode != 0:
        raise Exception(f'ECR login failed: {result.stderr}')
