from dataclasses import dataclass
from datetime import datetime


@dataclass
class Project:
    id: str
    name: str
    description: str
    status: str
    owner_id: str
    path: str
    repo_url: str | None
    created_at: datetime
    updated_at: datetime
