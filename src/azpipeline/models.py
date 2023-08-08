__copyright__ = """
@copyright (c) 2023 by Nidhal Baccouri. All rights reserved.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class PipelineSummary:
    name: Any
    build_id: Any
    result: Any
    status: Any
    url: Any
    branch: Any
    commit_id: Any
    triggered_by: Any
