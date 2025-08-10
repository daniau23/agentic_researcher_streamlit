import pytest
from graph_article.critic import critic_node

@pytest.mark.parametrize(
    "mock_content,expected_abstract",
    [
        ("ACCEPTED", "A valid abstract"),
        ("REJECTED", None),
    ]
)
def test_critic_node(mock_content, expected_abstract, mocker):
    class FakeResponse:
        def __init__(self, content):
            self.content = content

    mock_chain = mocker.Mock()
    mock_chain.invoke.return_value = FakeResponse(mock_content)

    mocker.patch("graph_article.critic.critic_chain", mock_chain)

    class DummyState:
        abstract = "A valid abstract"

    result = critic_node(DummyState())
    assert result["critique"] == mock_content
    assert result["final_abstract"] == expected_abstract