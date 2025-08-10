from langchain_community.document_loaders import SeleniumURLLoader
from shared import ResearchState

# Limit content length to ~100,000 characters (≈ 32,000 tokens max)
MAX_CHARS = 100_000

def load_node(state: ResearchState) -> dict:
    if not state.url:
        return {"content": "No URL to load"}

    loader = SeleniumURLLoader(urls=[str(state.url)])
    docs = loader.load()

    content = docs[0].page_content if docs else "No content"

    # Truncate early to prevent overload later
    truncated_content = content[:MAX_CHARS]
    return {"content": truncated_content}