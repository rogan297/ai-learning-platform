import uuid
from typing import Optional, Literal
import langdetect
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
import fuzzywuzzy.fuzz as fuzz


class TopicEval(BaseModel):
    """Strict evaluation to determine if the user has committed to a specific learning path or sub-topic."""
    topic_found: bool = Field(
        False,
        description="Set to True ONLY if the user has selected a concrete sub-topic, a numbered option from a list, or a specific lesson name."
    )
    topic_name: Optional[str] = Field(
        None,
        description="The clean name of the selected topic (e.g., 'Algorithmic Bias' instead of 'I want to learn about bias')."
    )
    specificity: Literal["none", "low", "medium", "high"] = Field(
        ...,
        description="""
        - 'none': Greeting or irrelevant text.
        - 'low': Broad fields (e.g., 'AI', 'Ethics', 'Math').
        - 'medium': Categories (e.g., 'Generative AI', 'Machine Learning').
        - 'high': Actionable niches, roadmap steps, or specific technical tasks (e.g., 'Data Bias Mitigation', 'Fine-tuning', 'React Hooks').
        """
    )
    content: str = Field(
        ...,
        description="Brief technical justification of why this specificity level was chosen."
    )


async def classify_topic(state: dict, model):
    messages = state["messages"]
    user_content = messages[-1].content.strip()

    last_ai_message = next((m for m in reversed(messages[:-1]) if isinstance(m, AIMessage)), None)

    forced_topic = None
    if last_ai_message and ("**" in last_ai_message.content or ":" in last_ai_message.content):
        options = [line.strip().replace("**", "") for line in last_ai_message.content.split('\n') if
                   ":" in line or "-" in line]

        for opt in options:
            if user_content.lower() in opt.lower() or (
                    len(user_content) > 5 and fuzz.partial_ratio(user_content.lower(), opt.lower()) > 85):
                forced_topic = opt.split(":")[0]
                break

    if forced_topic:
        response = TopicEval(
            topic_found=True,
            topic_name=forced_topic,
            specificity="high",
            content="User selected a suggested option from the menu."
        )
    else:
        user_lang = state.get("user_lang", "en")  # Usar el lenguaje guardado o detectar
        structured_model = model.with_structured_output(TopicEval)

        system_prompt = f"""STRICT Topic Classifier.
            Goal: Determine if the user is asking for a SPECIFIC technical or theoretical lesson.

            SPECIFICITY RULES:
            - HIGH: 'Algorithmic Bias', 'Differential Privacy', 'Step 1: Data cleaning', 'Backpropagation'.
            - LOW: 'AI', 'Ethics', 'Programming', 'I want to learn more'.

            If the user mentions a specific sub-topic or a title from a previous roadmap, mark as HIGH.
            ALWAYS respond in {user_lang.upper()}."""

        response = await structured_model.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_content)
        ])


    eval_message = AIMessage(content=f"Eval: {response.content}")
    messages_out = [eval_message]

    if response.topic_found:
        tool_call_id = f"call_{uuid.uuid4().hex[:12]}"
        tool_call_message = AIMessage(
            content="",
            tool_calls=[{
                "name": "list_available_agents",
                "args": {},
                "id": tool_call_id,
                "type": "tool_call",
            }],
        )
        messages_out.append(tool_call_message)

    return {
        "messages": messages_out,
        "topic_eval": response,
        "stimulus_count": 0 if response.topic_found else state.get("stimulus_count", 0) + 1
    }