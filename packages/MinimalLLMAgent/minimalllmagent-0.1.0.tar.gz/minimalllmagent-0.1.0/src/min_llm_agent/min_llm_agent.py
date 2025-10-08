import os
from typing import Union, List
from openai import OpenAI
from LyPythonToolbox import lyprint_separator, overwrite_stdout


supported_platform_name_list = ["OpenAI", "Grok", "DeepSeek", "Gemini", "Ali"]

api_key_envname_dict = {
    "OpenAI": "OPENAI_API_KEY",
    "Grok": "XAI_API_KEY",
    "DeepSeek": "DEEPSEEK_API_KEY",
    "Gemini": "GEMINI_API_KEY",
    "Ali": "DASHSCOPE_API_KEY",
}

base_url_envname_dict = {
    "OpenAI": "OPENAI_BASE_URL",
    "Grok": "XAI_BASE_URL",
    "DeepSeek": "DEEPSEEK_BASE_URL",
    "Gemini": "GEMINI_BASE_URL",
    "Ali": "DASHSCOPE_BASE_URL",
}

INTERACTIVE_HELP_STR = """
- To submit a query: start a new line, type '/', and press Enter.
    - Line breaks are allowed and recognized as a part of the query.
- Query 'q' or 'Q' to exit.
- Query 'm' or 'M' to print the memory.

See more details on: https://github.com/YueLin301/min_llm_agent
"""


def init_client(platform_name):
    assert (
        platform_name in supported_platform_name_list
    ), f"Invalid platform name: {platform_name}\nAvailable platforms: {supported_platform_name_list}"

    client = OpenAI(
        api_key=os.getenv(api_key_envname_dict[platform_name]),
        base_url=os.getenv(base_url_envname_dict[platform_name]),
    )

    return client


class min_llm_agent_class:
    def __init__(self, platform_name: str, model_name: str, name: str = "Yue's minimal LLM agent"):
        self.platform_name = platform_name
        self.model_name = model_name
        self.name = name
        self.memory = []
        self.client = init_client(platform_name)

    def messages_preprocess(self, messages_raw: Union[str, List[dict]], role: str = "user"):
        assert role in ["user", "system"], f"Invalid role: {role}\nAvailable roles: {['user', 'system']}"

        if isinstance(messages_raw, str):
            messages = [
                {
                    "role": role,
                    "content": messages_raw,
                }
            ]
        elif isinstance(messages_raw, list) and all(isinstance(item, dict) for item in messages_raw):
            messages = messages_raw
        else:
            raise ValueError(f"Invalid input: {messages_raw}\nAvailable types: {str, list[dict]}")

        return messages

    # @lyprint_elapsed_time
    def vanilla_query(self, messages: List[dict]):
        assert isinstance(messages, list) and all(
            isinstance(item, dict) for item in messages
        ), f"Invalid input: {messages}\nAvailable types: {list[dict]}"

        output_full = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            n=1,  # Generate 1 answer.
        )
        output_text = output_full.choices[0].message.content

        return output_text

    def add_anwer_to_memory(self, answer: str):
        self.memory = self.memory + [
            {
                "role": "assistant",
                "content": answer,
            }
        ]

    def reset_memory(self):
        self.memory = []

    def get_memory(self):
        return self.memory

    def set_memory(self, memory: List[dict]):
        self.memory = memory

    def append_memory(self, memory: List[dict]):
        self.memory = self.memory + memory

    def print_memory(self, memory_item_separator: str = None):
        lyprint_separator("=")
        print("Memory:")
        lyprint_separator("-")
        for i, message in enumerate(self.memory):
            role_i = message["role"]
            content_i = message["content"]
            print(f"""[{i}] ({role_i}): {content_i}""")
            if memory_item_separator is not None:
                assert isinstance(memory_item_separator, str), f"Invalid memory item separator: {memory_item_separator}\nAvailable types: {str}"
                lyprint_separator(memory_item_separator)
        if memory_item_separator is not None:
            overwrite_stdout(1)
        lyprint_separator("=")

    def __call__(self, messages_raw: Union[str, List[dict]], role: str = "user", with_memory: bool = True):

        messages = self.messages_preprocess(messages_raw, role)

        if with_memory:
            self.memory = self.memory + messages
            messages = self.memory

        answer = self.vanilla_query(messages)

        if with_memory:
            self.add_anwer_to_memory(answer)

        return answer

    def interact(self):
        lyprint_separator()

        print(f"""\nThis is {self.name}, powered by the model "{self.model_name}".\n{INTERACTIVE_HELP_STR}""")

        time_step = 0
        while True:
            lyprint_separator(">")

            print(f"[{time_step}] Question:")
            question_lines = []
            first_question_line = True
            while True:
                line = input("> " if first_question_line else "")
                if line.strip().upper() == "/":
                    break
                question_lines.append(line)
                first_question_line = False

            question = "\n".join(question_lines)

            # ================================

            if question.strip().upper() == "Q":
                break
            elif question.strip().upper() == "M":
                self.print_memory()
                continue

            # ================================

            print("")
            lyprint_separator("<")
            print("Querying...")

            response = self(question, role="user")

            overwrite_stdout(1)
            output_print_str = f"[{time_step}] Answer by the model {self.model_name}:"
            print(output_print_str)
            # print("-" * len(output_print_str))
            print(response)
            print("\n")
            time_step += 1
