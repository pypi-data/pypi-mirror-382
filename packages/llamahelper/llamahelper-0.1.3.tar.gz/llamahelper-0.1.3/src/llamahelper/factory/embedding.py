""" embedding """
from enum import Enum
import os
from typing import Any
from llama_index.core import Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("BIANXIE_API_KEY")
api_base = os.getenv("BIANXIE_BASE")


from typing import Any, List

from llama_index.core.bridge.pydantic import PrivateAttr
from llama_index.core.embeddings import BaseEmbedding
import os

from volcenginesdkarkruntime import Ark


class VolcanoEmbedding(BaseEmbedding):
    _model = PrivateAttr()
    _ark_client = PrivateAttr()
    _encoding_format = PrivateAttr()

    def __init__(
        self,
        model_name: str = "doubao-embedding-text-240715",
        api_key: str = "",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._ark_client = Ark(api_key=api_key)
        self._model = model_name
        self._encoding_format = "float"
    @classmethod
    def class_name(cls) -> str:
        return "ark"
    
    def _get_query_embedding(self, query: str) -> List[float]:
        """
        获取查询字符串的 embedding。
        通常查询和文档使用相同的 embedding 模型。
        """
        
        resp = self._ark_models.embeddings.create(
            model=self._model,
            input=[query],
            encoding_format=self._encoding_format,
        )
        return resp.data[0].embedding

    def _get_text_embedding(self, text: str) -> List[float]:
        """
        获取单个文档字符串的 embedding。
        """
        resp = self._ark_models.embeddings.create(
            model=self._model,
            input=[query],
            encoding_format=self._encoding_format,
        )
        return resp.data[0].embedding

    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        批量获取文档字符串的 embedding。
        如果你的火山模型支持批量推理，强烈建议实现此方法以提高效率。
        否则，它可以简单地循环调用 _get_text_embedding。
        """
        resp = self._ark_models.embeddings.create(
            model=self._model,
            input=texts,
            encoding_format=self._encoding_format,
        )
        return [i.embedding for i in resp.data]

    async def _aget_query_embedding(self, query: str) -> List[float]:
        return self._get_query_embedding(query)

    async def _aget_text_embedding(self, text: str) -> List[float]:
        return self._get_text_embedding(text)




class EmbeddingType(Enum):
    """enum
    """
    DEFAULT_EMBEDDING = "DefaultEmbedding"
    OPENAI_EMBEDDING = 'OpenAIEmbedding'
    SIMILARITY_TEXT_3S_EMBEDDING = "Similaritytext3sEmbedding"
    SIMILARITY_TEXT_3L_EMBEDDING = "Similaritytext3lEmbedding"
    SEARCH_TEXT_3S_EMBEDDING = "Searchtext3sEmbedding"
    SEARCH_TEXT_3L_EMBEDDING = "Searchtext3lEmbedding"

    # 添加更多选项

class EmbeddingFactory:
    """embedding 方案
    index._embed_model.get_agg_embedding_from_queries(['朱彦青','cc'])   对一组（或多个）相关的查询字符串生成一个聚合的嵌入向量
    index._embed_model.get_text_embedding('朱彦青')    对一个字符串进行词向量嵌入

    """
    def __new__(cls, emb_type: EmbeddingType | str) -> Any:
        if isinstance(emb_type,EmbeddingType):
            assert emb_type.value in [i.value for i in EmbeddingType]
            key_name = emb_type.value
        else:
            assert emb_type in [i.value for i in EmbeddingType]
            key_name = emb_type

        instance = None

        if key_name == 'DefaultEmbedding':
            instance = Settings.embed_model

        elif key_name == 'Similaritytext3sEmbedding':
            instance = OpenAIEmbedding(
                 mode='similarity', #text_search
                 model='text-embedding-3-small',
                 api_base=api_base,
                 api_key=api_key)

        elif key_name == 'Similaritytext3lEmbedding':
            instance = OpenAIEmbedding(
                 mode='similarity', #text_search
                 model='text-embedding-3-large',
                 api_base=api_base,
                 api_key=api_key)

        elif key_name == 'Searchtext3sEmbedding':
            instance = OpenAIEmbedding(
                 mode='text_search',
                 model='text-embedding-3-small',
                 api_base=api_base,
                 api_key=api_key)

        elif key_name == 'Searchtext3lEmbedding':
            instance = OpenAIEmbedding(
                 mode='text_search',
                 model='text-embedding-3-large',
                 api_base=api_base,
                 api_key=api_key)


        elif key_name == 'OpenAIEmbedding':
            instance = OpenAIEmbedding(api_base=api_base,
                                       api_key=api_key)

        else:
            raise TypeError('Unknown type')

        return instance
