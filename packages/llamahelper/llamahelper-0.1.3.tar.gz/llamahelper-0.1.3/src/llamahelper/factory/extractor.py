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

class TagExtractor(BaseExtractor):
    """自定义关键词提取器"""
    model_config = ConfigDict(extra='allow')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    async def aextract(self, nodes: Sequence[BaseNode]) -> List[Dict[str, Any]]:
        """异步提取方法"""
        return [self.extract_from_node(node) for node in nodes]

    def extract(self, nodes: Sequence[BaseNode]) -> List[Dict[str, Any]]:
        """同步提取方法"""
        return [self.extract_from_node(node) for node in nodes]

    def extract_from_node(self, node: BaseNode) -> Dict[str, Any]:
        """从单个节点提取信息"""
        docs = node.metadata.get('docs')
        print(docs,'text')
        
        from llmada import BianXieAdapter

        bx = BianXieAdapter()

        result = bx.product(f"""
        从下列文本中提取 Tags 并以列表的形式输出
        {docs}

        输出format:
        ```list_str
        ['河北工程大学', '黄英杰', '伙管会社团']
        ```
        """)
        print(result,'result')
        list_str = self._extract_n_code(result)

        import ast
        lst = ast.literal_eval(list_str)
        print(lst,'lst')
        print(type(lst),'list_type')
        return {
            "tags": lst,
            "vvv": ['aa','bb'],
        }
    
    def _extract_n_code(self,text: str)->str:
        """从文本中提取python代码

        Args:
            text (str): 输入的文本。

        Returns:
            str: 提取出的python文本
        """
        pattern = r'```list_str([\s\S]*?)```'
        matches = re.findall(pattern, text)
        return matches[0]

class CustomKeywordExtractor(BaseExtractor):
    """自定义关键词提取器"""
    model_config = ConfigDict(extra='allow')

    def __init__(self, keywords: List[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.keywords = keywords or [
            "习惯化", "快乐", "痛苦", "幸福感", "满足", 
            "间隔", "集中", "游戏", "度假", "结婚"
        ]

    async def aextract(self, nodes: Sequence[BaseNode]) -> List[Dict[str, Any]]:
        """异步提取方法"""
        return [self.extract_from_node(node) for node in nodes]

    def extract(self, nodes: Sequence[BaseNode]) -> List[Dict[str, Any]]:
        """同步提取方法"""
        return [self.extract_from_node(node) for node in nodes]

    def extract_from_node(self, node: BaseNode) -> Dict[str, Any]:
        """从单个节点提取信息"""
        text = node.get_content()
        print(text,'text')
        # 提取关键词
        found_keywords = []
        for keyword in self.keywords:
            if keyword in text:
                found_keywords.append(keyword)

        # 统计关键词频率
        keyword_freq = {}
        for keyword in found_keywords:
            keyword_freq[keyword] = text.count(keyword)

        # 提取数字信息
        numbers = re.findall(r'\d+', text)

        return {
            "keywords_found": found_keywords,
            "keyword_frequency": keyword_freq,
            "numbers_mentioned": numbers,
            "keyword_density": len(found_keywords) / len(text.split()) if text.split() else 0
        }

class DeDaoJYRKTitleExtractor(BaseExtractor):
    """自定义关键词提取器"""

    model_config = ConfigDict(extra='allow')

    def __init__(self, keywords: List[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.keywords = keywords or [
            "习惯化", "快乐", "痛苦", "幸福感", "满足", 
            "间隔", "集中", "游戏", "度假", "结婚"
        ]

    async def aextract(self, nodes: Sequence[BaseNode]) -> List[Dict[str, Any]]:
        """异步提取方法"""
        return [self.extract_from_node(node) for node in nodes]

    def extract(self, nodes: Sequence[BaseNode]) -> List[Dict[str, Any]]:
        """同步提取方法"""
        return [self.extract_from_node(node) for node in nodes]

    def extract_from_node(self, node: BaseNode) -> Dict[str, Any]:
        """从单个节点提取信息"""
        text = node.get_content()
        # print(text,'text')
        p = text.replace('\n','', 1) if text.startswith('\n') else text
        cal = p.split('\n',1)[0]
        return {
            "titie_cal": cal}

class HistoryMemoryKeywordExtractor(BaseExtractor):
    """自定义关键词提取器"""

    model_config = ConfigDict(extra='allow')

    def __init__(self, keywords: List[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.keywords = keywords or [
            "习惯化", "快乐", "痛苦", "幸福感", "满足", 
            "间隔", "集中", "游戏", "度假", "结婚"
        ]

    async def aextract(self, nodes: Sequence[BaseNode]) -> List[Dict[str, Any]]:
        """异步提取方法"""
        return [self.extract_from_node(node) for node in nodes]

    def extract(self, nodes: Sequence[BaseNode]) -> List[Dict[str, Any]]:
        """同步提取方法"""
        return [self.extract_from_node(node) for node in nodes]

    def extract_from_node(self, node: BaseNode) -> Dict[str, Any]:
        """从单个节点提取信息"""
        text = node.get_content()
        print(text,'text')
        # 提取关键词
        found_keywords = []
        for keyword in self.keywords:
            if keyword in text:
                found_keywords.append(keyword)

        bx = BianXieAdapter()
        result = bx.product(f"""
帮我从下列文本中提取出关键词,并输出
{text}

关键词:
""")
        return {
            "keywords_found": found_keywords,
            "keywords":result,
        }

class ExtractorType(Enum):
    """ extra """
    TITLE_EXTRACTOR = 'TitleExtractor'
    QUESTION_ANSWERED_EXTRACTOR = 'QuestionsAnsweredExtractor'
    CUSTOM_KEYWORD_EXTRACTOR = "CustomKeywordExtractor"
    DEDAO_JYRK_TITLE_EXTRACTOR = "DeDaoJYRKTitleExtractor"
    HISTORY_MEMORY_KEYWORD_EXTRACTOR = "HistoryMemoryKeywordExtractor"
    TAG_EXTRACTOR = "TagExtractor"
    # 添加更多选项

class ExtractorFactory:
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

        elif key_name == "TagExtractor":
            instance = TagExtractor()

        else:
            raise TypeError('Unknown type')

        return instance
