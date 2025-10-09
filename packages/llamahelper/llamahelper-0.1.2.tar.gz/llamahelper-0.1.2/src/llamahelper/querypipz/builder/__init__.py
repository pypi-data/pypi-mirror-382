""" builder """
from enum import Enum
from typing import Any
from .builderlib import (
    SZRSGraphMemoryBuilder,
    ChatHistoryMemoryBuilder,
    ChatHistoryMemoryBuilder_V3,
    JYRKArticleBuilder,
    ObsidianBuilder
)


class BuilderType(Enum):
    """构造者清单

    Args:
        Enum (_type_): 选择构造者
    """
    SZRS_GRAPH_MEMORY_BUILDER = 'SZRSGraphMemoryBuilder'
    CHAT_HISTORY_MEMORY_BUILDER = "ChatHistoryMemoryBuilder"
    CHAT_HISTORY_MEMORY_BUILDER_V3 = "ChatHistoryMemoryBuilder_V3"
    JYRK_ARTICLE_BUILDER = "JYRKArticleBuilder"
    OBSIDIAN_BUILDER = "ObsidianBuilder"
    # 添加更多选项

class BuilderFactory:
    """构造者工厂

    Raises:
        ValueError: _description_

    Returns:
        builder: 构造者
    """
    _builders = {
        BuilderType.SZRS_GRAPH_MEMORY_BUILDER: SZRSGraphMemoryBuilder,
        BuilderType.CHAT_HISTORY_MEMORY_BUILDER: ChatHistoryMemoryBuilder,
        BuilderType.CHAT_HISTORY_MEMORY_BUILDER_V3: ChatHistoryMemoryBuilder_V3,
        BuilderType.JYRK_ARTICLE_BUILDER: JYRKArticleBuilder,
        BuilderType.OBSIDIAN_BUILDER: ObsidianBuilder,
    }

    def __new__(cls, builder_type: BuilderType,persist_path=None) -> Any:
        if builder_type not in cls._builders:
            raise ValueError(f"Unknown builder type: {builder_type}")
        builder_class = cls._builders[builder_type]
        if persist_path:
            instance = builder_class(persist_path = persist_path)
        else:
            instance = builder_class()
        return instance
