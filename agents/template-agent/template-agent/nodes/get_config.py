import os
import logging
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from state import AgentState

logger = logging.getLogger(__name__)


async def get_config(state: AgentState):
    """
    Fetches agent configuration from the Kagent CRD instance.
    """
    try:
        config.load_incluster_config()
        custom_api = client.CustomObjectsApi()

        namespace = "kagent"
        resource_name = os.getenv("AGENT_NAME")

        group = "kagent.dev"
        version = "v1alpha2"
        plural = "agents"

        resource = custom_api.get_namespaced_custom_object(
            group=group,
            version=version,
            namespace=namespace,
            plural=plural,
            name=resource_name
        )

        labels = resource.get("metadata", {}).get("labels", {})
        skills = {k: v for k, v in labels.items() if not k.startswith("kubernetes.io/")}

        spec = resource.get("spec", {})
        description = spec.get("description", "No description provided in CRD.")

        logger.info(f"Configuration successfully loaded for Agent: {resource_name}")

        return {
            "agent_info": {
                "label": resource_name,
                "description": description,
                "capabilities": list(skills.keys()),
                "raw_crd": resource
            }
        }

    except ApiException as e:
        logger.error(f"K8s API Exception: {e}")
        return {"agent_info": {"description": "Error: Unauthorized or Missing CRD"}}
    except Exception as e:
        logger.error(f"Unexpected error in get_config: {e}")
        return {"agent_info": {"description": f"Error: {str(e)}"}}