import sys
import os
import importlib
import pytest
from dotenv import load_dotenv

# Ensure project root is importable when tests run from anywhere
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

load_dotenv()  # Load env vars for tests


class _MockResponse:
    def __init__(self, content: str):
        self.content = content


@pytest.fixture(autouse=True)
def no_real_llm_calls(monkeypatch):
    """
    Autouse fixture that prevents real LLM/endpoint calls during tests
    by monkeypatching chain-like objects to return dummy responses.

    This tries to import modules and patches attributes on module objects
    instead of using dotted-name strings (which cause import attempts
    and can raise ModuleNotFoundError).
    """

    # Helper to safely import a module name, return None on failure
    def try_import(name):
        try:
            return importlib.import_module(name)
        except ModuleNotFoundError:
            return None

    # 1) Patch writer_chain in graph_article.writer if present
    writer_mod = try_import("graph_article.writer")
    if writer_mod is not None:
        monkeypatch.setattr(
            writer_mod,
            "writer_chain",
            lambda *a, **kw: _MockResponse("Mocked writer response"),
            raising=False,
        )

    # 2) Patch critic_chain in graph_article.critic if present
    critic_mod = try_import("graph_article.critic")
    if critic_mod is not None:
        monkeypatch.setattr(
            critic_mod,
            "critic_chain",
            lambda *a, **kw: _MockResponse("ACCEPTED"),
            raising=False,
        )

    # 3) Patch summarizer: try both spellings
    summarizer_mod = try_import("graph_web.summarizer") or try_import("graph_web.summariser")
    if summarizer_mod is not None:
        # patch summarize_chain (callable)
        monkeypatch.setattr(
            summarizer_mod,
            "summarize_chain",
            lambda *a, **kw: _MockResponse("Mocked summary"),
            raising=False,
        )

    # 4) Patch ChatHuggingFace class in langchain_huggingface if available
    lch_mod = try_import("langchain_huggingface")
    if lch_mod is not None:
        # Replace the ChatHuggingFace class with a callable factory that returns an object
        # whose __call__ returns a MockResponse. Simpler: patch the class name itself to a
        # lambda that returns our callable.
        class DummyChat:
            def __init__(self, *a, **kw):
                pass

            def __call__(self, *a, **kw):
                return _MockResponse("Mocked generic LLM response")

        monkeypatch.setattr(lch_mod, "ChatHuggingFace", DummyChat, raising=False)

    # 5) As an extra safe fallback, if modules aren't importable, try to monkeypatch the
    # dotted names but don't let import errors propagate (monkeypatch.setattr with strings
    # can still try to import — we avoid that by only patching module objects above).
    yield