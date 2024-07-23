from config import model_type, model_args

from langchain_openai import ChatOpenAI
from langchain_openai import AzureChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_vertexai import ChatVertexAI

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_community.callbacks.manager import get_openai_callback


def get_agent(**kwargs):
    match model_type:
        case "openai":
            model_cls = ChatOpenAI
        case "azure":
            model_cls = AzureChatOpenAI
        case "anthropic":
            model_cls = ChatAnthropic
        case "google":
            model_cls = ChatVertexAI

    agent = model_cls(**model_args, **kwargs)
    return agent


def get_chain(prompt: str, **kwargs):
    prompt_template = PromptTemplate.from_template(prompt)
    model = get_agent(**kwargs)
    parser = StrOutputParser()

    chain = prompt_template | model | parser
    return chain
