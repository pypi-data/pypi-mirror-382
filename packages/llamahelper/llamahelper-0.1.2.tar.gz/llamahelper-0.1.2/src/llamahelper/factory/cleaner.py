""" cleaner 文本清洗"""
import re
from enum import Enum
from typing import Any
# from promptlibz.core import PromptManager,PromptRepository
from llama_index.core.schema import TransformComponent
from llmada.core import BianXieAdapter
from llama_index.core import Document
# from llama_index.core.node_parser import SimpleNodeParser
from llamahelper.log import Log
logger = Log.logger


class DeDaoCleaner(TransformComponent):
    """专为得到设计的清理类

    Args:
        TransformComponent (_type_): _description_
    """
    def __call__(self, nodes, **kwargs):
        repository = PromptRepository()
        manager = PromptManager(repository)
        prompt = manager.get_prompt("DedaoExtract")

        bx = BianXieAdapter()
        # prompt = Templates(TemplateType.DedaoExtract)
        # bx = GoogleAdapter("AIzaSyBH4ut1plgB95fEiBlBXq1S-VrdYY5xPU4")
        for node in nodes:
            result = bx.product(prompt.format(text = node.text))
            node.set_content(self._extract_n_code(result))
        return nodes

    def _extract_n_code(self,text: str)->str:
        """从文本中提取python代码

        Args:
            text (str): 输入的文本。

        Returns:
            str: 提取出的python文本
        """
        pattern = r'```原文摘抄([\s\S]*?)```'
        matches = re.findall(pattern, text)
        return matches[0]
    
class ExtractConceptCleaner(TransformComponent):
    """专为得到设计的清理类

    Args:
        TransformComponent (_type_): _description_
    """
    def __call__(self, nodes, **kwargs):

        prompt = """
**优化的提示词模板：**

```memory
<Concept: <The name of the specific personal concept, e.g., 黄英杰>>

---
<Description: <A description of the concept, including identifying information like name, relationships, or roles.>>

---
<Event: <Specific events, interactions, or details related to the concept mentioned in the conversation. Include relevant locations if mentioned.>>
```

**优化思考：**

1.  **聚焦个人差异性概念：** 明确指示只提取“有别于常识的个人差异性概念”，这自然会将重点放在人物（及其独特的经历和关系）和特定地点上，排除普遍性概念。
2.  **信息汇集：** 模板通过 `<Concept>`, `<Description>`, 和 `<Event>` 三个部分，强制将关于同一概念的不同信息（名字、描述、相关事件）聚合在一起，满足了信息汇集的要求。
3.  **对话提取：** 提示词任务本身就是基于对话进行的提取，因此模板是为从对话中提取信息而设计的。
4.  **特定格式：** 模板严格遵循了要求的输出格式。
5.  **清晰的指令：** 在实际使用时，会进一步补充指令，明确说明提取范围（人物为主，地点辅之），以及对“有别于常识”的理解（例如，一个普通的朋友名字不是特异概念，但一个特定职业或经历的朋友就是）。

{chat_history}
"""
        bx = BianXieAdapter()
        memr2 = []
        for node in nodes:
            result = bx.product(prompt.format(chat_history = node.text))
            memorys = self._extract_n_memory(result)
            memr = []
            for memory in memorys:
                memr.append(Document(text = self._extract_concept(memory),metadata = {"docs":memory}))
            memr2.extend(memr)

        return memr2

    def _extract_concept(self,text: str)->str:
        """从文本中提取python代码

        Args:
            text (str): 输入的文本。

        Returns:
            str: 提取出的python文本
        """
        pattern = r'<Concept: ([\s\S]*?)>'
        matches = re.findall(pattern, text)
        return matches[0]

    def _extract_n_memory(self,text: str)->str:
        """从文本中提取python代码

        Args:
            text (str): 输入的文本。

        Returns:
            str: 提取出的python文本
        """
        pattern = r'```memory([\s\S]*?)```'
        matches = re.findall(pattern, text)
        return matches

class ExtractEvent1Cleaner(TransformComponent):
    """专为得到设计的清理类

    Args:
        TransformComponent (_type_): _description_
    """
    def __call__(self, nodes, **kwargs):

        prompt = """
**优化的提示词模板：**

```memory
<Concept: <The name of the specific personal concept, e.g., 黄英杰>>

---
<Description: <A description of the event .>>

```

**优化思考：**

1.  **聚焦个人差异性概念：** 明确指示只提取“有别于常识的个人差异性概念”，这自然会将重点放在人物（及其独特的经历和关系）和特定地点上，排除普遍性概念。
2.  **信息汇集：** 模板通过 `<Concept>`, `<Description>`, 两个部分，Concept 重点强调事件,即概念与概念间发生的关系,多以简单句为多, Description则是对发生事件的描述 。
3.  **对话提取：** 提示词任务本身就是基于对话进行的提取，因此模板是为从对话中提取信息而设计的。
4.  **特定格式：** 模板严格遵循了要求的输出格式。

{chat_history}
"""
        bx = BianXieAdapter()
        memr2 = []
        for node in nodes:
            result = bx.product(prompt.format(chat_history = node.text))
            memorys = self._extract_n_memory(result)
            memr = []
            for memory in memorys:
                memr.append(Document(text = self._extract_concept(memory),metadata = {"docs":memory}))
            memr2.extend(memr)

        return memr2

    def _extract_concept(self,text: str)->str:
        """从文本中提取python代码

        Args:
            text (str): 输入的文本。

        Returns:
            str: 提取出的python文本
        """
        pattern = r'<Concept: ([\s\S]*?)>'
        matches = re.findall(pattern, text)
        return matches[0]

    def _extract_n_memory(self,text: str)->str:
        """从文本中提取python代码

        Args:
            text (str): 输入的文本。

        Returns:
            str: 提取出的python文本
        """
        pattern = r'```memory([\s\S]*?)```'
        matches = re.findall(pattern, text)
        return matches



class ChatHistoryMemoryCleaner(TransformComponent):
    """专为得到设计的清理类

    Args:
        TransformComponent (_type_): _description_
    """
    def __call__(self, nodes, **kwargs):
        text = nodes[0].text
        assert isinstance(text,str)
        logger.debug(f'text: {text}')
        conversation = self._parse_conversation(text)
        logger.debug(f'conversation: {conversation}')
        a = [f"user: {conversation_i.get('user')},\nassistant: {conversation_i.get('assistant')}" for conversation_i in conversation]
        
        docs = []

        if len(a)>=2:
            docs.append(Document(text = a[0],metadata = {'docs':     a[0]+a[1]},excluded_embed_metadata_keys=['docs']))
            docs.append(Document(text = a[len(a)-1],metadata = {'docs':a[len(a)-2]+a[len(a)-1]},excluded_embed_metadata_keys=['docs']))
            for i in range(len(a)-2):
                # print(i,i+1,i+2)
                docs.append(Document(text = a[i+1],metadata = {'docs':a[i]+a[i+1] + a[i+2]},excluded_embed_metadata_keys=['docs']))
        else:
            docs.append(Document(text = a[0],metadata = {'docs': a[0]},excluded_embed_metadata_keys=['docs']))
        return docs

    def _parse_conversation(self,text):
        # 定义匹配 user 和 assistant 对话的正则表达式
        # (user|assistant):  匹配 "user:" 或 "assistant:"
        # ([\s\S]*?)        匹配后面的任意字符（包括换行符），非贪婪模式
        # (?=\n(user|assistant):|$)  正向先行断言，确保匹配到下一个 "user:" 或 "assistant:"
        #                              或者字符串的结尾，这样可以正确地分割每个对话块
        pattern = re.compile(r'(user|assistant):\s*([\s\S]*?)(?=\n(user|assistant):|$)')

        matches = pattern.finditer(text)
        
        conversation_list = []
        current_pair = {}

        for match in matches:
            speaker = match.group(1)
            content = match.group(2).strip() # .strip() 去除内容前后可能存在的空白符

            if speaker == "user":
                # 如果当前已经有 user，说明上一个 pair 已经结束，将上一个 pair 加入列表
                # （这种情况通常不会发生，因为我们是按顺序处理的，user: 后面是 assistant:）
                # 但是为了健壮性，可以加上判断
                if "user" in current_pair:
                    conversation_list.append(current_pair)
                    current_pair = {} # 重置
                current_pair["user"] = content
            elif speaker == "assistant":
                # 确保 assistant 前面有对应的 user
                if "user" in current_pair:
                    current_pair["assistant"] = content
                    conversation_list.append(current_pair)
                    current_pair = {} # 清空，准备下一个对话对
                else:
                    # 这种情况下，assistant 出现但前面没有 user，可能数据格式有问题，或者第一个就是 assistant
                    # 这里可以根据需求选择是忽略还是报错
                    print(f"Warning: Assistant response found without a preceding user query: '{content}'")
                    # 如果你想将这种不成对的 assistant 也作为一个独立的条目，可以这样处理：
                    # conversation_list.append({"assistant": content})

        # 处理最后一个可能不成对的 user (如果文本以 user 结尾)
        if current_pair and "user" in current_pair and "assistant" not in current_pair:
            conversation_list.append(current_pair)

        return conversation_list

class ExcludedEmbedMetadataCleaner(TransformComponent):
    """专为得到设计的清理类

    Args:
        TransformComponent (_type_): _description_
    """
    def __call__(self, nodes, **kwargs):
        for node in nodes:
            # 这样设置确保只有text被用于embedding
            node.excluded_embed_metadata_keys = list(node.metadata.keys())
            # node.excluded_llm_metadata_keys
        return nodes
    


class CleanerType(Enum):
    """types
    """
    DE_DAO_CLEANER = 'DeDaoCleaner'
    EXTRACT_CONCEPT_CLEARER = "ExtractConceptCleaner"
    EXCLUDED_EMBED_METADATA_CLEARER = "ExcludedEmbedMetadataCleaner"
    ExtractEvent1Cleaner = "ExtractEvent1Cleaner"
    ChatHistoryMemoryCleaner = "ChatHistoryMemoryCleaner"
    # 添加更多选项

class Cleaner:
    """文本清洗
    """
    def __new__(cls, clean_type: CleanerType | str) -> Any:
        if isinstance(clean_type,CleanerType):
            assert clean_type.value in [i.value for i in CleanerType]
            key_name = clean_type.value
        else:
            assert clean_type in [i.value for i in CleanerType]
            key_name = clean_type
        instance = None

        if key_name == 'DeDaoCleaner':
            instance = DeDaoCleaner()

        elif key_name == 'ExcludedEmbedMetadataCleaner': # running
            instance = ExcludedEmbedMetadataCleaner()

        elif key_name == "ChatHistoryMemoryCleaner": # running
            instance = ChatHistoryMemoryCleaner()

        elif key_name == 'ExtractConceptCleaner': # running
            instance = ExtractConceptCleaner()

        elif key_name == "ExtractEvent1Cleaner":
            instance = ExtractEvent1Cleaner()


        else:
            raise TypeError('Unknown type')

        return instance
