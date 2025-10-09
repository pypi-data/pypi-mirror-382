""" useful tools """
from llama_index.core.workflow import Context
from llama_index.core.tools import QueryEngineTool
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings
from llama_index.embeddings.openai import OpenAIEmbedding
import os

class VisualIndex():
    """visualization Index
    """
    def __init__(self,index):
        self.index = index

    def get_docs_id(self):
        """ get docs ids """
        return list(self.index.docstore.docs.keys())

    def get_documents(self):
        """ get documents """
        return [self.index.docstore.get_document(i) for i in self.get_docs_id()]

    def get_document_by_id(self,doc_id): # 有a功能
        """ get documents by doc_id """
        return self.index.docstore.get_document(doc_id)


class Package():
    """包装工具
    """
    def __init__(self) -> None:
        pass

    @staticmethod
    def package_tool(func):
        """ 包装工具 """
        return FunctionTool.from_defaults(func,name=func.__name__,
                                          return_direct=False, #直接返回 具体定义在Tool_Metadata中
                                          )

    @staticmethod
    def package_querypip2tool(query_engine,name,description):
        """ 将query包装成工具 """
        qenginetools = QueryEngineTool.from_defaults(
                query_engine=query_engine,
                name=name,
                description=description,
                return_direct=False, #直接返回 具体定义在Tool_Metadata中
            )
        return qenginetools


class EasyAgentz():
    """ agent helper"""
    def __init__(self, agent):
        self.agent = agent
        self.ctx = Context(agent)
        self.resp = None

    async def run(self,prompt = "What is 5+3+2"):
        """ 
        运行agent
        """
        self.resp = await self.agent.run(prompt,ctx=self.ctx)
        return str(self.resp)

    def update_prompts(self,react_system_prompt:str):
        """ 更新prompt
        """
        self.agent.update_prompts({"react_header": react_system_prompt})

    def tool_calls(self):
        """ 查询工具调用情况"""
        return self.resp.tool_calls

class EasyIndex():
    """ Index helper"""
    def __init__(self,index):
        """ init """
        self.index = index

    def insert(self,document):
        """ 插入 document """
        self.index.insert(document)



def set_llama_index(api_key: str = None, api_base: str = "https://api.bianxieai.com/v1",model:str="gpt-4o",temperature: float =0.1,
                    llm_config:dict = {},embed_config:dict = {}):
    """初始化

    Args:
        api_key (str): API key for authentication.
        api_base (str): Base URL for the API endpoint.
    """


    api_key=api_key or os.getenv('BIANXIE_API_KEY')

    client = OpenAI(
        model=model,
        api_base=api_base,
        api_key=api_key,
        temperature=temperature,
        **llm_config
    )
    embedding = OpenAIEmbedding(api_base=api_base,api_key=api_key,**embed_config)
    Settings.embed_model = embedding
    Settings.llm = client

