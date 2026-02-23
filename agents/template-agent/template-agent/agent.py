import os
import logging

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.store.postgres.aio import AsyncPostgresStore
from langchain_openai import ChatOpenAI

from contextlib import asynccontextmanager
from psycopg_pool import AsyncConnectionPool
from langchain_google_genai import ChatGoogleGenerativeAI
from nodes.task import task
from nodes.get_config import get_config
from state import AgentState

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


        async def task_node(state: AgentState):
            logger.info("Node: task - Processing")
            return await task(state, model)

        async def get_config_node(state: AgentState):
            logger.info("Node: get_config - Processing")
            return await get_config(state)

        graph_builder = StateGraph(AgentState)

        logger.debug("Adding nodes to the graph...")
        graph_builder.add_node("task", task_node)
        graph_builder.add_node("get_config", get_config_node)

        graph_builder.add_edge(START, "get_config")
        graph_builder.add_edge("get_config", "task")
        graph_builder.add_edge("task", END)

        compiled_graph = graph_builder.compile(checkpointer=checkpointer, store=store)
        logger.info("Graph compiled successfully.")
        return compiled_graph

    except Exception as e:
        logger.exception("An error occurred during graph creation or setup")
        raise
