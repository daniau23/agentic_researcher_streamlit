# graph_web/loader.py
"""
HTML loader that extracts content by prioritizing headings, sections,
ordered/unordered lists (ol/ul/li), and div blocks using BeautifulSoup.

This avoids Selenium. Works reliably on Streamlit Cloud / HF Spaces.
"""

from shared import ResearchState
from typing import Dict, Iterable
import logging
import requests
from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)

# Limit content length to ~100,000 characters (≈ 32,000 tokens max)
MAX_CHARS = 100_000

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
    )
}

# Tags we care about, in preferred order when searching the page
PRIORITY_TAGS = [
    "h1", "h2", "h3", "h4", "h5", "h6",
    "section",
    "ol", "ul",  # we'll extract their li children
    "div",
]


def _safe_get_text(elem: Tag) -> str:
    """Return cleaned text for a BeautifulSoup Tag."""
    # separator ensures lists / nested blocks are spaced
    return elem.get_text(separator=" ", strip=True)


def _iter_priority_blocks(soup: BeautifulSoup) -> Iterable[Tag]:
    """
    Yield tag elements from the document in DOM order but filtered to our
    priority tags. We skip elements that are likely to be navigation, footer, ads.
    """
    # Remove obviously irrelevant elements first
    for bad in soup(["script", "style", "noscript", "iframe", "svg", "picture", "meta", "link"]):
        try:
            bad.decompose()
        except Exception:
            pass

    # Also remove site chrome elements that commonly contain duplicated text
    for chrome in soup.find_all(["header", "footer", "nav", "aside", "form"]):
        try:
            chrome.decompose()
        except Exception:
            pass

    # Walk the document and yield only the priority tags in DOM order
    for tag in soup.find_all(PRIORITY_TAGS):
        # Skip empty tags
        txt = _safe_get_text(tag)
        if not txt:
            continue
        # Skip tiny fragments that are unlikely to be meaningful
        if len(txt) < 30:
            # but keep headings even if short (they can be meaningful)
            if tag.name not in {"h1", "h2", "h3", "h4", "h5", "h6"}:
                continue
        yield tag


def _fetch_and_extract(url: str) -> str:
    """Fetch the URL and extract prioritized content as a single string."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        logger.warning("requests fetch failed for %s: %s", url, e)
        return "No content"

    html = resp.text or ""
    # Prefer lxml if available (faster); fall back to html.parser
    try:
        soup = BeautifulSoup(html, "lxml")
    except Exception:
        soup = BeautifulSoup(html, "html.parser")

    parts = []
    seen_texts = set()

    for elem in _iter_priority_blocks(soup):
        if elem.name in {"ol", "ul"}:
            # join li children in order
            lis = elem.find_all("li")
            li_texts = []
            for li in lis:
                t = _safe_get_text(li)
                if t and t not in seen_texts:
                    li_texts.append(t)
                    seen_texts.add(t)
            if li_texts:
                parts.append(" • ".join(li_texts))  # bullet-style join for readability
        else:
            text = _safe_get_text(elem)
            if not text:
                continue
            # avoid duplicates
            if text in seen_texts:
                continue
            seen_texts.add(text)
            parts.append(text)

        # stop early if we already have enough content
        if sum(len(p) for p in parts) >= MAX_CHARS:
            break

    if not parts:
        return "No content"

    # Join with two newlines between blocks to preserve some structure
    full_text = "\n\n".join(parts)
    return full_text


def load_node(state: ResearchState) -> Dict[str, str]:
    """
    Load the page content using requests + BeautifulSoup and return dict with 'content'.
    """
    if not state.url:
        return {"content": "No URL to load"}

    url = str(state.url)
    try:
        content = _fetch_and_extract(url)
    except Exception as e:
        logger.exception("Unexpected error extracting content from %s: %s", url, e)
        content = "No content"

    # truncate to MAX_CHARS for downstream safety
    truncated = content[:MAX_CHARS]
    return {"content": truncated}
