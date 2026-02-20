import uuid
import logging
from typing import Optional
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from state import AgentState

logger = logging.getLogger(__name__)


async def task(state: AgentState, model):
    """
    This nodes generates study material and a quiz based on CRD metadata.
    """
    info = state.get("agent_info", {})
    agent_label = info.get("label", "Tutor")
    agent_description = info.get("description", "Expert Assistant")
    capabilities = ", ".join(info.get("capabilities", []))


    base_system_prompt = f"""
    You are an AI Tutor. 
    ROLE: {agent_label}
    DESCRIPTION: {agent_description}
    SKILLS: {capabilities}

    YOUR GOAL:
    Create a short educational study material about your role and skills.
    Then, immediately follow it with a 3-question quiz to test the user.
    """

    input_messages = [SystemMessage(content=base_system_prompt)] + state["messages"]


    response = await model.ainvoke(input_messages)

    logger.info("Material and Quiz generated successfully.")


    return {
        "messages": [response]
    }