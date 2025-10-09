######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.18.10.1+obcheckpoint(0.2.8);ob(v1)                                                   #
# Generated on 2025-10-09T09:15:42.159657                                                            #
######################################################################################################

from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    import os


def get_repository_info(path: typing.Union[str, os.PathLike]) -> typing.Dict[str, typing.Union[str, bool]]:
    """
    Get git repository information for a path
    
    Returns:
        dict: Dictionary containing:
            repo_url: Repository URL (converted to HTTPS if from SSH)
            branch_name: Current branch name
            commit_sha: Current commit SHA
            has_uncommitted_changes: Boolean indicating if there are uncommitted changes
    """
    ...

