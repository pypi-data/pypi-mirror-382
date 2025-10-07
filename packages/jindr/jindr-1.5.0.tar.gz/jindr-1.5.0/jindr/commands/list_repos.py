"""Handler for list repos command."""

from __future__ import annotations

from argparse import Namespace

from jindr.docker import list_repos
from .__common__ import CliCommand

__author__ = 'Murray Andrews'


# ------------------------------------------------------------------------------
@CliCommand.register('ls', 'repos')
class ListRepos(CliCommand):
    """List repositories in the registry."""

    # --------------------------------------------------------------------------
    @staticmethod
    def execute(args: Namespace) -> int:
        """Execute the command."""
        for repo in sorted(list_repos(args.registry)):
            print(repo)
        return 0
