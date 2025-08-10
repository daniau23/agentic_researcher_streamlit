from graph_article.writer import writer_node

def test_writer_node_basic(mocker):
    class FakeResponse:
        def __init__(self, content):
            self.content = content

    mock_chain = mocker.Mock()
    mock_chain.invoke.return_value = FakeResponse("This is a generated abstract.")

    mocker.patch("graph_article.writer.writer_chain", mock_chain)

    class DummyState:
        input = "Test Title"
        category = "Science"

    result = writer_node(DummyState())
    assert result["abstract"] == "This is a generated abstract."
