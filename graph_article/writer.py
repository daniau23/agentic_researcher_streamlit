import os
from utils.retry import retry
from requests.exceptions import Timeout
from langchain.prompts import PromptTemplate
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

from utils.logger import setup_logger

logger = setup_logger(__name__)

HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
repo_id = "meta-llama/Llama-3.2-3B-Instruct"

model_kwargs_writer = {
    "max_new_tokens": 200,
    "max_length": 100,
    "temperature": 0.8,
    "timeout": 6000,
}

llm = HuggingFaceEndpoint(
    repo_id=repo_id,
    huggingfacehub_api_token=HUGGINGFACEHUB_API_TOKEN,
    **model_kwargs_writer
)
chat_model = ChatHuggingFace(llm=llm)

prompt = PromptTemplate.from_template(
    "Generate an abstract for the paper titled '{input}' in the domain of {category}."
)

writer_chain = prompt | chat_model

@retry((Timeout,))
def writer_node(state):
    logger.info(f"writer_node started with input: '{state.input}' and category: '{state.category}'")
    try:
        result = writer_chain.invoke({"input": state.input, "category": state.category})
        logger.info("writer_node successfully generated abstract")
        return {"abstract": result.content}
    except Exception as e:
        logger.error(f"writer_node error: {e}")
        raise