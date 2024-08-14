import json
from typing import Optional, Union

from config import model_type, model_args

from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_vertexai import ChatVertexAI

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_core.pydantic_v1 import BaseModel

# from langchain_community.callbacks.manager import get_openai_callback

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


def convert_json(message: AIMessage) -> Union[dict, list]:
    return json.loads(message.json())


def get_prompt_chain(
    prompt: str,
    prompt_kwargs: dict = {},
    agent_kwargs: dict = {},
    output_struct: Optional[BaseModel] = None,
):
    prompt_template = PromptTemplate.from_template(prompt, **prompt_kwargs)
    model = get_agent(**agent_kwargs)

    if output_struct is not None:
        model = model.with_structured_output(
            output_struct,
        )
    parser = StrOutputParser() if output_struct is None else convert_json

    chain = prompt_template | model | parser

    return chain


def get_chat_chain(
    prompt: str,
    prompt_kwargs: dict = {},
    agent_kwargs: dict = {},
    output_struct: Optional[BaseModel] = None,
):
    prompt_template = ChatPromptTemplate.from_template(prompt, **prompt_kwargs)
    model = get_agent(**agent_kwargs)

    if output_struct is not None:
        model = model.with_structured_output(
            output_struct,
        )
    parser = StrOutputParser() if output_struct is None else convert_json

    chain = prompt_template | model | parser

    return chain


class MultiTernChain:
    def __init__(
        self,
        system_prompt: str,
        limit_turn: int = 20,
        agent_kwargs: dict = {},
        output_struct: Optional[BaseModel] = None,
        history_key: Optional[str] = None,
        user_prefix: str = "",
    ) -> None:
        self.system_prompt = system_prompt
        self.limit_turn = limit_turn
        self.structed = output_struct is not None

        if self.structed and history_key is None:
            raise ValueError("structed agent must have `history_key`")
        if not self.structed and history_key is not None:
            raise ValueError("unstructed agent don't have `history_key`")

        self.model = get_agent(**agent_kwargs)
        if output_struct is not None:
            self.model = self.model.with_structured_output(
                output_struct,
            )
        self.parser = StrOutputParser() if output_struct is None else convert_json
        self.history_key = history_key
        self.user_prefix = user_prefix

        self.chain = None
        self.clear_history()

    @property
    def chat_history(self):
        return [
            (
                {"role": "ai", "message": m.content}
                if isinstance(m, AIMessage)
                else {"role": "user", "message": m.content[len(self.user_prefix) :]}
            )
            for m in self.__chat_history
        ]

    @chat_history.setter
    def chat_history(self, value: list[dict]):
        self.clear_history()
        for log in value:
            if log is None:
                self.__chat_history.append(None)
            if log["role"] == "ai":
                self.__chat_history.append(AIMessage(log["message"]))
            elif log["role"] == "user":
                self.__chat_history.append(HumanMessage(self.user_prefix + log["message"]))
            else:
                raise KeyError(f"`{log['role']}` is unexpected role.")

    def clear_history(self):
        self.__chat_history = []

    def set_system_prompt(self, system_prompt_args: dict = {}):
        self.system_prompt_args = system_prompt_args
        sys_prompt = self.system_prompt.format(
            **self.system_prompt_args, limit_turn=self.limit_turn
        )
        prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", sys_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "user: {{message}}"),
            ],
            template_format="mustache",  # json 형태 입력받을 수 있게
        )
        self.chain = prompt_template | self.model | self.parser

    def init_new_session(self) -> str:
        self.clear_history()

        init_chain = self.model | self.parser
        init_result = init_chain.invoke(self.chain.first.messages[0].prompt.template)
        # print(init_result)

        hist = init_result[self.history_key] if self.structed else init_result

        self.__chat_history.append(AIMessage(content=hist))
        return init_result

    def get_turn_limit_prompt(self) -> str:
        limit = self.limit_turn - len(self.chat_history) // 2
        return f"\n\nTry to end the conversation within {max(limit, 1)} turns."

    # def get_answer_stream(self, input_text: str):
    #     # TODO: typing_extensions 로 바꾸고 스트리밍 구현
    #     if self.chain is None:
    #         raise RuntimeError("chain must be init before answer, through `set_system_prompt()`")

    #     response = ""
    #     for chunk in self.chain.stream(
    #         {
    #             "message": HumanMessage(content=input_text + self.get_turn_limit_prompt()),
    #             "chat_history": self.__chat_history,
    #         },
    #         # config={"metadata": {"conversation_id": conversation_id}},
    #     ):
    #         yield chunk
    #         response += chunk
    #     self.__chat_history += [
    #         HumanMessage(content=input_text),
    #         AIMessage(content=convert_json(response)["context"]),
    #     ]

    def get_answer(self, input_text: str):
        if self.chain is None:
            raise RuntimeError("chain must be init before answer, through `set_system_prompt()`")

        input_text = self.user_prefix + input_text
        response = self.chain.invoke(
            {
                "message": input_text + self.get_turn_limit_prompt(),
                "chat_history": self.__chat_history,
            }
        )

        hist = response[self.history_key] if self.structed else response

        # print(response)
        self.__chat_history += [
            HumanMessage(content=input_text),
            AIMessage(content=hist),
        ]
        return response
