import json
import logging
import os
import asyncio
import uvicorn

from kagent.core import KAgentConfig
from kagent.langgraph import KAgentApp
from agent import create_graph
from agent import get_db_resources

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

async def main():
    """Main entry point for the CLI."""
    with open(os.path.join(os.path.dirname(__file__), "agent-card.json"), "r") as f:
        agent_card = json.load(f)


    config = KAgentConfig(name=agent_card.get("name", "orchestrator-agent"))



    async with get_db_resources() as pool:
        graph = await create_graph(pool)

        app = KAgentApp(graph=graph, agent_card=agent_card, config=config, tracing=True)

        port = int(os.getenv("AGENT_PORT", "8080"))
        host = os.getenv("AGENT_HOST", "0.0.0.0")


        server_config = uvicorn.Config(
            app.build(),
            host=host,
            port=port,
            log_level="info"
        )
        server = uvicorn.Server(server_config)

        logger.info(f"Starting server on {host}:{port}")


        await server.serve()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")