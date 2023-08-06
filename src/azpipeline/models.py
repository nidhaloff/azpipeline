__copyright__ = """
@copyright (c) 2023 by Nidhal Baccouri. All rights reserved.
"""

from dataclasses import dataclass


@dataclass
class PipelineSummary:
    name: str
    build_id: int
    result: str
    status: str
    url: str
    branch: str
    commit_id: str
    triggered_by: str
