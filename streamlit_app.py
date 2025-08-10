import streamlit as st
from shared import ResearchState
from graph_article.graph_article import article_graph
from graph_web.graph_web import web_graph
from pydantic import ValidationError
import os

st.title("Agentic Research Abstract Generator and Web Content Summariser Agent With Langraph")

# Initialize session state for API key if not present
if "hf_api_key" not in st.session_state:
    st.session_state.hf_api_key = ""

# API key input with pre-filled value from session state
hf_api_key = st.text_input(
    "Enter your HuggingFace API key (required to use language models)",
    type="password",
    value=st.session_state.hf_api_key,
    help="Get it from https://huggingface.co/settings/tokens"
)

# Save input back to session state
st.session_state.hf_api_key = hf_api_key

CREDITS_EXCEEDED_MSG = (
    "You have exceeded your monthly included credits for Inference Providers. "
    "Subscribe to PRO to get 20x more monthly included credits."
)

if not hf_api_key:
    st.warning("Please enter your HuggingFace API key to use the app.")
    st.stop()

# Set the environment variable so underlying libs can authenticate
os.environ["HUGGINGFACEHUB_API_TOKEN"] = hf_api_key

option = st.selectbox("Select a task", ["Generate Research Abstract", "Summarize Webpage"])

if option == "Generate Research Abstract":
    title = st.text_input("Enter research title")
    category = st.text_input("Enter category")

    if st.button("Generate Abstract"):
        if not title or not category:
            st.error("Please enter both title and category.")
        else:
            with st.spinner("Generating abstract..."):
                init_state = ResearchState(input=title, category=category)
                try:
                    final_state = article_graph.invoke(init_state)
                    if final_state.get("final_abstract"):
                        st.success("Final Abstract:")
                        st.write(final_state["final_abstract"])
                    else:
                        st.warning("No abstract was accepted by the critic.")
                except Exception as e:
                    err_str = str(e)
                    if CREDITS_EXCEEDED_MSG in err_str:
                        st.error(CREDITS_EXCEEDED_MSG)
                    else:
                        st.error(f"Error: {err_str}")

elif option == "Summarize Webpage":
    url = st.text_input("Enter URL to summarize")

    if st.button("Summarize"):
        if not url:
            st.error("Please enter a URL.")
        else:
            with st.spinner("Summarizing..."):
                try:
                    init_state = ResearchState(url=url)
                    final_state = web_graph.invoke(init_state)
                    st.success("Summary:")
                    st.write(final_state.get("summary", "No summary available."))
                except ValidationError as ve:
                    st.error(f"Invalid URL: {ve}")
                except Exception as e:
                    err_str = str(e)
                    if CREDITS_EXCEEDED_MSG in err_str:
                        st.error(CREDITS_EXCEEDED_MSG)
                    else:
                        st.error(f"Error: {err_str}")