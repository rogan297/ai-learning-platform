from typing import Optional, Annotated, Dict, List, Any
from langgraph.graph import add_messages
from typing_extensions import TypedDict


class AgentMetadata(TypedDict):
    """
    Structure to hold Kubernetes CRD information.
    """
    label: str
    description: str
    capabilities: List[str]
    raw_crd: Optional[Dict[str, Any]]


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    user_lang: str
    agent_info: AgentMetadata
    quiz_score: Optional[int]
    needs_remediation: bool
    current_material: Optional[str]