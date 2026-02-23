from langchain_core.messages import HumanMessage, SystemMessage


async def generate_user_prompt(state, model):
    """Generate a topic suggestion prompt when user input lacks specific topic."""
    user_lang = getattr(state.get("topic_eval", {}), "user_lang", "en")

    system_prompt = f"""You are a Technical Learning Curator. Since the user hasn't specified a topic, your goal is to present a structured 'Learning Menu' with high-impact, specific niches to spark their interest.

    Rules:
    1. NO CONVERSATIONAL FILLER: Do not ask "How are you?" or "What do you want to learn?". 
    2. BE SPECIFIC: Instead of 'AI', suggest 'Large Language Models (LLMs)' or 'Computer Vision'. Instead of 'Databases', suggest 'Vector Databases for RAG' or 'NoSQL Architecture'.
    3. STRUCTURE: Use bold headers and bullet points. Each topic must include a 1-sentence 'why it matters'.
    4. MANDATORY LANGUAGE: Respond EXACTLY in {user_lang.upper()}.
    5. CALL TO ACTION: End with a brief: "Reply with a topic or number to start a deep-dive roadmap."

    Example format:
    - **Topic Name**: Brief technical value proposition."""

    messages = [SystemMessage(content=system_prompt), *state["messages"]]
    response = await model.ainvoke(messages)

    return {"messages": [response]}