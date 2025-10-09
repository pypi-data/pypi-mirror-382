""" extractor """
import re
from enum import Enum
from typing import List, Dict, Any, Sequence
from llmada.core import BianXieAdapter
from llama_index.core.extractors import (
    TitleExtractor,
    QuestionsAnsweredExtractor,
)
from llama_index.core.extractors import BaseExtractor
from llama_index.core.schema import BaseNode

from pydantic import ConfigDict



class ExtractorType(Enum):
    """ extra """
    TITLE_EXTRACTOR = 'TitleExtractor'
    QUESTION_ANSWERED_EXTRACTOR = 'QuestionsAnsweredExtractor'
    CUSTOM_KEYWORD_EXTRACTOR = "CustomKeywordExtractor"
    DEDAO_JYRK_TITLE_EXTRACTOR = "DeDaoJYRKTitleExtractor"
    HISTORY_MEMORY_KEYWORD_EXTRACTOR = "HistoryMemoryKeywordExtractor"
    # 添加更多选项

class Extractor:
    """extractor
    """
    def __new__(cls, extra_type: ExtractorType | str) -> Any:

        if isinstance(extra_type,ExtractorType):
            assert extra_type.value in [i.value for i in ExtractorType]
            key_name = extra_type.value
        else:
            assert extra_type in [i.value for i in ExtractorType]
            key_name = extra_type
        instance = None

        if key_name == 'TitleExtractor':
            instance = TitleExtractor()

        elif key_name =="QuestionsAnsweredExtractor":
            instance = QuestionsAnsweredExtractor()

        elif key_name =="CustomKeywordExtractor":
            instance = CustomKeywordExtractor()

        elif key_name =="DeDaoJYRKTitleExtractor":
            instance = DeDaoJYRKTitleExtractor()

        elif key_name =="HistoryMemoryKeywordExtractor":
            instance = HistoryMemoryKeywordExtractor()

        else:
            raise TypeError('Unknown type')

        return instance
