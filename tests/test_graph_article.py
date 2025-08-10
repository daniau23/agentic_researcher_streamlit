from graph_article.graph_article import article_graph
from shared import ResearchState

class DummyResponse:
    def __init__(self, content: str):
        self.content = content


def test_article_graph_accept(mocker):
    # Patch writer_chain.invoke to return an object with .content
    mock_writer_chain = mocker.Mock()
    mock_writer_chain.invoke.return_value = DummyResponse("Test abstract")
    mocker.patch("graph_article.writer.writer_chain", mock_writer_chain)

    # Patch critic_chain.invoke to return ACCEPTED (object with .content)
    mock_critic_chain = mocker.Mock()
    mock_critic_chain.invoke.return_value = DummyResponse("ACCEPTED")
    mocker.patch("graph_article.critic.critic_chain", mock_critic_chain)

    init_state = ResearchState(input="Title", category="Category")
    final_state = article_graph.invoke(init_state)

    assert final_state["final_abstract"] == "Test abstract"
    assert final_state["critique"] == "ACCEPTED"


def test_article_graph_reject_then_accept(mocker):
    # Patch writer_chain.invoke to return an object with .content
    mock_writer_chain = mocker.Mock()
    mock_writer_chain.invoke.return_value = DummyResponse("Test abstract")
    mocker.patch("graph_article.writer.writer_chain", mock_writer_chain)

    # Setup critic_chain.invoke to reject first (REJECTED), then accept (ACCEPTED)
    call_count = {"count": 0}

    def critic_invoke_side_effect(*args, **kwargs):
        if call_count["count"] == 0:
            call_count["count"] += 1
            return DummyResponse("REJECTED")
        return DummyResponse("ACCEPTED")

    mock_critic_chain = mocker.Mock()
    mock_critic_chain.invoke.side_effect = critic_invoke_side_effect
    mocker.patch("graph_article.critic.critic_chain", mock_critic_chain)

    init_state = ResearchState(input="Title", category="Category")
    final_state = article_graph.invoke(init_state)

    assert final_state["final_abstract"] == "Test abstract" or final_state["final_abstract"] == "Final abstract"
    assert final_state["critique"] == "ACCEPTED"
