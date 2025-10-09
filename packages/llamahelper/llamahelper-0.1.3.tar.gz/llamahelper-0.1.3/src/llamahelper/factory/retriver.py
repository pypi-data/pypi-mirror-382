""" retriver """
from enum import Enum
from typing import Any
from typing import List
from llama_index.core.objects import ObjectIndex
from llama_index.core import VectorStoreIndex
from llama_index.core.indices.property_graph import (
    LLMSynonymRetriever,
    VectorContextRetriever,
)
from llama_index.core import QueryBundle
from llama_index.core.schema import NodeWithScore
from llama_index.core.retrievers import (
    BaseRetriever,
    VectorIndexRetriever,
    KeywordTableSimpleRetriever,
)
from llama_index.core import VectorStoreIndex
from llama_index.core import Document
from llamahelper.log import Log
logger = Log.logger

class CustomRetriever(BaseRetriever):
    """Custom retriever that performs both semantic search and hybrid search."""

    def __init__(
        self,
        vector_retriever: VectorIndexRetriever,
        keyword_retriever: KeywordTableSimpleRetriever,
        mode: str = "AND",
    ) -> None:
        """Init params."""

        self._vector_retriever = vector_retriever
        self._keyword_retriever = keyword_retriever
        if mode not in ("AND", "OR"):
            raise ValueError("Invalid mode.")
        self._mode = mode
        super().__init__()

    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        """Retrieve nodes given query."""

        vector_nodes = self._vector_retriever.retrieve(query_bundle)
        keyword_nodes = self._keyword_retriever.retrieve(query_bundle)

        vector_ids = {n.node.node_id for n in vector_nodes}
        keyword_ids = {n.node.node_id for n in keyword_nodes}

        combined_dict = {n.node.node_id: n for n in vector_nodes}
        combined_dict.update({n.node.node_id: n for n in keyword_nodes})

        if self._mode == "AND":
            retrieve_ids = vector_ids.intersection(keyword_ids)
        else:
            retrieve_ids = vector_ids.union(keyword_ids)

        retrieve_nodes = [combined_dict[rid] for rid in retrieve_ids]
        return retrieve_nodes


class CustomRetriever2(BaseRetriever):
    """Custom retriever that performs both semantic search and hybrid search."""

    def __init__(
        self,
        # vector_retriever: VectorIndexRetriever,
        # keyword_retriever: KeywordTableSimpleRetriever,
    ) -> None:
        """Init params."""
        self.index = None
        self.title_retriver = None
        self.key_retriver = None
        super().__init__()

    def complex_build(self,index):
        self.index = index
        documents = [self.index.docstore.get_document(i) for i in list(self.index.docstore.docs.keys())]
        title_index = VectorStoreIndex.from_documents([Document(text = doc.text) for doc in documents])
        self.key_retriver = self.index.as_retriever()
        self.title_retriver = title_index.as_retriever()
        

    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        """Retrieve nodes given query."""

        retrieve_nodes = []
        titles = self.title_retriver.retrieve(query_bundle)
        for title_i in titles:
            print(title_i)
            print(type(title_i))
            print(title_i.text,type(title_i.text))
            context = self.key_retriver.retrieve(title_i.text)
            retrieve_nodes.append(context)
        return retrieve_nodes



class RetriverType(Enum):
    """Retriver

    Args:
        Enum (_type_): _description_
    """
    TOOLS_RETRIVER = 'ToolsRetriver'
    GRAPH_LLM_SYNONYM_RETRIEVER = "GraphLLMSynonymRetriever"
    GRAPH_VECTOR_CONTEXT_RETRIEVER = "GraphVectorContextRetriever"
    CustomRetriever = "CustomRetriever"
    CustomRetriever2 = "CustomRetriever2"
    # 添加更多选项


class RetriverFactory:
    """_summary_
    """
    def __new__(cls, retriver_type: RetriverType | str,tools = None,
                property_graph_store = None,**kwargs) -> Any:
        assert retriver_type.value in [i.value for i in RetriverType]

        if isinstance(retriver_type,RetriverType):
            assert retriver_type.value in [i.value for i in RetriverType]
            key_name = retriver_type.value
        else:
            assert retriver_type in [i.value for i in RetriverType]
            key_name = retriver_type
        instance = None

        if key_name == 'ToolsRetriver':
            logger.info(f'running {key_name}')
            obj_index = ObjectIndex.from_objects(tools,index_cls=VectorStoreIndex)
            instance=obj_index.as_retriever(similarity_top_k=2)

        elif key_name == "GraphLLMSynonymRetriever":
            logger.info(f'running {key_name}')
            instance = LLMSynonymRetriever(
                graph_store = property_graph_store,
                include_text=False,
            )
        elif key_name == "GraphVectorContextRetriever":
            logger.info(f'running {key_name}')
            instance = VectorContextRetriever(
                graph_store = property_graph_store,
                include_text=False,
            )

        elif key_name == "CustomRetriever":
            """
            vector_retriever = VectorIndexRetriever(index=vector_index, similarity_top_k=2)
            keyword_retriever = KeywordTableSimpleRetriever(index=keyword_index)
            custom_retriever = CustomRetriever(vector_retriever, keyword_retriever)
            """
            logger.info(f'running {key_name}')
            instance = CustomRetriever(
                **kwargs
            )
        elif key_name == "CustomRetriever2":
            logger.info(f'running {key_name}')
            instance = CustomRetriever2()

        else:
            raise KeyError('Unknown type')
        return instance

    @staticmethod
    def sub_retriver(index,retrievers:list):
        """ set sub retriver"""
        retriever = index.as_retriever(
            sub_retrievers=retrievers
                    )
        return retriever



