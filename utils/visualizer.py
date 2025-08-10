from IPython.display import Image, display
from pathlib import Path

def graph_visualiser(graph, filename: str = "graph.jpg", show: bool = True):
    """
    Visualize and save the compiled LangGraph as a .jpg image.

    Args:
        graph: Compiled LangGraph object.
        filename (str): Path to save the image.
        show (bool): Whether to display the image in notebook (optional).
    """
    try:
        # Get raw image data
        image_data = graph.get_graph().draw_mermaid_png()

        # Save to file
        output_path = Path(filename)
        with open(output_path, "wb") as f:
            f.write(image_data)

        if show:
            display(Image(filename))
        print(f"✅ Graph image saved as: {output_path.resolve()}")

    except Exception as e:
        print(f"❌ Failed to generate graph image: {e}")