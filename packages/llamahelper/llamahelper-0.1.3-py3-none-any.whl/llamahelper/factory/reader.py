"""  Reader 工厂模式 """
import os
from enum import Enum
from typing import List, Any, Dict,Optional
from llama_index.core.readers.base import BaseReader
from llama_index.core import Document
from llama_index.readers.database import DatabaseReader
import pandas as pd
from llamahelper.utils import get_data_from_md, extract_text_from_pdf

class ObsidianReaderCus(BaseReader):
    """_summary_

    Args:
        BaseReader (_type_): _description_
    """
    def load_data(self, file_path: str, extra_info: Optional[Dict] = None) -> List[Document]:
        # 自定义读取逻辑
        with open(file_path, 'r') as file:
            text = file.read()
        data,content = get_data_from_md(text)

        # 使用状态
        status = data.get('编辑状态',None)
        topic = data.get('topic','')
        describe = data.get('describe','')
        creation_date = data.get("creation date",'')
        tags = data.get('tags', [])
        link = data.get('链接','')
        content_cut = content[:6000]
        if len(content_cut) != len(content):
            print(topic,'is too long ***')
        document = Document(text=f"topic: {topic} content: {content}",
                            metadata={"topic":topic,
                                      "status":status,
                                      "creation_date":str(creation_date),
                                      "tags":tags,
                                      "link":link},
                           )
        return [document]

class PDFFileReader(BaseReader):
    """PDF文档读取
    将一个PDF文件完整读取为一个Document
    Args:
        BaseReader (_type_): 
    """
    def load_data(self, file_path: str, extra_info: Optional[Dict] = None) -> List[Document]:
        # 自定义读取逻辑

        text = extract_text_from_pdf(file_path)
        document = Document(text=text,
                            metadata={"topic":'',
                                      "status":'file',
                                      "file_path":file_path,
                                      },
                           )

        # from llama_index.core.schema import TextNode
        # node1 = TextNode(text="<text_chunk>", id_="<node_id>")
        # node2 = TextNode(text="<text_chunk>", id_="<node_id>")
        return [document]

class SimplesReader(BaseReader):
    """_summary_

    Args:
        BaseReader (_type_): _description_
    """

    def load_data(self, file_path: str, extra_info: Optional[Dict] = None) -> List[Document]:
        """ # 自定义读取逻辑 """
        extra_info
        text = extract_text_from_pdf(file_path)
        document = Document(text=text,
                            metadata={"topic":'',
                                      "status":'file',
                                      },
                           )
        return [document]

class TransactionCSVReader(BaseReader):
    """读取CSV

    Args:
        BaseReader (_type_): _description_
    """
    def load_data(self, file_path: str):
        margin = pd.read_csv(file_path)
        documents = []
        for i in margin.groupby('hash.1'):
            documents.append(Document(text = str(i[1].iloc[0].to_dict()),
                                      metadata={'transaction':i[0]}))
        return documents

class BlockCSVReader(BaseReader):
    """_summary_

    Args:
        BaseReader (_type_): _description_
    """
    def load_data(self, file_path: str):
        margin = pd.read_csv(file_path)
        documents = []
        for i in margin.groupby('hash'):
            documents.append(Document(text = str(i[1].to_dict()),metadata={'block':i[0]}))
        return documents



class ReaderType(Enum):
    """_summary_

    Args:
        Enum (_type_): _description_
    """
    CUS_OBSIDIAN_READER = 'ObsidianReaderCus'
    PDF_FILE_READER = "PDFFileReader"
    DATA_BASE_READER = 'DatabaseReader'

class ReaderFactory:
    """_summary_
    """
    def __new__(cls, reader_type: ReaderType | str) -> Any:
        assert reader_type.value in [i.value for i in ReaderType]

        if isinstance(reader_type,ReaderType):
            assert reader_type.value in [i.value for i in ReaderType]
            key_name = reader_type.value
        else:
            assert reader_type in [i.value for i in ReaderType]
            key_name = reader_type
        instance = None

        if key_name == 'ObsidianReaderCus':
            instance = ObsidianReaderCus()
        elif key_name == 'PDFFileReader':
            instance = PDFFileReader()
        elif key_name == 'DatabaseReader':
            # instance = AnotherClass(param1=value1, param2=value2)
            reader = DatabaseReader(
                scheme=os.getenv("DB_SCHEME"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASS"),
                dbname=os.getenv("DB_NAME"),
            )
            instance = reader
            # query = "SELECT * FROM users"
            # documents = reader.load_data(query=query)
        else:
            raise TypeError('Unknown type')

        return instance
