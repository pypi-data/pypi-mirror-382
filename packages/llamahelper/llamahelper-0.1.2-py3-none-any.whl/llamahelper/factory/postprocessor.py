""" agent """
from enum import Enum
from llama_index.core.postprocessor import SimilarityPostprocessor

class PostprocessorType(Enum):
    """ enum """
    SimilarityPostprocessor = 'SimilarityPostprocessor'
    # 添加更多选项

class PostprocessorFactory:
    """ factory """
    def __new__(cls, postp_type: PostprocessorType | str) -> Any:
        if isinstance(postp_type,PostprocessorType):
            assert postp_type.value in [i.value for i in PostprocessorType]
            key_name = postp_type.value
        else:
            assert postp_type in [i.value for i in PostprocessorType]
            key_name = postp_type
        instance = None


        if key_name == 'SimilarityPostprocessor':
            instance = SimilarityPostprocessor(similarity_cutoff=0.6)

        else:
            raise TypeError('Unknown type')

        return instance
