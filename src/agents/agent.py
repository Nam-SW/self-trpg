from config import model_type, model_args

from langchain_openai import ChatOpenAI
from langchain_openai import AzureChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_vertexai import ChatVertexAI

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_community.callbacks.manager import get_openai_callback

from utils.utils import convert_json


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


def get_prompt_chain(
    prompt: str,
    prompt_kwargs: dict = {},
    agent_kwargs: dict = {},
):
    prompt_template = PromptTemplate.from_template(prompt, **prompt_kwargs)
    model = get_agent(**agent_kwargs)
    parser = StrOutputParser()

    chain = prompt_template | model | parser
    return chain


def get_chat_chain(
    prompts: list[tuple[str, str]],
    prompt_kwargs: dict = {},
    agent_kwargs: dict = {},
):
    prompt_template = ChatPromptTemplate.from_template(prompts, **prompt_kwargs)
    model = get_agent(**agent_kwargs)
    parser = StrOutputParser()

    chain = prompt_template | model | parser
    return chain


class MultiTernChain:
    def __init__(self, system_prompt: str, **kwargs) -> None:
        self.system_prompt = system_prompt

        self.model = get_agent(**kwargs)
        self.parser = StrOutputParser()
        self.chain = None

    @property
    def chat_history(self):
        return [
            f"{'이야기꾼' if isinstance(m, AIMessage) else '유저'}: {m.content}"
            for m in self.__chat_history
        ]

    def clear_history(self):
        self.__chat_history = []

    def init_new_session(self, system_prompt_args: dict = {}) -> str:
        self.clear_history()
        self.system_prompt_args = system_prompt_args
        sys_prompt = self.system_prompt.format(**self.system_prompt_args)
        prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", sys_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                (
                    "user",
                    ("행동:{{message}}\n"),
                ),
            ],
            template_format="mustache",  # json 형태 입력받을 수 있게
        )
        self.chain = prompt_template | self.model | self.parser

        init_chain = self.model | self.parser
        init_result = init_chain.invoke(sys_prompt)
        # print(init_result)

        self.__chat_history.append(AIMessage(content=convert_json(init_result)["context"]))
        return init_result

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
        self.__chat_history.extend(
            [
                message,
                AIMessage(content=convert_json(response)["context"]),
            ]
        )

    def get_answer(self, input_text: str):
        if self.chain is None:
            raise RuntimeError("chain must be init before answer, through `set_system_prompt()`")

        response = self.chain.invoke({"message": input_text, "chat_history": self.__chat_history})
        # print(response)
        self.__chat_history.extend(
            [
                HumanMessage(content=input_text),
                AIMessage(content=convert_json(response)["context"]),
            ]
        )
        return response
