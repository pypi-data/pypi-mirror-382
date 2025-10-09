""" store factory """
from enum import Enum
from typing import Any
import os
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.vector_stores import SimpleVectorStore
from llama_index.core.graph_stores import SimpleGraphStore
# from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.graph_stores.nebula import NebulaPropertyGraphStore
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from llama_index.graph_stores.memgraph import MemgraphPropertyGraphStore
from pinecone import Pinecone
# import faiss
from querypipz.log import Log
logger = Log.logger


class VectorStoreType(Enum):
    """_summary_

    Args:
        Enum (_type_): _description_
    """
    SIMPLE_VECTOR_STORE = 'SimpleVectorStore'
    FAISS = 'FAISS'
    PINECONE = "PINECONE"
    # 添加更多选项

class VectorStore:
    """_summary_
    """
    def __new__(cls, vector_type: VectorStoreType| str) -> Any:

        assert vector_type.value in [i.value for i in VectorStoreType]
        if isinstance(vector_type,VectorStoreType):
            assert vector_type.value in [i.value for i in VectorStoreType]
            key_name = vector_type.value
        else:
            assert vector_type in [i.value for i in VectorStoreType]
            key_name = vector_type
        instance = None

        if key_name == 'SimpleVectorStore':
            logger.info(f'running {key_name}')
            instance = SimpleVectorStore()

        # elif key_name == 'FAISS':
        #     logger.info(f'running {key_name}')
        #     faiss_index = faiss.IndexFlatL2(1536)  # Example dimension
        #     instance = FaissVectorStore(faiss_index=faiss_index)

        elif key_name == 'PINECONE':
            logger.info(f'running {key_name}')
            api_key = os.environ["PINECONE_API_KEY"]
            pc = Pinecone(api_key=api_key)
            pinecone_index = pc.Index("quickstart-index")
            vector_store = PineconeVectorStore(
                                            pinecone_index=pinecone_index, namespace="test_05_14"
                                        )
            instance = vector_store

        else:
            raise KeyError('Unknown type')

        return instance


class DocStoreType(Enum):
    """Docs

    Args:
        Enum (_type_): _description_
    """
    SIMPLE_DOCUMENT_STORE = 'SimpleDocumentStore'
    # Add more options as needed


class DocStore:
    """DocStore
    """
    def __new__(cls, doc_type: DocStoreType | str) -> Any:
        assert doc_type.value in [i.value for i in DocStoreType]

        if isinstance(doc_type,DocStoreType):
            assert doc_type.value in [i.value for i in DocStoreType]
            key_name = doc_type.value
        else:
            assert doc_type in [i.value for i in DocStoreType]
            key_name = doc_type
        instance = None

        if key_name == 'SimpleDocumentStore':
            logger.info(f'running {key_name}')
            instance = SimpleDocumentStore()
        else:
            raise KeyError('Unknown type')

        return instance


class GraphStoreType(Enum):
    """GraphStoreType

    Args:
        Enum (_type_): _description_
    """
    SIMPLE_GRAPH_STORE = 'SimpleGraphStore'
    NEBULA_GRAPH_STORE = 'NebulaGraphStore'
    NEO4J_GRAPH_STORE = 'Neo4jGraphStore'
    MEMGRAPH_GRAPH_STORE = 'MemgraphGraphStore'

class GraphStore:
    """GraphStore
    """
    def __new__(cls, graph_type: GraphStoreType | str) -> Any:

        assert graph_type.value in [i.value for i in GraphStoreType]

        if isinstance(graph_type,GraphStoreType):
            assert graph_type.value in [i.value for i in GraphStoreType]
            key_name = graph_type.value
        else:
            assert graph_type in [i.value for i in GraphStoreType]
            key_name = graph_type
        instance = None

        if key_name == 'SimpleGraphStore':
            logger.info(f'running {key_name}')
            instance = SimpleGraphStore()
        elif key_name == 'NebulaGraphStore':
            logger.info(f'running {key_name}')
            os.environ["NEBULA_USER"] = "root"
            os.environ["NEBULA_PASSWORD"] = "nebula"
            os.environ["NEBULA_ADDRESS"] = "127.0.0.1:9669"
            # Initialize NebulaPropertyGraphStore
            graph_store = NebulaPropertyGraphStore(
                space="llamaindex",
                overwrite=True  # Overwrite existing space if needed
            )
            instance = graph_store

        elif key_name == 'Neo4jGraphStore':
            logger.info(f'running {key_name}')
            graph_store = Neo4jPropertyGraphStore(
                username="neo4j",
                password="ZHF4233613",
                url="bolt://localhost:7687",
            )
            instance = graph_store

        elif key_name == 'MemgraphGraphStore':
            logger.info(f'running {key_name}')
            graph_store = MemgraphPropertyGraphStore(
                username="",# Enter your Memgraph username (default "")
                password="",# Enter your Memgraph password (default "")
                url="",  # Specify the connection URL, e.g., 'bolt://localhost:7687'
            )
            instance = graph_store
        else:
            raise KeyError('Unknown type')

        return instance
