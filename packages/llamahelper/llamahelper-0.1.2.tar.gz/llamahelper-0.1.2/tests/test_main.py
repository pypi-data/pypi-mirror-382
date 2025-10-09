from llamahelper.factory import LLMFactory,LLMType

def test_llm():
    llm = LLMFactory(LLMType.BIANXIELLM,
               model_name ="gemini-2.5-flash-preview-05-20-nothinking"
               )
    




def test_agent_react():
    agent = AgentFactory(AgentType.REACT_AGENT)


def test_agent_function():
    agent = AgentFactory(AgentType.FUNCTION_AGENT)





