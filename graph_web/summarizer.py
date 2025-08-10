import os
from utils.retry import retry
from requests.exceptions import Timeout
from langchain.prompts import PromptTemplate
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

from utils.logger import setup_logger

logger = setup_logger(__name__)

HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
repo_id = "mistralai/Mistral-7B-Instruct-v0.3"

model_kwargs = {
    "temperature": 0.1,
    "max_new_tokens": 100,
    "timeout": 6000,
}

llm = HuggingFaceEndpoint(
    repo_id=repo_id,
    huggingfacehub_api_token=HUGGINGFACEHUB_API_TOKEN,
    **model_kwargs
)
chat_model = ChatHuggingFace(llm=llm)

prompt = PromptTemplate.from_template(
    "Summarize the following content concisely:\n\n{content}\n\nSummary:"
)
summarize_chain = prompt | chat_model

@retry((Timeout,))
def summarize_node(state):
    logger.info("summarize_node started")
    if not state.content:
        logger.warning("summarize_node found no content to summarize")
        return {"summary": "No content to summarize"}
    try:
        result = summarize_chain.invoke({"content": state.content})
        logger.info("summarize_node successfully generated summary")
        return {"summary": result.content}
    except Exception as e:
        logger.error(f"summarize_node error: {e}")
        raise
