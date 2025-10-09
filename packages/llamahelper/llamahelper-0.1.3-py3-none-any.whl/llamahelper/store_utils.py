""" store connect """
import os
from pinecone import Pinecone
from pinecone import ServerlessSpec
from pinecone.data.index import Index
from llama_index.core import StorageContext
from llama_index.vector_stores.pinecone import PineconeVectorStore

import redis


class Pineconer():
    """pinecone connecter
    """
    def __init__(self,api_key = None):
        self.api_key = api_key or os.getenv("PINECONE_API_KEY")
        self.pc = Pinecone(api_key=self.api_key)

    def create(self,index_name:str):
        """ create """
        self.pc.create_index(
            index_name,#"api-documents-index",
            dimension=1536, # 维度1536
            metric="euclidean",#欧式空间 "cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )

    def load(self)->Index:
        """ load """
        pinecone_index = self.pc.Index("api-documents-index")
        return pinecone_index

    def get_storage(self,pinecone_index:Index)->StorageContext:
        """ get store"""
        vector_store = PineconeVectorStore(pinecone_index=pinecone_index,namespace = "test1")
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        return storage_context

redis_client = redis.Redis.from_url("redis://localhost:6379")
