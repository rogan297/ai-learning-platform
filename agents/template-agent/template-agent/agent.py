import asyncio
import uuid
import os
import logging
from contextlib import asynccontextmanager
from psycopg_pool import AsyncConnectionPool

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.store.postgres.aio import AsyncPostgresStore
from langchain_openai import ChatOpenAI


from nodes.task import task
from nodes.get_config import get_config
from state import AgentState



logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def get_db_resources():
    db_uri = os.getenv("DB_URI")
    ca_content = os.getenv("DB_CA_CONTENT")
    cert_content = os.getenv("DB_CERT_CONTENT")
    key_content = os.getenv("DB_KEY_CONTENT")

    # Nota: host y port deben estar definidos o venir de env
    logger.info("Initializing database resource connection...")

    if ca_content and cert_content and key_content:
        try:
            cert_dir = "/tmp/db_certs"
            os.makedirs(cert_dir, exist_ok=True)

            paths = {
                "ca": os.path.join(cert_dir, "ca.crt"),
                "cert": os.path.join(cert_dir, "tls.crt"),
                "key": os.path.join(cert_dir, "tls.key")
            }

            with open(paths["ca"], "w") as f:
                f.write(ca_content)
            with open(paths["cert"], "w") as f:
                f.write(cert_content)
            with open(paths["key"], "w") as f:
                f.write(key_content)

            os.chmod(paths["key"], 0o600)
            logger.info(f"Certificates written successfully to {cert_dir}")

            if "sslrootcert" not in db_uri:
                db_uri += f"&sslrootcert={paths['ca']}&sslcert={paths['cert']}&sslkey={paths['key']}&sslmode=verify-full"

        except Exception as e:
            logger.exception("Failed to write database certificates to disk")
            raise

    connection_kwargs = {
        "sslmode": "verify-ca",
        "sslrootcert": "/tmp/db_certs/ca.crt",
        "sslcert": "/tmp/db_certs/tls.crt",
        "sslkey": "/tmp/db_certs/tls.key",
        "autocommit": True
    }

    try:
        async with AsyncConnectionPool(conninfo=db_uri, max_size=10, kwargs=connection_kwargs) as pool:
            logger.info("Connection pool established with Postgres")
            yield pool
    except Exception as e:
        logger.error(f"Could not connect to the database pool: {e}")
        raise


async def create_graph(pool):
    logger.info("Starting graph compilation process...")

    try:
        checkpointer = AsyncPostgresSaver(pool)
        store = AsyncPostgresStore(pool)

        logger.debug("Running setup for checkpointer and store...")
        await checkpointer.setup()
        await store.setup()

        model = ChatOpenAI(model="gpt-4o-mini")


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
