import logging
import uuid
from typing import Literal

from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, AIMessage
from langgraph.types import Command


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("Orchestrator.SelectAgent")


class AgentEval(BaseModel):
    there_is_agent: bool = Field(
        ...,
        description="True ONLY if a specialized agent (NOT the orchestrator) exists for this topic."
    )
    agent_name: str = Field(
        ...,
        description="Technical name. If creating new: use kebab-case (e.g., 'ethics-specialist')."
    )
    agent_description: str = Field(
        ...,
        description="Executive summary of functions."
    )
    agent_skills: list[str] = Field(
        ...,
        description="List of skills in KEBAB-CASE (no spaces, e.g., ['ai-ethics', 'risk-management']). Mandatory for K8s compatibility."
    )
    action_type: Literal["update_agent_config", "deploy_new_agent"] = Field(
        ...,
        description="Decision: 'deploy_new_agent' is preferred for new specific domains."
    )

async def select_agent(state, model):
    logger.info("Starting select_agent nodes execution.")

    available_agents_output = state["messages"][-1].content
    topic_info = state.get("topic_eval", None)
    user_lang = state.get("language", "en")


    if not topic_info or not topic_info.topic_found:
        logger.warning(f"Topic not found or invalid: {topic_info}. Routing to generate_user_prompt.")
        return Command(goto="generate_user_prompt")

    logger.info(f"Analyzing topic: '{topic_info.topic_name}' (Language: {user_lang})")

    system_prompt = f"""
    ### ROLE
    You are a High-Precision System Architect Orchestrator. Your goal is to maintain an efficient agent fleet by avoiding redundancy.

    ### CRITICAL RULES
1. **PROTECT ORCHESTRATOR**: Never, under any circumstances, select 'update_agent_config' for the 'orchestrator-agent'. It is a system-level agent and must remain untouched.
2. **KUBERNETES COMPLIANCE**: All 'agent_skills' must be written in kebab-case (lowercase, dashes instead of spaces). 
   - WRONG: "AI ethics"
   - RIGHT: "ai-ethics"
3. **NEW VS UPDATE**: Only update an agent if it is a 90% match and it is NOT the orchestrator. If the topic is "{topic_info.topic_name}", and no specialized agent exists, you MUST use 'deploy_new_agent'.
    
    ### CONTEXT
    - USER TOPIC: "{topic_info.topic_name}"
    - SYSTEM LANGUAGE: {user_lang}
    - AVAILABLE AGENTS: 
    <agents>
    {available_agents_output}
    </agents>

    ### DECISION LOGIC
    1. ANALYZE: Compare the 'USER TOPIC' against each agent in 'AVAILABLE AGENTS'.
    2. EVALUATE: 
       - Does an existing agent have a domain expertise that covers the 'USER TOPIC'?
       - Example: If topic is "Python Debugging" and an agent "Code Expert" exists, UPDATE him. Do not create a new one.
    3. ACTION:
       - If match found (Similarity > 0.7): Set action_type="update_agent_config" and merge descriptions.
       - If NO match found: Set action_type="deploy_new_agent" and design a specialized agent.

    ### OUTPUT INSTRUCTIONS
    - All descriptions and skill lists must be written in: {user_lang}.
    - 'agent_skills' MUST be a JSON list of specific strings (e.g., ["skill1", "skill2"]).
    - The 'agent_name' must be professional and follow snake_case or PascalCase.
    """

    logger.debug(f"System prompt generated for model. Length: {len(system_prompt)}")

    try:
        structured_model = model.with_structured_output(AgentEval)
        logger.info("Invoking LLM for structured analysis...")

        analysis = await structured_model.ainvoke([
            SystemMessage(content=system_prompt)
        ])

        logger.info(
            f"LLM Analysis complete. Result: Agent Found={analysis.there_is_agent}, Action={analysis.action_type}")
    except Exception as e:
        logger.error(f"Error during LLM invocation: {str(e)}", exc_info=True)
        raise

    tool_call_id = f"call_{uuid.uuid4().hex[:12]}"

    tool_call_message = AIMessage(
        content="",
        tool_calls=[{
            "name": analysis.action_type,
            "args": {
                "name": analysis.agent_name,
                "description": analysis.agent_description,
                "skills": analysis.agent_skills
            },
            "id": tool_call_id,
            "type": "tool_call",
        }],
    )

    logger.info(f"Tool call generated: {analysis.action_type} with ID {tool_call_id}")

    return {
        "messages": [tool_call_message],
    }