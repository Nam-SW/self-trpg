from config import model_type, model_args

from langchain_openai import ChatOpenAI
from langchain_openai import AzureChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_vertexai import ChatVertexAI

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
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


def get_prompt_chain(prompt: str, **kwargs):
    prompt_template = PromptTemplate.from_template(prompt)
    model = get_agent(**kwargs)
    parser = StrOutputParser()

    chain = prompt_template | model | parser
    return chain


def get_chat_chain(prompts: list[tuple[str, str]], **kwargs):
    prompt_template = ChatPromptTemplate.from_template(prompts)
    model = get_agent(**kwargs)
    parser = StrOutputParser()

    chain = prompt_template | model | parser
    return chain


class MultiTernChain:
    def __init__(self, system_prompt: str, **kwargs) -> None:
        self.system_prompt = system_prompt

        self.model = get_agent(**kwargs)
        self.parser = StrOutputParser()
        self.chain = None
        self.clear_history()

    @property
    def chat_history(self):
        return [
            f"{'이야기꾼' if isinstance(m, AIMessage) else '유저'}: {m.content}"
            for m in self.__chat_history
        ]

    def clear_history(self):
        self.__chat_history = []

    def set_system_prompt(self, system_prompt_args: dict = {}):
        self.system_prompt_args = system_prompt_args
        prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt.format(**self.system_prompt_args)),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{message}"),
            ]
        )
        self.chain = prompt_template | self.model | self.parser

    def get_answer_stream(self, input_text: str):
        if self.chain is None:
            raise RuntimeError("chain must be init before answer, through `set_system_prompt()`")

        message = HumanMessage(content=input_text)
        response = ""

        for chunk in self.chain.stream(
            {
                "message": message,
                "chat_history": self.__chat_history,
            },
            # config={"metadata": {"conversation_id": conversation_id}},
        ):
            yield chunk
            response += chunk
        else:
            response = self.chain.invoke(
                {
                    "message": message,
                    "chat_history": self.__chat_history,
                }
            )

        self.__chat_history.extend(
            [
                message,
                AIMessage(content=response),
            ]
        )

    def get_answer(self, input_text: str):
        if self.chain is None:
            raise RuntimeError("chain must be init before answer, through `set_system_prompt()`")

        response = self.chain.invoke({"message": input_text, "chat_history": self.__chat_history})
        self.__chat_history.extend(
            [
                HumanMessage(content=input_text),
                AIMessage(content=response),
            ]
        )
        return response
