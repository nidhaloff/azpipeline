
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