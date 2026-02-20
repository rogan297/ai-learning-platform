from typing import Optional
from langgraph.graph import add_messages
from typing_extensions import TypedDict, Annotated
from nodes.classify_topic import TopicEval

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    topic_eval: Optional[TopicEval]
    user_lang: str
    stimulus_count: int