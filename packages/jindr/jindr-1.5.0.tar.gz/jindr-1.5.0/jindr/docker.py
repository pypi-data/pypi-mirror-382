"""Docker related utility components."""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache, total_ordering
from typing import Any

import docker
import requests
from docker.models.containers import Container

from jindr.lib.misc import camel_to_snake, is_valid_hostname
from .exceptions import JinDrError, JinDrNotFoundError

__author__ = 'Murray Andrews'


REGISTRY_IMAGE = 'registry'
REGISTRY = 'localhost:5001'
REGISTRY_INTERNAL_PORT = 5000  # This is the internal port in the container
REGISTRY_INTERNAL_DIR = '/var/lib/registry'  # Where image data is stored in the container.
REGISTRY_TIMEOUT = 10

REGISTRY_ENVIRONMENT = {
    'REGISTRY_LOG_LEVEL': 'info',
    'REGISTRY_HTTP_DEBUG_PROMETHEUS_ENABLED': 'false',
    'OTEL_TRACES_EXPORTER': 'none',
    'OTEL_METRICS_EXPORTER': 'none',
    'OTEL_LOGS_EXPORTER': 'console',
}


# ------------------------------------------------------------------------------
@dataclass
class DockerRegistryRef:
    """Container for docker registry reference."""

    host: str
    port: int | None = None

    # --------------------------------------------------------------------------
    def __post_init__(self):
        """Validate host and port."""

        if self.port is not None and not 1 <= self.port <= 65535:
            raise ValueError(f'Port out of range: {self.port}')

        if self.host != 'localhost' and (
            len(self.host.split('.')) < 2 or not is_valid_hostname(self.host)
        ):
            raise ValueError(f'Bad hostname: {self.host}')

    # --------------------------------------------------------------------------
    def __hash__(self):
        """Return hash of host and port."""
        return hash((self.host, self.port))

    # --------------------------------------------------------------------------
    @classmethod
    def from_str(cls, registry: str) -> DockerRegistryRef:
        """Parse a docker registry reference."""

        if ':' in registry:
            host, port_s = registry.lower().rsplit(':', 1)
            try:
                port = int(port_s)
            except ValueError:
                raise ValueError(f'Bad port: {port_s}')
            return cls(host, port)
        return cls(registry)

    # --------------------------------------------------------------------------
    def __str__(self) -> str:
        """Get a string representation of the registry."""

        return f'{self.host}:{self.port}' if self.port else self.host


# ------------------------------------------------------------------------------
@total_ordering
@dataclass(kw_only=True)
class DockerObjectRef:
    """Represents a Docker object reference (repo or image)."""

    registry: DockerRegistryRef = None
    name: str = None
    digest: str = None
    tag: str = None

    # --------------------------------------------------------------------------
    @classmethod
    def from_str(
        cls, ref: str, *, registry: str | DockerRegistryRef = None, tag: str = None
    ) -> DockerObjectRef:
        """
        Parse a Docker object reference.

        :param ref:         The Docker object reference as a string.
        :param registry:    The registry to use if not specified in the ref string.
        :param tag:         The registry to use if not specified in the ref string.
        """

        _registry, _tag, digest = None, None, None

        if '@' in ref:
            ref, digest = ref.split('@', 1)

        # Find last ':' that comes after last '/' to avoid misinterpreting port in registry
        tag_sep = ref.rfind(':')
        slash_sep = ref.rfind('/')
        if tag_sep > slash_sep:
            ref, _tag = ref[:tag_sep], ref[tag_sep + 1 :]

        # Determine registry vs repository
        parts = ref.split('/', 1)
        if '.' in parts[0] or ':' in parts[0] or parts[0] == 'localhost':
            # First part is a registry
            _registry = DockerRegistryRef.from_str(parts[0])
            name = parts[1] if len(parts) > 1 else ''
        else:
            # No registry; entire image is the name
            name = ref

        if not name:
            raise ValueError('Image name is required')

        return cls(
            registry=_registry
            or (
                registry
                if isinstance(registry, DockerRegistryRef)
                else DockerRegistryRef.from_str(registry)
            ),
            name=name,
            tag=(_tag or tag) if digest is None else None,
            digest=digest,
        )

    # --------------------------------------------------------------------------
    def __lt__(self, other: Any) -> bool:
        """Compare two Docker object references based on their string representation."""

        return str(self) < str(other)

    # --------------------------------------------------------------------------
    def __str__(self) -> str:
        """Return string representation."""

        base = f'{self.registry}/{self.name}' if self.registry else self.name
        if self.digest:
            return f'{base}@{self.digest}'
        if self.tag:
            return f'{base}:{self.tag}'
        return base

    # --------------------------------------------------------------------------
    def __hash__(self) -> int:
        """Return hash value of object."""

        return hash((self.registry, self.name, self.digest, self.tag))


# ------------------------------------------------------------------------------
def find_registry_container(registry: DockerRegistryRef, client: docker.DockerClient) -> Container:
    """
    Find the container that is running the specified docker registry.

    The registry must be on localhost, the container must be running and using
    the "registry" image.
    """

    if registry.host != 'localhost':
        raise ValueError(f'Bad host: {registry.host} - must be localhost')

    containers = client.containers.list(
        filters={
            'ancestor': REGISTRY_IMAGE,
            'status': 'running',
            'publish': f'{registry.port or 443}/tcp',
        }
    )

    if not containers:
        raise JinDrError(f'Could not find active container running registry for {registry}')

    # This really should not happen as it would mean 2 containers on one port!
    if len(containers) > 1:
        raise JinDrError(f'Multiple containers running registry for {registry}')

    return containers[0]


# ------------------------------------------------------------------------------
def find_registry_config_file(registry_container: Container) -> str:
    """Find the config file for the specified docker registry."""

    # Check for command line arg that looks like a YAML file
    for item in registry_container.attrs.get('Config', {}).get('Cmd', []):
        if item.endswith(('.yml', '.yaml')):
            return item

    # Check REGISTRY_CONFIGURATION_PATH env var
    for item in registry_container.attrs.get('Config', {}).get('Env', []):
        k, v = item.split('=', 1)
        if k == 'REGISTRY_CONFIGURATION_PATH':
            return v

    # Last resort
    return '/etc/distribution/config.yml'


# ------------------------------------------------------------------------------
def garbage_collect_registry(registry_container: Container) -> str:
    """
    Garbage collect the docker registry.

    :param registry_container: The docker registry container to garbage collect.
    :return:    Info about the result for human consumption.
    """

    config_file = find_registry_config_file(registry_container)
    result = registry_container.exec_run(
        ['bin/registry', 'garbage-collect', config_file, '--delete-untagged']
    )
    if m := re.search('^.*eligible for deletion$', result.output.decode('utf-8'), re.MULTILINE):
        return m.group(0)

    return ''


# ------------------------------------------------------------------------------
class DockerImageInfo:
    """Simple container to hold image info."""

    # --------------------------------------------------------------------------
    @classmethod
    def new(cls, **kwargs) -> DockerImageInfo:
        """Create an ImageInfo from a dict, converting keys to snake-case."""

        return cls(**{camel_to_snake(k): v for k, v in kwargs.items()})

    # --------------------------------------------------------------------------
    @classmethod
    @lru_cache
    def from_registry(cls, image: DockerObjectRef) -> DockerImageInfo:
        """Load image info from registry."""

        if not image.registry:
            raise ValueError('Repository must specify a registry')
        resp = requests.get(
            f'http://{image.registry}/v2/{image.name}/manifests/{image.tag or "latest"}',
            headers={'Accept': 'application/vnd.docker.distribution.manifest.v2+json'},
            timeout=REGISTRY_TIMEOUT,
        )
        if resp.status_code == 404:
            raise JinDrNotFoundError(image)
        resp.raise_for_status()
        return cls.new(
            image=image, content_digest=resp.headers['Docker-Content-Digest'], **resp.json()
        )

    # --------------------------------------------------------------------------
    # noinspection PyUnusedLocal
    def __init__(
        self,
        *,
        image: DockerObjectRef,
        manifests: list[dict] = None,
        content_digest=None,
        **kwargs,
    ) -> None:
        """Create an ImageInfo instance, ignoring uninteresting keys."""

        self.image = image
        self.manifests = manifests or []
        self.content_digest = content_digest

    # --------------------------------------------------------------------------
    @property
    def platforms(self) -> set[str]:
        """Get the platforms for which the image has elements."""

        return {
            '{os}/{architecture}'.format(**m['platform'])
            for m in self.manifests
            if any(v != 'unknown' for v in m['platform'].values())
        }

    # --------------------------------------------------------------------------
    @property
    def image_id(self) -> str:
        """
        Get the image ID.

        WARNING: This is usually but may not be the first 12 chars of the content
                 digest. Close enough for our purposes.
        """

        return self.content_digest.split(':', 1)[1][:12]

    # --------------------------------------------------------------------------
    def __str__(self) -> str:
        """Generate string representation."""

        return f'{self.image} ({self.content_digest}) ({", ".join(sorted(self.platforms))})'


# ------------------------------------------------------------------------------
@lru_cache
def list_repos(registry: DockerRegistryRef) -> list[DockerObjectRef]:
    """List the repositories in the specified registry."""

    resp = requests.get(f'http://{registry}/v2/_catalog', timeout=REGISTRY_TIMEOUT)
    resp.raise_for_status()
    return [
        DockerObjectRef(registry=registry, name=repo)
        for repo in resp.json().get('repositories', [])
    ]


# ------------------------------------------------------------------------------
@lru_cache
def list_images(repo: DockerObjectRef) -> list[DockerObjectRef]:
    """List the images in the specified repo."""

    if not repo.registry:
        raise ValueError('Repository must specify a registry')
    resp = requests.get(
        f'http://{repo.registry}/v2/{repo.name}/tags/list', timeout=REGISTRY_TIMEOUT
    )
    if resp.status_code == 404:
        raise JinDrNotFoundError(repo)
    resp.raise_for_status()
    data = resp.json()

    return [
        DockerObjectRef(registry=repo.registry, name=data['name'], tag=tag)
        for tag in data.get('tags', [])
    ]


# ------------------------------------------------------------------------------
def delete_image(image: DockerObjectRef) -> None:
    """
    Delete the specified image.

    This will just delete the image manifest -- not the blobs. A separate
    garbage collection still needs to happen but is not done here.

    :param image: The image to delete.
    """

    image_info = DockerImageInfo.from_registry(image)
    # Process is to delete the image manifest. This will still leave the blobs
    resp = requests.delete(
        f'http://{image.registry}/v2/{image.name}/manifests/{image_info.content_digest}',
        timeout=REGISTRY_TIMEOUT,
    )
    if resp.status_code == 404:
        raise JinDrNotFoundError(image)
    resp.raise_for_status()
