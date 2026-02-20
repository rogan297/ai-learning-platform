"""update_agent_config tool for MCP server.
"""

from core.server import mcp
import yaml
import io
from jinja2 import Template
from kubernetes import client, config, dynamic
from kubernetes.dynamic.exceptions import ResourceNotFoundError

import asyncio

@mcp.tool()
def update_agent_config(name: str, description: str, skills: list) -> str:
    """
        Performs a complete update of an existing agent's configuration and skill set.

        This tool overwrites the current agent settings with new values. It is specifically designed
        to evolve an agent's capabilities by adjusting its 'skills' list and metadata based
        on new requirements.

        Note: This is a full replacement update. All parameters must be provided to maintain
        the integrity of the agent's profile.

        Args:
            name (str): You have to pass the same name of the agent that want to update, not create a one new.
            description (str): The updated description of the agent's role.
            skills (list): The new complete list of skills/tools the agent is authorized to use.
                           This replaces the previous skill set entirely.
            user_id (str): The identifier of the user performing the update (for authorization).

        Returns:
            str: A confirmation message indicating the successful synchronization of the
                 new configuration and the updated status of the agent.
    """
    try:
        config.load_kube_config()
    except:
        config.load_incluster_config()

    k8s_client = client.ApiClient()
    dynamic_client = dynamic.DynamicClient(k8s_client)

    populated_skills = {}
    for skill in skills:
        key = f"skill-{skill.lower().replace(' ', '-')}"
        populated_skills[key] = skill

    data_vars = {
        "name": name,
        "description": description,
        "skills": populated_skills
    }

    with open("agent-template.yaml", "r") as f:
        template_content = f.read()

    template = Template(template_content)
    rendered_string = template.render(data_vars)
    resource_data = yaml.safe_load(rendered_string)

    try:
        api_resource = dynamic_client.resources.get(
            api_version="kagent.dev/v1alpha2",
            kind="Agent"
        )

        dynamic_client.patch(
            resource=api_resource,
            body=resource_data,
            name=name,
            namespace="kagent",
            content_type="application/merge-patch+json"
        )

        success_msg = f"Resource '{name}' updated successfully via Patch."
        print(success_msg)
        return success_msg
    except ResourceNotFoundError:

        error_message = "Error: The CRD 'Agent' (kagent.dev/v1alpha2) is not installed in the cluster."
        print(error_message)
        return error_message
    except Exception as e:
        if "AlreadyExists" in str(e):
            error_message = "Resource already exists."
            print(error_message)
            return error_message
        else:
            error_message = f"Unexpected error: {e}"
            print(error_message)
            return error_message

