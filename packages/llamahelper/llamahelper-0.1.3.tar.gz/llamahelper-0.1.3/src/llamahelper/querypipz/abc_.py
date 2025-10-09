""" abc """
from typing import Optional
from abc import ABC, abstractmethod
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex


class QueryerABC(ABC):
    """问答

    Args:
        ABC (_type_): query
    """
    def __init__(self):
        self.persist_path = None
        self.reader: Optional[SimpleDirectoryReader] = None
        self.ingestion_pipeline: Optional[IngestionPipeline] = None
        self.kg_extractors = None
        self.storage_context = None
        self.index_type = None
        self.retriever_nest = None
        self.query_nest = None
        self.query_pipeline = None
        self.retriever = None
        self.index: Optional[VectorStoreIndex] = None


    @abstractmethod
    def build(self):
        """ init a RAG query """
        raise NotImplementedError

    @abstractmethod
    def update(self, prompt: str):
        """Update the index"""
        raise NotImplementedError

    @abstractmethod
    def reload(self):
        """ reload a exist RAG query"""
        raise NotImplementedError

    @abstractmethod
    def query(self, prompt: str, similarity_top_k: int = 3):
        """Query the index with prompt"""
        raise NotImplementedError

    @abstractmethod
    def retrieve_search(self, query_text: str, similarity_top_k: int = 5):
        """Retrieve relevant documents"""
        raise NotImplementedError




class QueryBuilder(ABC):
    """QueryBuilder

    Args:
        ABC (_type_): _description_

    Raises:
        NotImplementedError: _description_
        NotImplementedError: _description_
        NotImplementedError: _description_
        NotImplementedError: _description_
        NotImplementedError: _description_
        NotImplementedError: _description_
        NotImplementedError: _description_
        NotImplementedError: _description_
        NotImplementedError: _description_
        NotImplementedError: _description_
    """
    def __init__(self): # 这里设定知识库的本地存储位置
        self.query : QueryerABC = None
        self.query.persist_path : str = ''

    @abstractmethod
    def set_llm(self):
        """Set the language model"""
        raise NotImplementedError

    @abstractmethod
    def build_reader(self,file_path:str = None):
        """Build document reader"""
        raise NotImplementedError

    @abstractmethod
    def build_ingestion_pipeline(self):
        """Build ingestion pipeline"""
        raise NotImplementedError

    @abstractmethod
    def build_kg_extractors(self):
        """Build knowledge graph extractors"""
        raise NotImplementedError

    @abstractmethod
    def build_storage_context(self):
        """Build storage context"""
        raise NotImplementedError

    @abstractmethod
    def build_index_type(self):
        """Build index"""
        raise NotImplementedError

    @abstractmethod
    def build_retriver_nest(self):
        """Build retriever"""
        raise NotImplementedError

    @abstractmethod
    def build_query_pipeline(self):
        """Build query pipeline"""
        raise NotImplementedError

    @abstractmethod
    def build_tools(self):
        """Build tools"""
        raise NotImplementedError

    @abstractmethod
    def get_queryer(self):
        """Get the built queryer"""
        raise NotImplementedError
