from shared import ResearchState
from pydantic import ValidationError

DEFAULT_URL = "https://www.mdpi.com/2076-3417/11/20/9772"

def search_node(state: ResearchState) -> dict:
    if state.url:
        return {"url": str(state.url)}

    user_input = input(f"Enter URL to summarize [default: {DEFAULT_URL}]: ").strip()
    url_input = user_input if user_input else DEFAULT_URL

    try:
        validated = ResearchState(url=url_input)
    except ValidationError as e:
        raise ValueError(f"Invalid URL: {e}")

    return {"url": str(validated.url)}