import os
from utils.retry import retry
from requests.exceptions import Timeout
from langchain.prompts import PromptTemplate
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from utils.logger import setup_logger

logger = setup_logger(__name__)

HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
repo_id = "mistralai/Mistral-7B-Instruct-v0.3"

model_kwargs_critic = {
    "max_new_tokens": 5,
    "temperature": 0.1,
    "timeout": 6000,
}

llm = HuggingFaceEndpoint(
    repo_id=repo_id,
    huggingfacehub_api_token=HUGGINGFACEHUB_API_TOKEN,
    **model_kwargs_critic
)
chat_model = ChatHuggingFace(llm=llm)

prompt = PromptTemplate.from_template(
    "You are a strict research reviewer. Review the abstract:\n\n{abstract}\n\nRespond with 'ACCEPTED' or 'REJECTED'."
)
critic_chain = prompt | chat_model

@retry((Timeout,))
def critic_node(state):
    logger.info(f"critic_node started reviewing abstract: '{state.abstract[:50]}...'")
    try:
        result = critic_chain.invoke({"abstract": state.abstract})
        critique = result.content.strip().upper()
        logger.info(f"critic_node critique result: {critique}")
        return {
            "critique": critique,
            "final_abstract": state.abstract if critique == "ACCEPTED" else None
        }
    except Exception as e:
        logger.error(f"critic_node error: {e}")
        raise