# graph_web/loader.py
"""
HTML loader using requests + BeautifulSoup with targeted extraction.

Priority extraction order:
  1. <h1 class="title hypothesis_container">
  2. <h2 id="html-abstract-title">
  3. all <div class="html-p"> elements (joined as paragraphs)
Fallback: full visible-page text extraction.

Returns: {"content": <truncated_text>}
"""

from shared import ResearchState
from typing import Dict, Optional
import logging
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Limit content length to ~100,000 characters (≈ 32,000 tokens max)
MAX_CHARS = 100_000

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
    )
}


def _fetch_html(url: str) -> Optional[str]:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        logger.warning("requests fetch failed for %s: %s", url, e)
        return None


def _extract_targeted(soup: BeautifulSoup) -> Optional[str]:
    """
    Try the prioritized selectors:
      - h1.title.hypothesis_container
      - h2#html-abstract-title
      - div.html-p (join as paragraphs)
    Return the first match's text or None if none found.
    """
    # 1) h1 with both classes 'title' and 'hypothesis_container'
    el = soup.select_one("h1.title.hypothesis_container")
    if el:
        text = el.get_text(separator=" ", strip=True)
        if text:
            logger.info("Extracted content using selector: h1.title.hypothesis_container")
            return text

    # 2) h2 with id html-abstract-title
    el = soup.select_one("h2#html-abstract-title")
    if el:
        text = el.get_text(separator=" ", strip=True)
        if text:
            logger.info("Extracted content using selector: h2#html-abstract-title")
            return text

    # 3) all div.html-p (collect paragraphs)
    divs = soup.select("div.html-p")
    if divs:
        paragraphs = []
        for d in divs:
            ptext = d.get_text(separator=" ", strip=True)
            if ptext:
                paragraphs.append(ptext)
        if paragraphs:
            joined = "\n\n".join(paragraphs)
            logger.info("Extracted content using selector: div.html-p (joined %d paragraphs)", len(paragraphs))
            return joined

    return None


def _extract_visible_text(soup: BeautifulSoup) -> str:
    """Fallback generic visible text extraction."""
    for tag in soup(["script", "style", "noscript", "iframe", "header", "footer", "svg"]):
        try:
            tag.decompose()
        except Exception:
            pass

    texts = list(soup.stripped_strings)
    if not texts:
        return "No content"
    return " ".join(texts)


def load_node(state: ResearchState) -> Dict[str, str]:
    """
    Load the page content from state.url using requests + BeautifulSoup,
    preferring targeted selectors first.
    """
    if not state.url:
        return {"content": "No URL to load"}

    url = str(state.url)
    html = _fetch_html(url)
    if not html:
        return {"content": "No content"}

    # Parse using lxml if available for speed, else fallback
    try:
        soup = BeautifulSoup(html, "lxml")
    except Exception:
        soup = BeautifulSoup(html, "html.parser")

    # Try targeted extraction
    try:
        targeted = _extract_targeted(soup)
        if targeted:
            content = targeted
        else:
            # Fallback to full visible text
            content = _extract_visible_text(soup)
    except Exception as e:
        logger.exception("Error during extraction for %s: %s", url, e)
        content = "No content"

    truncated = content[:MAX_CHARS]
    return {"content": truncated}
