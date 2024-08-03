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
    def __init__(self, system_prompt: str, limit_turn: int = 20, **kwargs) -> None:
        self.system_prompt = system_prompt
        self.limit_turn = limit_turn

        self.model = get_agent(**kwargs)
        self.parser = StrOutputParser()
        self.chain = None
        self.clear_history()

    @property
    def chat_history(self):
        return [
            {"role": "ai" if isinstance(m, AIMessage) else "user", "message": m.content}
            for m in self.__chat_history
        ]

    def clear_history(self):
        self.__chat_history = []

    def init_new_session(self, system_prompt_args: dict = {}) -> str:
        self.clear_history()
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

        init_chain = self.model | self.parser
        init_result = init_chain.invoke(sys_prompt)
        # print(init_result)

        self.__chat_history.append(AIMessage(content=convert_json(init_result)["context"]))
        return init_result

    def get_turn_limit_prompt(self) -> str:
        limit = self.limit_turn - len(self.chat_history) // 2
        return f"\n\nAnswer in JSON format, and Try to end the conversation within {max(limit, 1)} turns."

    def get_answer_stream(self, input_text: str):
        if self.chain is None:
            raise RuntimeError("chain must be init before answer, through `set_system_prompt()`")

        response = ""
        for chunk in self.chain.stream(
            {
                "message": HumanMessage(content=input_text + self.get_turn_limit_prompt()),
                "chat_history": self.__chat_history,
            },
            # config={"metadata": {"conversation_id": conversation_id}},
        ):
            yield chunk
            response += chunk
        self.__chat_history += [
            HumanMessage(content=input_text),
            AIMessage(content=convert_json(response)["context"]),
        ]

    def get_answer(self, input_text: str):
        if self.chain is None:
            raise RuntimeError("chain must be init before answer, through `set_system_prompt()`")

        response = self.chain.invoke({"message": input_text, "chat_history": self.__chat_history})
        # print(response)
        self.__chat_history += [
            HumanMessage(content=input_text + self.get_turn_limit_prompt()),
            AIMessage(content=convert_json(response)["context"]),
        ]
        return response
