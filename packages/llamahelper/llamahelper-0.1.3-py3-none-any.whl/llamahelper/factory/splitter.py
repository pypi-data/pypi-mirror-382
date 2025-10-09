""" splitter """
from enum import Enum
import re
from typing import List, Any
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core.node_parser import CodeSplitter


class DeDaoJYRKTextSplitter(SentenceSplitter):
    """ other """
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 100, **kwargs):
        super().__init__(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            **kwargs
        )

    def _split_text(self, text: str, chunk_size: int) -> List[str]:
        """
        _Split incoming text and return chunks with overlap size.

        Has a preference for complete sentences, phrases, and minimal overlap.
        """
        assert isinstance(text,str)
        assert isinstance(chunk_size,int)

        # text : str
        if text == "":
            return [text]

#         with self.callback_manager.event(
#             CBEventType.CHUNKING, payload={EventPayload.CHUNKS: [text]}
#         ) as event:
#             splits = self._split(text, chunk_size)
#             chunks = self._merge(splits, chunk_size)

#             event.on_end(payload={EventPayload.CHUNKS: chunks})
        chunks = text.split('\n\n')
        assert isinstance(chunks,list)
        return chunks

class HistoryMemorySplitter(SentenceSplitter):
    """ historyMemory"""
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 100, **kwargs):
        super().__init__(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            **kwargs
        )

    def split_qa_strings(self,text):
        """
        将包含 user: 和 assistant: 标记的文本拆分成一对一对的问答对字符串。

        Args:
        text: 包含问答对的字符串。

        Returns:
        一个列表，其中每个元素都是一个字符串，包含一个完整的问答对
        （从 user: 开始到其对应的 assistant: 结束）。
        如果存在不成对的 user 或 assistant，它们将被忽略。
        """
        # 使用正则表达式找到所有 user: ... assistant: ... 的完整对
        # non-greedy match for user: content, followed by assistant: and its content
        pattern = re.compile(r"user:.*?assistant:.*?(?=user:|$)", re.S)
        matches = pattern.findall(text)

        qa_strings = []
        for match in matches:
            qa_strings.append(match.strip()) # 将匹配到的完整问答对字符串添加到列表中

        return qa_strings

    def _split_text(self, text: str, chunk_size: int) -> List[str]:
        """
        自定义分割逻辑
        """
        if text == "":
            return [text]

        chunks = self.split_qa_strings(text)
        return chunks

class TestSplitter(SentenceSplitter):
    """ historyMemory"""
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 100, **kwargs):
        super().__init__(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            **kwargs
        )

    def split_qa_strings(self,text) -> List[str]:
        """
        将包含 user: 和 assistant: 标记的文本拆分成一对一对的问答对字符串。

        Args:
        text: 包含问答对的字符串。

        Returns:
        一个列表，其中每个元素都是一个字符串，包含一个完整的问答对
        （从 user: 开始到其对应的 assistant: 结束）。
        如果存在不成对的 user 或 assistant，它们将被忽略。
        """
        return text.split("\n")

    def _split_text(self, text: str, chunk_size: int) -> List[str]:
        """
        自定义分割逻辑
        """
        if text == "":
            return [text]

        chunks = self.split_qa_strings(text)
        return chunks

class SplitterType(Enum):
    """ enum """
    SIMPLE = 'Simple'
    CODE_SPLITTER = 'CodeSplitter'
    TOKEN_TEXT_SPLITTER = "TokenTextSplitter"
    DEDAO_JYRK_TEXT_SPLITTER = "DeDaoJYRKTextSplitter"
    HISTORY_MEMORY_SPLITTER = "HistoryMemorySplitter"
    TEST_SPLITTER = "TestSplitter"
    # 添加更多选项

class SplitterFactory:
    """ splitter """
    def __new__(cls, splitter_type: SplitterType | str,chunk_size = None) -> Any:
        assert splitter_type.value in [i.value for i in SplitterType]

        if isinstance(splitter_type,SplitterType):
            assert splitter_type.value in [i.value for i in SplitterType]
            key_name = splitter_type.value
        else:
            assert splitter_type in [i.value for i in SplitterType]
            key_name = splitter_type
        instance = None

        if key_name == 'Simple':
            instance = SentenceSplitter(chunk_size=chunk_size or 4096, chunk_overlap=50)

        elif key_name == "TestSplitter":
            instance = TestSplitter()

        elif key_name =="DeDaoJYRKTextSplitter":
            instance = DeDaoJYRKTextSplitter()

        elif key_name == 'CodeSplitter':
            instance = CodeSplitter(
                language="python",
                chunk_lines=40,  # lines per chunk
                chunk_lines_overlap=15,  # lines overlap between chunks
                max_chars=1500,  # max chars per chunk
            )

        elif key_name == 'TokenTextSplitter':
            instance = TokenTextSplitter()

        elif key_name == "HistoryMemorySplitter":
            instance = HistoryMemorySplitter()

        else:
            raise TypeError('Unknown type')

        return instance
