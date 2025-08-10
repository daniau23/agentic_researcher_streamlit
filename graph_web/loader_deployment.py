from shared import ResearchState
from typing import Dict
import logging
import requests
from bs4 import BeautifulSoup

"""
Simple, robust HTML loader using requests + BeautifulSoup.
This avoids Selenium / chromedriver and works reliably on Streamlit Cloud
without system-level browser dependencies.
"""

logger = logging.getLogger(__name__)

# Limit content length to ~100,000 characters (≈ 32,000 tokens max)
MAX_CHARS = 100_000

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
    )
}

def _fetch_text_via_requests(url: str) -> str:
    """Fetch page and extract visible text using BeautifulSoup."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        logger.warning("requests fetch failed for %s: %s", url, e)
        return "No content"

    html = resp.text or ""
    # Prefer lxml parser if available, fallback to default parser
    try:
        soup = BeautifulSoup(html, "lxml")
    except Exception:
        soup = BeautifulSoup(html, "html.parser")

    # Remove script/style/iframe/noscript elements
    for tag in soup(["script", "style", "noscript", "iframe", "header", "footer", "svg"]):
        try:
            tag.decompose()
        except Exception:
            pass

    # Extract visible text
    texts = list(soup.stripped_strings)
    if not texts:
        return "No content"

    # Join with single spaces to avoid huge whitespace
    full_text = " ".join(texts)
    return full_text

def load_node(state: ResearchState) -> Dict[str, str]:
    """
    Load the page content from state.url using requests + BeautifulSoup.
    Returns a dict with the 'content' key.
    """
    if not state.url:
        return {"content": "No URL to load"}

    url = str(state.url)
    try:
        content = _fetch_text_via_requests(url)
    except Exception as e:
        logger.error("Unexpected error fetching %s: %s", url, e)
        content = "No content"

    truncated = content[:MAX_CHARS]
    return {"content": truncated}