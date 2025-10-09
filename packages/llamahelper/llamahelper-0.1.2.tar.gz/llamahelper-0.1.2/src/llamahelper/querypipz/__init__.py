""" init.py """
import os
from llama_index.core import Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("BIANXIE_API_KEY")
api_base = os.getenv("BIANXIE_BASE")

Settings.llm = OpenAI(model="gpt-4o",api_base=api_base,api_key=api_key)
Settings.embed_model = OpenAIEmbedding(model_name="text-embedding-3-small",api_key=api_key,api_base =api_base)

# Settings.chunk_size = 20000

from querypipz.director import Director
from querypipz.builder import BuilderFactory, BuilderType


from llama_index.core.graph_stores.types import EntityNode, ChunkNode, Relation
from llama_index.core.schema import TextNode

from querypipz.log import Log

Log.reset_level('debug')
#  "faiss-cpu>=1.11.0",