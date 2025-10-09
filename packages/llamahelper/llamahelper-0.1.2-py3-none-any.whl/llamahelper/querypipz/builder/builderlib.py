""" builderlib """
import os
import types
from dotenv import load_dotenv
from llama_index.llms.openai import OpenAI
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core import Settings, Document
from llama_index.core import StorageContext,SimpleDirectoryReader

from querypipz.abc_ import QueryBuilder
from querypipz.queryer import Queryer

from querypipz.factory import (
    GraphExtractor,
    GraphExtractorType,
    Embedding,
    EmbeddingType,
    Extractor,
    ExtractorType,
    Cleaner,
    CleanerType,
    Splitter,
    SplitterType,
    Reader,
    ReaderType,
    VectorStore,
    VectorStoreType,
    GraphStore,
    GraphStoreType,
    Retriver,
    RetriverType,
    LLMFactory,
    LLMType,
    )


load_dotenv()

api_key = os.getenv("BIANXIE_API_KEY")
api_base = os.getenv("BIANXIE_BASE")

class BaseQueryBuilder(QueryBuilder):
    """ base """
    def __init__(self,persist_path='/Users/zhaoxuefeng/GitHub/obsidian/知识库/Base'): # 这里设定知识库的本地存储位置
        self.query = Queryer() # 固定
        self.query.persist_path = persist_path # 固定

    def set_llm(self):
        """设定大模型等基础参数
        """
        # Settings.llm = OpenAI(model="gpt-4.1",api_base=api_base,api_key=api_key)
        # Settings.embed_model = OpenAIEmbedding(model_name="text-embedding-3-small",api_key=api_key,api_base =api_base)
        # Settings.chunk_size = 20000

    def build_reader(self,file_path:str = None):
        """_summary_
        """
        file_path= file_path or '/Users/zhaoxuefeng/GitHub/obsidian/工作/日记'
        self.query.reader = SimpleDirectoryReader(
                input_dir=file_path,
                file_extractor = {".md": Reader(ReaderType.CUS_OBSIDIAN_READER)},
                recursive=True,
            )

    def build_ingestion_pipeline(self):
        """_summary_
        """
        self.query.ingestion_pipeline = IngestionPipeline(
            transformations=[
                Splitter(SplitterType.TOKEN_TEXT_SPLITTER),
                Embedding(EmbeddingType.OPENAI_EMBEDDING),
                ],
            docstore=None,
            cache = None
            )

    def build_storage_context(self):
        """_summary_
        self.query.storage_context = StorageContext.from_defaults(
                vector_store=VectorStore(VectorStoreType.FAISS),
            )
        """
        self.query.storage_context = None

    def build_index_type(self):
        """_summary_
        """
        self.query.index_type = "VectorStoreIndex"

    def build_tools(self): # 增加一些特异性的函数, 使用以下方法进行添加
        """_summary_
        """
        self.query.tools = None

    def get_queryer(self):# 默认
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.query
    
    def build_retriver_nest(self):
        """_summary_
        """
        self.query.retriever_nest = None

    def build_query_pipeline(self): # query 可以直接返回query -> 也可以使用queryengine 进行包装
        """ build """
        self.query.query_engine = None

    def build_kg_extractors(self):
        """_summary_
        """
        self.query.kg_extractors = None




class BaseGraphQueryBuilder(BaseQueryBuilder):
    """ base """
    def __init__(self,persist_path='/Users/zhaoxuefeng/GitHub/obsidian/知识库/Base'): # 这里设定知识库的本地存储位置
        self.query = Queryer() # 固定
        self.query.persist_path = persist_path # 固定

    def build_storage_context(self):
        """_summary_
        """
        self.query.storage_context = StorageContext.from_defaults(
                vector_store=VectorStore(VectorStoreType.FAISS),
                property_graph_store=GraphStore(GraphStoreType.NEO4J_GRAPH_STORE),
            )

    def build_index_type(self):
        """_summary_
        """
        self.query.index_type = "PropertyGraphIndex"

    def build_kg_extractors(self):
        """_summary_
        """
        self.query.kg_extractors = [GraphExtractor(GraphExtractorType.SCHEMA_LLM_PATH_EXTRACTOR3)]

    def build_tools(self): # 增加一些特异性的函数, 使用以下方法进行添加
        """_summary_
        """
        def dynamic_method(self, name_path:str):
            return self.index.property_graph_store.save_networkx_graph(name=name_path)
        
        self.query.networkx_tools = dynamic_method.__get__(self.query,Queryer)



##########################################################################################

class SZRSGraphMemoryBuilder(BaseGraphQueryBuilder):
    def __init__(self,persist_path='/Users/zhaoxuefeng/GitHub/obsidian/知识库/SZRSGraphMemory'):
        super().__init__(persist_path = persist_path)

    def set_llm(self):
        Settings.llm = OpenAI(model="gpt-4.1-mini-2025-04-14",api_base=api_base,api_key=api_key)

    def build_reader(self,file_path:str = None):
        self.query.reader = None

    def build_ingestion_pipeline(self):
        self.query.ingestion_pipeline = IngestionPipeline(
            transformations=[
                Splitter(SplitterType.SIMPLE,chunk_size = 1024),
                Cleaner(CleanerType.EXCLUDED_EMBED_METADATA_CLEARER)
                ]
            )
    def build_kg_extractors(self):
        """_summary_
        """
        self.query.kg_extractors = [GraphExtractor(GraphExtractorType.SCHEMA_LLM_PATH_EXTRACTOR3)]


class ChatHistoryMemoryBuilder_V3(BaseQueryBuilder):
    def __init__(self,persist_path='/Users/zhaoxuefeng/GitHub/obsidian/知识库/HistoryMemory_3'):
        super().__init__(persist_path = persist_path)

    def set_llm(self):
        Settings.llm = LLMFactory(LLMType.BIANXIELLM,model_name="gemini-2.5-flash-preview-05-20-nothinking")

    def build_reader(self,file_path:str = None):
        self.query.reader = None

    def build_ingestion_pipeline(self):
        self.query.ingestion_pipeline = IngestionPipeline(
            transformations=[
                Cleaner(CleanerType.ChatHistoryMemoryCleaner),
                # Extractor(ExtractorType.HISTORY_MEMORY_KEYWORD_EXTRACTOR),
                # Embedding(EmbeddingType.SIMILARITY_TEXT_3L_EMBEDDING),
                ]
            )


class ChatHistoryMemoryBuilder(BaseQueryBuilder):
    def __init__(self,persist_path='/Users/zhaoxuefeng/GitHub/obsidian/知识库/HistoryMemory_2'):
        super().__init__(persist_path = persist_path)

    def set_llm(self):
        Settings.llm = LLMFactory(LLMType.BIANXIELLM,model_name="gemini-2.5-flash-preview-05-20-nothinking")
        # Settings.llm = OpenAI(model="gpt-4.1-mini-2025-04-14",api_base=api_base,api_key=api_key)

    def build_reader(self,file_path:str = None):
        self.query.reader = None

    def build_ingestion_pipeline(self):
        self.query.ingestion_pipeline = IngestionPipeline(
            transformations=[
                Cleaner(CleanerType.ChatHistoryMemoryCleaner),
                # Extractor(ExtractorType.HISTORY_MEMORY_KEYWORD_EXTRACTOR),
                # Embedding(EmbeddingType.SIMILARITY_TEXT_3L_EMBEDDING),
                ]
            )

class ChatHistoryMemoryBuilder_old(BaseQueryBuilder):
    def __init__(self,persist_path='/Users/zhaoxuefeng/GitHub/obsidian/知识库/HistoryMemory'):
        super().__init__(persist_path = persist_path)

    def set_llm(self):
        Settings.llm = OpenAI(model="gpt-4.1-mini-2025-04-14",api_base=api_base,api_key=api_key)

    def build_reader(self,file_path:str = None):
        self.query.reader = None

    def build_ingestion_pipeline(self):
        self.query.ingestion_pipeline = IngestionPipeline(
            transformations=[
                Cleaner(CleanerType.ChatHistoryMemoryCleaner),
                # Extractor(ExtractorType.HISTORY_MEMORY_KEYWORD_EXTRACTOR),
                # Embedding(EmbeddingType.SIMILARITY_TEXT_3L_EMBEDDING),
                ]
            )


class JYRKArticleBuilder(BaseQueryBuilder):
    """ dedao jyrk 6 builder """
    def __init__(self,persist_path='/Users/zhaoxuefeng/GitHub/obsidian/知识库/JYRK'):
        super().__init__(persist_path = persist_path)

    def set_llm(self):
        Settings.llm = OpenAI(model="gemini-2.5-flash-preview-04-17-nothinking",api_base=api_key,
                              api_key=api_base)

    def build_reader(self,file_path:str = None):
        self.query.reader = SimpleDirectoryReader(
            input_dir=file_path,
            file_extractor = {".pdf": Reader(ReaderType.PDF_FILE_READER)},
            recursive=True,
            exclude=["*.mp3","*.MP3"],
            )

    def build_ingestion_pipeline(self):
        self.query.ingestion_pipeline = IngestionPipeline(
            transformations=[
                Cleaner(CleanerType.DE_DAO_CLEANER),
                Splitter(SplitterType.DEDAO_JYRK_TEXT_SPLITTER),
                Extractor(ExtractorType.DEDAO_JYRK_TITLE_EXTRACTOR),
                Embedding(EmbeddingType.OPENAI_EMBEDDING),
                ],
            )


class ObsidianBuilder(BaseQueryBuilder):
    """ obsidian habit builder """
    def __init__(self,persist_path='/Users/zhaoxuefeng/GitHub/obsidian/知识库/Obsidian'):
        super().__init__(persist_path = persist_path)

    def build_reader(self,file_path:str = None):
        self.query.reader = SimpleDirectoryReader(
                input_dir=file_path,
                file_extractor = {".md": Reader(ReaderType.CUS_OBSIDIAN_READER)},
                recursive=True,
            )
