import uuid
import logging
from typing import Optional
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from state import AgentState
import langdetect

logger = logging.getLogger(__name__)

async def task(state: AgentState, model):
    """
    This node generates high-level technical lessons and a quiz
    based on the agent's expertise area rather than its own metadata.
    """
    info = state.get("agent_info", {})
    agent_label = info.get("label", "Expert Tutor")
    agent_description = info.get("description", "A specialized assistant.")

    messages = state["messages"]
    user_content = messages[-1].content.strip()
    user_lang = langdetect.detect(user_content)

    subject_area = agent_label.replace("-", " ").replace("/", " ").title()

    base_system_prompt = f"""
    You are a Senior Technical Expert in {subject_area}.
    IDENTITY: {agent_label}
    CONTEXT: {agent_description}

    YOUR GOAL:
    Act as a mentor. Do not introduce yourself as an AI or explain your programming. 
    Instead, provide a deep-dive educational lesson on a specific core concept within {subject_area}.

    RESPONSE STRUCTURE:
    1. LESSON TITLE: A professional and engaging title.
    2. TECHNICAL CONTENT: Explain a specific architecture, workflow, or advanced concept. 
       Use technical depth (at least 3 detailed paragraphs).
    3. PRACTICAL SCENARIO: Provide a "Real-World Use Case" where this knowledge is applied.
    4. KNOWLEDGE CHECK: A 3-question multiple-choice quiz based ONLY on the content provided above.

    TONE: Professional, authoritative, and educational. Skip the "Hi, I'm your tutor" fluff and dive straight into the expertise.
    ALWAYS respond in {user_lang.upper()}"""

    input_messages = [SystemMessage(content=base_system_prompt)] + state["messages"]

    response = await model.ainvoke(input_messages)

    logger.info(f"Expert lesson on {subject_area} generated successfully.")

    return {
        "messages": [response]
    }