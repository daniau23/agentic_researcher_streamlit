from pydantic import BaseModel, HttpUrl
from typing import Optional

class ResearchState(BaseModel):
    # For article graph
    input: Optional[str] = None
    category: Optional[str] = None
    abstract: Optional[str] = None
    critique: Optional[str] = None
    final_abstract: Optional[str] = None

    # For web summarizer graph
    url: Optional[HttpUrl] = None
    content: Optional[str] = None
    summary: Optional[str] = None