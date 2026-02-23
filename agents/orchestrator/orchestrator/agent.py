import asyncio
import uuid
import os
import logging
from contextlib import asynccontextmanager
from psycopg_pool import AsyncConnectionPool

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.store.postgres.aio import AsyncPostgresStore
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI

from nodes.classify_topic import classify_topic
from nodes.select_agent import select_agent
from nodes.generate_user_prompt import generate_user_prompt
from nodes.tool_node import get_tools_function
from state import AgentState
from langchain_google_genai import ChatGoogleGenerativeAI

# OpenTelemetry imports
from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.openai import OpenAIInstrumentor
from openinference.instrumentation.langchain import LangChainInstrumentor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def get_db_resources():
    db_uri = os.getenv("DB_URI")

    logger.info("Initializing database resource connection...")

    connection_kwargs = {
        "autocommit": True
    }

    try:
        async with AsyncConnectionPool(conninfo=db_uri, max_size=10, kwargs=connection_kwargs) as pool:
            logger.info("Connection pool established with Postgres")
            yield pool
    except Exception as e:
        logger.error(f"Could not connect to the database pool: {e}")
        raise


def get_model():
    provider = os.getenv("PROVIDER", "").lower()
    model_name = os.getenv("MODEL_NAME", "gpt-4o-mini")  # Default model
    api_key = os.getenv("API_KEY")
    supported_providers = {
        "openai": ChatOpenAI,
        "gemini": ChatGoogleGenerativeAI
    }

    if provider not in supported_providers:
        raise ValueError(f"Provider '{provider}' is not supported. Choose from: {list(supported_providers.keys())}")

    if not api_key:
        raise ValueError("You must provide a valid API key")

    model_class = supported_providers[provider]

    actual_model = "gemini-1.5-flash" if provider == "gemini" and model_name == "gpt-4o-mini" else model_name


    return model_class(model=actual_model, api_key=api_key)

async def create_graph(pool):
    logger.info("Starting graph compilation process...")

    try:
        # --- Telemetry Setup ---
        logger.info("Configuring OpenTelemetry...")
        resource = Resource(attributes={
            SERVICE_NAME: "orchestrator-agent"
        })

        endpoint = "http://opentelemetry-collector-audit.telemetry.svc.cluster.local:4317"
        logger.info(f"Connecting to OTLP exporter at: {endpoint}")

        provider = TracerProvider(resource=resource)
        exporter = OTLPSpanExporter(endpoint=endpoint, insecure=True)
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)


        logger.info("TracerProvider initialized and OTLP exporter attached.")

        # Instrumenting libraries
        logger.info("Instrumenting OpenAI and LangChain...")
        OpenAIInstrumentor().instrument()
        LangChainInstrumentor().instrument()
        logger.info("Instrumentation complete. Traces will be sent to the collector.")
        # -----------------------


        checkpointer = AsyncPostgresSaver(pool)
        store = AsyncPostgresStore(pool)

        logger.debug("Running setup for checkpointer and store...")
        await checkpointer.setup()
        await store.setup()

        model = get_model()
        tools = await get_tools_function()
        execute_tools = ToolNode(tools)
        logger.info(f"Loaded {len(tools)} tools for ToolNode")

        async def classify_topic_node(state: AgentState):
            logger.info("Node: classify_topic - Processing")
            return await classify_topic(state, model)

        async def generate_prompt_node(state: AgentState):
            logger.info("Node: generate_user_prompt - Processing")
            return await generate_user_prompt(state, model)

        async def select_agent_node(state: AgentState):
            logger.info("Node: select_agent - Processing")
            return await select_agent(state, model)

        graph_builder = StateGraph(AgentState)

        logger.debug("Adding nodes to the graph...")
        graph_builder.add_node("classify_topic", classify_topic_node)
        graph_builder.add_node("execute_list_tool", execute_tools)
        graph_builder.add_node("execute_tools", execute_tools)
        graph_builder.add_node("select_agent", select_agent_node)
        graph_builder.add_node("generate_user_prompt", generate_prompt_node)

        graph_builder.add_edge(START, "classify_topic")

        graph_builder.add_conditional_edges(
            "classify_topic",
            tools_condition,
            {
                "tools": "execute_list_tool",
                "__end__": "generate_user_prompt"
            }
        )

        graph_builder.add_edge("execute_list_tool", "select_agent")

        graph_builder.add_conditional_edges(
            "select_agent",
            tools_condition,
            {
                "tools": "execute_tools",
                "__end__": END
            }
        )

        compiled_graph = graph_builder.compile(checkpointer=checkpointer, store=store)
        logger.info("Graph compiled successfully.")
        return compiled_graph

    except Exception as e:
        logger.exception("An error occurred during graph creation or telemetry setup")
        raise