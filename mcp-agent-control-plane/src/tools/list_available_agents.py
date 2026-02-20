from core.server import mcp
import logging
import json
from kubernetes_asyncio import client, config
from kubernetes_asyncio.client.rest import ApiException

import asyncio

@mcp.tool()
async def list_available_agents() -> str:
    """
    Retrieves a list of all AI agents by querying the Kubernetes Cluster CRDs.
    
    Returns:
        str: A JSON-formatted string containing an array of agent objects derived from CRDs.
    """
    api_client = None
    try:
        try:
            config.load_incluster_config()
        except config.ConfigException:
            await config.load_kube_config()

        group = "kagent.dev"
        version = "v1alpha2"
        plural = "agents"

        api_client = client.ApiClient()

        custom_api = client.CustomObjectsApi(api_client)

        response = await custom_api.list_cluster_custom_object(
            group=group,
            version=version,
            plural=plural
        )

        agents = []
        items = response.get("items", [])


        for item in items:
            spec = item.get("spec", {})
            metadata = item.get("metadata", {})

            agent_data = {
                "id": metadata.get("uid"),
                "name": metadata.get("name"),
                "description": spec.get("description", "No description provided"),
                "labels": metadata.get("labels", {}),
            }
            agents.append(agent_data)

        return json.dumps(agents, indent=2)

    except ApiException as e:
        logging.error(f"Kubernetes API error: {e}")
        return f"Error connecting to cluster: {e}"
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return f"General error: {str(e)}"
    finally:
        if api_client:
            await api_client.close()
            logging.info("Kubernetes API client session closed.")