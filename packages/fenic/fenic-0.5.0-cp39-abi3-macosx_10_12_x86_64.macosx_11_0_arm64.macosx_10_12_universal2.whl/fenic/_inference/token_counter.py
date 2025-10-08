from typing import Protocol, Union

import tiktoken

from fenic._constants import PREFIX_TOKENS_PER_MESSAGE, TOKENS_PER_NAME
from fenic._inference.common_openai.openai_utils import convert_messages
from fenic._inference.types import LMRequestMessages

Tokenizable = Union[str | LMRequestMessages]

class TokenCounter(Protocol):
    def count_tokens(self, messages: Tokenizable) -> int: ...

class TiktokenTokenCounter(TokenCounter):

    def __init__(self, model_name: str, fallback_encoding: str = "o200k_base"):
        try:
            self.tokenizer = tiktoken.encoding_for_model(model_name)
        except KeyError:
            self.tokenizer = tiktoken.get_encoding(fallback_encoding)

    def count_tokens(self, messages: Tokenizable) -> int:
        if isinstance(messages, str):
            return len(self.tokenizer.encode(messages))
        elif isinstance(messages, LMRequestMessages):
            return self._count_message_tokens(convert_messages(messages))
        else:
            raise TypeError(f"Expected str or LMRequestMessages, got {type(messages)}")

    def _count_message_tokens(self, messages: list[dict[str, str]]) -> int:
        num_tokens = 0
        for message in messages:
            if "content" in message and isinstance(message["content"], list):
                num_tokens += self._count_message_tokens(messages=message["content"])
                continue
            if "type" in message and message["type"] == "file":
                # providers count file tokens differently, so we leave that up to the client
                continue
            num_tokens += PREFIX_TOKENS_PER_MESSAGE  # Every message starts with <im_start>{role/name}\n{content}<im_end>\n
            for key, value in message.items():
                num_tokens += len(self.tokenizer.encode(value))
                if key == "name":
                    num_tokens -= TOKENS_PER_NAME  # Subtract one token if the 'name' field is present

        num_tokens += 2  # Every assistant reply is primed with <im_start>assistant

        return num_tokens
