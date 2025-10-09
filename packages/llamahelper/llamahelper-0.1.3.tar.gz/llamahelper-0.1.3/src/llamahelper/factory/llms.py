""" llm """
from enum import Enum
from llama_index.llms.openrouter import OpenRouter
from typing import List, Any
from dotenv import load_dotenv
import os
load_dotenv()

class LLMType(Enum):
    """ enum """
    BIANXIELLM = 'BIANXIELLM'
    # 添加更多选项

class LLMFactory:
    """ factory """
    def __new__(cls, llm_type: LLMType | str,
                     model_name:str | None = None) -> Any:
        if isinstance(llm_type,LLMType):
            assert llm_type.value in [i.value for i in LLMType]
            key_name = llm_type.value
        else:
            assert llm_type in [i.value for i in LLMType]
            key_name = llm_type
        instance = None
        api_key = os.getenv("BIANXIE_API_KEY")
        api_base = os.getenv("BIANXIE_BASE")

        if key_name == 'BIANXIELLM':
            llm = OpenRouter(
                api_key=api_key,
                api_base=api_base,
                # max_tokens=256,
                # context_window=4096,
                model=model_name or "gemini-2.5-flash-preview-05-20-nothinking",
            )
            instance = llm

        else:
            raise TypeError('Unknown type')

        return instance
