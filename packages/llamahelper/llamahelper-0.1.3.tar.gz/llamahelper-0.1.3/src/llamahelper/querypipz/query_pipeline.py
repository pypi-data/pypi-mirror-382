# TODO  
from enum import Enum
from typing import List, Any

from llama_index.core.query_engine.custom import CustomQueryEngine
from llama_index.core.query_engine import RetrieverQueryEngine


# class PythonQueryEngine(CustomQueryEngine):
#     """RAG String Query Engine."""

#     retriever: BaseRetriever
#     response_synthesizer: BaseSynthesizer
#     llm: OpenAI
#     qa_prompt: PromptTemplate
#     stream:bool

#     def custom_query(self, query_str: str):
#         # custom_query(query_str: str) -> STR_OR_RESPONSE_TYPE
#         # acustom_query(query_str: str) -> STR_OR_RESPONSE_TYPE

#         queries = query_str.split('&')
#         nodes = []
#         for query_str in queries:
#             nodes += self.retriever.retrieve(query_str)
#         # nodes = self.retriever.retrieve(query_str)
#         print(query_str,'query_str')
#         context_str = "\n\n".join([n.node.get_metadata_str() for n in nodes])
#         if self.stream:
#             response = self.llm.stream_complete(
#                 qa_prompt.format(safe_code=context_str, prompt=query_str)
#             )

#             def response_gen():
#                 i = [0]
#                 for r in response:
#                     i.append(len(str(r)))
#                     yield str(r)[i[-2]:]

#             return StreamingResponse(response_gen=response_gen(),source_nodes=nodes)
#         else:
#             response = self.llm.complete(qa_prompt.format(safe_code=context_str, prompt=query_str))
    
#             response_obj = self.response_synthesizer.synthesize(response.text, nodes)
#             return Response(response=response.text,source_nodes=nodes) # TODO 增加metadata

"""

    # 具体生成器
class QueryBuilder3(QueryBuilder):
    '''

    '''

    def get_query(self):
        # 例如：
            # instance = AnotherClass(param1=value1, param2=value2)
        
        
        retriever = index.as_retriever(similarity_top_k=similarity_top_k)
        query_engine = PythonQueryEngine(
                retriever=retriever,
                response_synthesizer=get_response_synthesizer(response_mode="compact"),
                llm=Settings.llm,
                qa_prompt=qa_prompt,
                stream = True,
            )

        return query_engine
"""

from llama_index.core.query_engine import CustomQueryEngine
from llama_index.llms.openai import OpenAI
from llama_index.core import PromptTemplate

from toolsz.dev import AutoAPIMD

class APIQueryEngine(CustomQueryEngine):
    """RAG String Query Engine."""

    # retriever: BaseRetriever
    # response_synthesizer: BaseSynthesizer
    llm: OpenAI
    qa_prompt: PromptTemplate
    input_file: str
    def custom_query(self, query_str: str):
        qa_prompt = PromptTemplate(
    "API文档信息如下.\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "Given the context information and not prior knowledge, "
    "answer the query.\n"
    "Query: {query_str}\n"
    "Answer: "
)
        context_str = AutoAPIMD().generate_api_docs(self.input_file, 'api_documentation_mermaidz.md')

        response = self.llm.complete(
            qa_prompt.format(context_str=context_str, query_str=query_str)
        )

        return str(response)


class QueryType(Enum):
    Simple = 'Simple'
    Simple2 = 'Simple2'
    # 添加更多选项

class QueryPipeline:
    def __new__(cls, type: QueryType,custom_retriever) -> Any:
        assert type.value in [i.value for i in QueryType]
        instance = None

        if type.value == 'Simple':

            from llama_index.core import get_response_synthesizer
            response_synthesizer = get_response_synthesizer()
            # instance = SomeClass(param1=value1, param2=value2)
            instance = RetrieverQueryEngine(
                retriever=custom_retriever,
                response_synthesizer=response_synthesizer,
            )
        elif type.value == 'APIQuery':
            instance = APIQueryEngine(
                qa_prompt=qa_prompt,
                llm = Settings.llm,
                input_file = '/Users/zhaoxuefeng/GitHub/llmada/src/llmada/core.py'
            )


        elif type.value == 'Simple2':
            query_engine2 = SubQuestionQueryEngine.from_defaults(
                query_engine_tools=query_engine_tools,
                use_async=True,
            )
        
        elif type.value == 'Simple2':
                
            # instance = AnotherClass(param1=value1, param2=value2)
            pass
            # query_engine = RetrieverQueryEngine(
            #     retriever=self.query.retriver,
            #     response_synthesizer=response_synthesizer,
            #     node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.7)],
            # )

        else:
            raise TypeError('Unknown type')

        return instance

