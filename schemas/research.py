from pydantic import BaseModel
from typing import Optional


class ResearchRequest(BaseModel):
    topic: str
    depth: Optional[str] = "medium"  # "quick", "medium", "deep"


class Source(BaseModel):
    title: str
    url: str
    summary: str


class ResearchReport(BaseModel):
    topic: str
    summary: str
    key_findings: list[str]
    sources: list[Source]
    depth_used: str
    total_sources_found: int
