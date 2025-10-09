''' 指挥者与建造者'''
from querypipz.abc_ import QueryBuilder
from querypipz.log import Log
logger = Log.logger
# 指挥者
class Director:
    """指挥者
    """
    def __init__(self, builder:QueryBuilder):
        self.builder = builder

    def construct(self,file_path:str = None):
        """开始建造

        Returns:
            返回queryer: 建造成功的产品
        """
        logger.info("-->set_llm ")
        self.builder.set_llm()
        logger.info("--> build_reader")
        self.builder.build_reader(file_path) # data loader
        logger.info("--> build_ingestion_pipeline")
        self.builder.build_ingestion_pipeline()
        logger.info("--> build_kg_extractors")
        self.builder.build_kg_extractors() # extractor transformers
        logger.info("--> build_storage_context")
        self.builder.build_storage_context()
        logger.info("--> build_index_type")
        self.builder.build_index_type()
        logger.info("--> build_tools")
        self.builder.build_tools()
        logger.info("--> build_retriver_nest")
        self.builder.build_retriver_nest()
        logger.info("-->build_query_pipeline  ")
        self.builder.build_query_pipeline()
        logger.info("-->get_queryer ")
        queryer = self.builder.get_queryer()
        return queryer