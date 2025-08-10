from graph_web.summarizer import summarize_node
from shared import ResearchState

def test_summarize_node_with_content(mocker):
    class FakeResponse:
        def __init__(self, content):
            self.content = content

    mock_chain = mocker.Mock()
    mock_chain.invoke.return_value = FakeResponse("Summary of the content.")

    mocker.patch("graph_web.summarizer.summarize_chain", mock_chain)

    state = ResearchState(content="Some long content")
    result = summarize_node(state)
    assert result["summary"] == "Summary of the content."


def test_summarize_node_no_content():
    state = ResearchState(content=None)
    result = summarize_node(state)
    assert result["summary"] == "No content to summarize"