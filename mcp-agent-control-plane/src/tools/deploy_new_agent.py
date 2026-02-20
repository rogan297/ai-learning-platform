import logging
import yaml
import os
from jinja2 import Template
from kubernetes import client, config, dynamic
from kubernetes.dynamic.exceptions import ResourceNotFoundError
from kubernetes.client.rest import ApiException
from core.server import mcp

# Configure standard logging format if not already set globally
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(agent_name)s] %(message)s'
)
logger = logging.getLogger(__name__)


@mcp.tool()
async def deploy_new_agent(name: str, description: str, skills: list) -> str:
    """
    Registers and deploys a new AI agent including its RBAC security context.
    """
    log = logging.LoggerAdapter(logger, {"agent_name": name})

    log.info(f"Initiating deployment sequence for agent: {name}")

    try:
        try:
            config.load_incluster_config()
            log.debug("Loaded in-cluster Kubernetes configuration.")
        except config.ConfigException:
            config.load_kube_config()
            log.debug("Loaded local kube-config.")

        k8s_client = client.ApiClient()
        core_api = client.CoreV1Api(k8s_client)
        rbac_api = client.RbacAuthorizationV1Api(k8s_client)
        dynamic_client = dynamic.DynamicClient(k8s_client)

        namespace = os.getenv("NAMESPACE", "kagent")
        log.info(f"Targeting namespace: {namespace}")

        sa_manifest = client.V1ServiceAccount(metadata=client.V1ObjectMeta(name=name))

        role_manifest = client.V1Role(
            metadata=client.V1ObjectMeta(name=f"{name}-reader-role", namespace=namespace),
            rules=[client.V1PolicyRule(
                api_groups=["kagent.dev"],
                resources=["agents"],
                verbs=["get", "list"]
            )]
        )

        rb_manifest = client.V1RoleBinding(
            metadata=client.V1ObjectMeta(name=f"{name}-rb", namespace=namespace),
            subjects=[client.RbacV1Subject(kind="ServiceAccount", name=name, namespace=namespace)],
            role_ref=client.V1RoleRef(
                kind="Role",
                name=f"{name}-reader-role",
                api_group="rbac.authorization.k8s.io"
            )
        )

        resources = [
            ("ServiceAccount", core_api.create_namespaced_service_account, sa_manifest),
            ("Role", rbac_api.create_namespaced_role, role_manifest),
            ("RoleBinding", rbac_api.create_namespaced_role_binding, rb_manifest)
        ]

        for res_type, api_call, body in resources:
            try:
                log.debug(f"Attempting to create {res_type}...")
                api_call(namespace=namespace, body=body)
                log.info(f"Successfully created {res_type}: {name}")
            except ApiException as e:
                if e.status == 409:
                    log.warning(f"{res_type} '{name}' already exists. Skipping creation.")
                else:
                    log.error(f"Failed to create {res_type}: {e.status} - {e.reason}")
                    raise e

        log.debug(f"Processing template for agent Custom Resource with {len(skills)} skills.")
        populated_skills = {f"skill-{s.lower().replace(' ', '-')}": s for s in skills}

        data_vars = {
            "name": name,
            "description": description,
            "skills": populated_skills
        }

        template_path = "agent-template.yaml"
        if not os.path.exists(template_path):
            log.error(f"Template file missing: {template_path}")
            return f"Error: {template_path} not found."

        with open(template_path, "r") as f:
            template = Template(f.read())

        resource_data = yaml.safe_load(template.render(data_vars))

        try:
            agent_resource = dynamic_client.resources.get(
                api_version="kagent.dev/v1alpha2",
                kind="Agent"
            )
            log.debug("Found Agent CRD definition.")

            agent_resource.create(body=resource_data, namespace=namespace)
            log.info(f"Agent Custom Resource '{name}' deployed successfully.")

        except ResourceNotFoundError:
            log.critical("CRD 'kagent.dev/v1alpha2' not found on cluster.")
            return "Error: Agent CRD is not installed."

        return f"Successfully deployed agent '{name}' with full RBAC context."

    except ApiException as e:
        log.error(f"Kubernetes API rejection: {e.status} {e.reason} - {e.body}")
        return f"K8s API Error: {e.reason}"
    except Exception as e:
        log.exception(f"Unexpected fatal error during deployment of {name}")
        return f"Deployment failed: {str(e)}"