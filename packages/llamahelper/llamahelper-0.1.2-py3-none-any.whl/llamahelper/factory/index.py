""" agent """
from enum import Enum
from typing import List, Any
from llama_index.core.tools import FunctionTool
from llama_index.core.agent.workflow import FunctionAgent, ReActAgent
from llama_index.core import Settings

class IndexType(Enum):
    """ enum """
    REACT_AGENT = 'ReactAgent'
    FUNCTION_AGENT = 'FunctionAgent'
    # 添加更多选项

class IndexFactory:
    """ factory """
    def __new__(cls, agent_type: IndexType | str,
                tools:List[FunctionTool] = None,
                tools_retriver = None,
                ) -> Any:
        if isinstance(agent_type,IndexType):
            assert agent_type.value in [i.value for i in IndexType]
            key_name = agent_type.value
        else:
            assert agent_type in [i.value for i in IndexType]
            key_name = agent_type
        instance = None

        # assert tools | tools_retriver
        assert (tools is not None) or (tools_retriver is not None)
        if key_name == 'ReactAgent':
            instance = ReActAgent(
                    tools = tools,
                    tools_retriver=tools_retriver,
                    llm=Settings.llm,
                    verbose=True,)

        elif key_name == 'FunctionAgent':
            instance = FunctionAgent(
                tools = tools,
                tools_retriver=tools_retriver,
                llm=Settings.llm,
                verbose=True,)

        else:
            raise TypeError('Unknown type')

        return instance


""" agent """
from enum import Enum
from typing import List, Any
from llama_index.core.tools import FunctionTool
from llama_index.core.agent.workflow import FunctionAgent, ReActAgent
from llama_index.core import Settings

from llama_index.core.agent.workflow import ToolCallResult, AgentStream

from llama_index.core.agent.workflow import FunctionAgent, ReActAgent
from llama_index.core.workflow import Context
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import FunctionTool



# define an "object" index over these tools
from llama_index.core import VectorStoreIndex
from llama_index.core.objects import ObjectIndex



obj_index = ObjectIndex.from_objects(
    all_tools,
    index_cls=VectorStoreIndex,
    # if we were using an external vector store, we could pass the stroage context and any other kwargs
    # storage_context=storage_context,
    # embed_model=embed_model,
    # ...
)



agent = FunctionAgent(
    tool_retriever=obj_index.as_retriever(similarity_top_k=2),
    llm=OpenAI(model="gpt-4o"),
)

# context to hold the session/state
ctx = Context(agent)



