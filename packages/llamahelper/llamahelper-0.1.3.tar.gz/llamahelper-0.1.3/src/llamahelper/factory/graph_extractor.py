""" graph_extractor """

from enum import Enum
from typing import Any
from typing import Literal
from llama_index.core.indices.property_graph.transformations import (
    ImplicitPathExtractor,
    SchemaLLMPathExtractor,
    SimpleLLMPathExtractor,
    DynamicLLMPathExtractor,
)
from llama_index.core import Settings
from llama_index.core.graph_stores.types import (
    EntityNode,
    Relation,
    KG_NODES_KEY,
    KG_RELATIONS_KEY,
)
from llama_index.core.schema import BaseNode, TransformComponent


class MyGraphExtractor(TransformComponent):
    """CUSTOM """

    def __call__(
        self, llama_nodes: list[BaseNode], **kwargs
    ) -> list[BaseNode]:
        for llama_node in llama_nodes:
            # be sure to not overwrite existing entities/relations

            existing_nodes = llama_node.metadata.pop(KG_NODES_KEY, [])
            existing_relations = llama_node.metadata.pop(KG_RELATIONS_KEY, [])

            existing_nodes.append(
                EntityNode(
                    name="llama", label="ANIMAL", properties={"key": "val"}
                )
            )
            existing_nodes.append(
                EntityNode(
                    name="index", label="THING", properties={"key": "val"}
                )
            )

            existing_relations.append(
                Relation(
                    label="HAS",
                    source_id="llama",
                    target_id="index",
                    properties={},
                )
            )

            # add back to the metadata

            llama_node.metadata[KG_NODES_KEY] = existing_nodes
            llama_node.metadata[KG_RELATIONS_KEY] = existing_relations

        return llama_nodes

    # optional async method
    # async def acall(self, llama_nodes: list[BaseNode], **kwargs) -> list[BaseNode]:
    #    ...

from llama_index.core.indices.property_graph.utils import (
    default_parse_triplets_fn,
)
from llama_index.core.llms.llm import LLM

from llama_index.core.prompts.default_prompts import (
    DEFAULT_KG_TRIPLET_EXTRACT_PROMPT,
)

import asyncio
from typing import Any, Callable, Optional, Sequence, Union

from llama_index.core.async_utils import run_jobs
from llama_index.core.indices.property_graph.utils import (
    default_parse_triplets_fn,
)
from llama_index.core.graph_stores.types import (
    EntityNode,
    Relation,
    KG_NODES_KEY,
    KG_RELATIONS_KEY,
)
from llama_index.core.llms.llm import LLM
from llama_index.core.prompts import PromptTemplate
from llama_index.core.prompts.default_prompts import (
    DEFAULT_KG_TRIPLET_EXTRACT_PROMPT,
)
from llama_index.core.schema import TransformComponent, BaseNode, MetadataMode

"""
LLM_PATH = > 添加nodes 和 relations 到metadata

text + metadata -> 制作nodes 和relations 
完成以后将metadata 挂载到新的nodes和relations上
"""
class MyGraphExtractor2(SimpleLLMPathExtractor):

    async def _aextract(self, node: BaseNode) -> BaseNode:
        """Extract triples from a node."""
        assert hasattr(node, "text")

        text = node.get_content(metadata_mode=MetadataMode.LLM)

        
        try:
            llm_response = await self.llm.apredict(
                self.extract_prompt,
                text=text,
                max_knowledge_triplets=self.max_paths_per_chunk,
            )
            triples = self.parse_fn(llm_response)
        except ValueError:
            triples = []

        existing_nodes = node.metadata.pop(KG_NODES_KEY, [])
        existing_relations = node.metadata.pop(KG_RELATIONS_KEY, [])

        metadata = node.metadata.copy()
        metadata['type'] = 'concept'
        for subj, rel, obj in triples:
            subj_node = EntityNode(name=subj, properties=metadata)
            obj_node = EntityNode(name=obj, properties=metadata)
            rel_node = Relation(
                label=rel,
                source_id=subj_node.id,
                target_id=obj_node.id,
                properties=metadata,
            )

            existing_nodes.extend([subj_node, obj_node])
            existing_relations.append(rel_node)

        node.metadata[KG_NODES_KEY] = existing_nodes
        node.metadata[KG_RELATIONS_KEY] = existing_relations

        return node



class GraphExtractorType(Enum):
    ''' enum '''
    MY_GRAPH_EXTRACTOR = 'MyGraphExtractor'
    DYNAMIC_LLM_PATH_EXTRACTOR = "DynamicLLMPathExtractor"
    DYNAMIC_LLM_PATH_EXTRACTOR2 = "DynamicLLMPathExtractor2"
    SCHEMA_LLM_PATH_EXTRACTOR = "SchemaLLMPathExtractor"
    SCHEMA_LLM_PATH_EXTRACTOR2 = "SchemaLLMPathExtractor2"
    SCHEMA_LLM_PATH_EXTRACTOR3 = "SchemaLLMPathExtractor3"
    SIMPLE_LLM_PATH_EXTRACTOR = "SimpleLLMPathExtractor"
    IMPLICIT_PATH_EXTRACTOR = "ImplicitPathExtractor"
    # Add more options as needed


class GraphExtractor:
    """ Factory"""
    def __new__(cls, graph_extra_type: GraphExtractorType | str) -> Any:

        assert graph_extra_type.value in [i.value for i in GraphExtractorType]

        if isinstance(graph_extra_type,GraphExtractorType):
            assert graph_extra_type.value in [i.value for i in GraphExtractorType]
            key_name = graph_extra_type.value
        else:
            assert graph_extra_type in [i.value for i in GraphExtractorType]
            key_name = graph_extra_type
        instance = None

        if key_name == 'MyGraphExtractor':
            instance = MyGraphExtractor()

        elif key_name == 'MyGraphExtractor':
            instance = MyGraphExtractor()
        elif key_name == 'MyGraphExtractor':
            instance = MyGraphExtractor()

        elif key_name == 'SimpleLLMPathExtractor':
            instance = SimpleLLMPathExtractor()
        elif key_name == 'ImplicitPathExtractor':
            # 是通过将定义的Node Relations 的对象可以转化为 metadata 的nodes and edges 如果没有定义则跳过
            instance = ImplicitPathExtractor() 

        elif key_name == 'ImplicitPathExtractor2':
            # 是通过将定义的Node Relations 的对象可以转化为 metadata 的nodes and edges 如果没有定义则跳过
            instance = ImplicitPathExtractor2() 
        elif key_name == 'DynamicLLMPathExtractor':
            instance = DynamicLLMPathExtractor(
                        max_triplets_per_chunk=20,
                        num_workers=4,
                        allowed_entity_types=["POLITICIAN", "POLITICAL_PARTY"],
                        allowed_relation_types=["PRESIDENT_OF", "MEMBER_OF"],
                        allowed_relation_props=["description"],
                        allowed_entity_props=["description"],
                        )

        elif key_name == 'DynamicLLMPathExtractor2':
            instance  = DynamicLLMPathExtractor(
                                                max_triplets_per_chunk=20,
                                                num_workers=4,
                                                allowed_entity_types=None,
                                                allowed_relation_types=None,
                                                allowed_relation_props=[],
                                                allowed_entity_props=[],
                                            )
        elif key_name == 'SchemaLLMPathExtractor':
            instance = SchemaLLMPathExtractor(
                                            llm = Settings.llm,
                                            max_triplets_per_chunk=20,
                                            strict=False,
                                            possible_entities=None,
                                            possible_relations=None,
                                            possible_relation_props=[
                                                "extra_description"
                                            ],
                                            possible_entity_props=[
                                                "extra_description"
                                            ],
                                            num_workers=4,
                                            )
        elif key_name == "SchemaLLMPathExtractor2":

            # best practice to use upper-case
            entities = Literal["PERSON", "PLACE", "ORGANIZATION"]
            relations = Literal["HAS", "PART_OF", "WORKED_ON", "WORKED_WITH", "WORKED_AT"]

            # define which entities can have which relations
            validation_schema = {
                "PERSON": ["HAS", "PART_OF", "WORKED_ON", "WORKED_WITH", "WORKED_AT"],
                "PLACE": ["HAS", "PART_OF", "WORKED_AT"],
                "ORGANIZATION": ["HAS", "PART_OF", "WORKED_WITH"],
            }

            instance = SchemaLLMPathExtractor(
                llm=Settings.llm,
                possible_entities=entities,
                possible_relations=relations,
                kg_validation_schema=validation_schema,
                # if false, allows for values outside of the schema
                # useful for using the schema as a suggestion
                strict=True,
            )
        elif key_name == "SchemaLLMPathExtractor3":

            # best practice to use upper-case
            entities = Literal["人物", "地点",]
            relations = Literal["母子", "父子", "亲属", "朋友", "喜欢","归属"]

            # define which entities can have which relations
            validation_schema = {
                "人物": ["母子", "父子", "亲属", "朋友", ],
                "地点": ["归属", "喜欢"],
            }

            instance = SchemaLLMPathExtractor(
                llm=Settings.llm,
                possible_entities=entities,
                possible_relations=relations,
                kg_validation_schema=validation_schema,
                # if false, allows for values outside of the schema
                # useful for using the schema as a suggestion
                strict=True,
            )

        else:
            raise TypeError('Unknown type')

        return instance
