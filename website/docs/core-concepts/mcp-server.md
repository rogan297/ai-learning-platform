---
sidebar_position: 3
sidebar_label: Mcp Server
---
## Overview

The MCP Server provides three core tools responsible for dynamically
managing agents inside a Kubernetes cluster. These tools enable secure
deployment, updating, and listing of agents while leveraging RBAC
permissions to ensure proper governance and access control.

------------------------------------------------------------------------

## 1. deploy_agent Tool

### Description

The `deploy_agent` tool is the primary and most important tool of the
MCP server. It is responsible for dynamically creating and deploying new
agents inside the cluster.

### Arguments

This tool accepts three arguments:

-   `name`
-   `description`
-   `skills` (key-value map)

### How It Works

Using the **Jinja2 templating framework**, the tool dynamically
generates a Kubernetes YAML manifest for the agent based on the
following template:



``` yaml
apiVersion: kagent.dev/v1alpha2
kind: Agent
metadata:
  name: "{{ name }}"
  labels:
    {%- for key, value in skills.items() %}
    {{ key }}: "{{ value }}"
    {%- endfor %}
spec:
  serviceAccountName: "{{ name }}"
  description: "{{ description }}"
  type: BYO
  byo:
    deployment:
      image: agent/custom/template-agent:0.1.0
      env:
        - name: DB_URI
          value: "postgresql://postgres:postgres@postgres.database.svc.cluster.local:5432/ai_platform_core"
        - name: AGENT_HOST
          value: "0.0.0.0"
        - name: AGENT_PORT
          value: "8080"
        - name: AGENT_NAME
          value: "{{ name }}"
        - name: API_KEY
          value: "your-token"
        - name: PROVIDER
          value: "openai"
        - name: MODEL
          value: "gpt-4o-mini"
```



After generating the YAML definition, the tool uses:

-   The Kubernetes Python client
-   The RBAC permissions assigned to the MCP server within the cluster

With these permissions, the agent is automatically created and deployed.

------------------------------------------------------------------------

## 2. update_agent Tool

### Description

The `update_agent` tool is responsible for updating existing agents
inside the cluster.

### Arguments

This tool also accepts three arguments:

-   `name`
-   `description`
-   `skills`

### How It Works

Using the provided `name` (which must match the existing agent), the
tool updates the agent's description and skills.

The update process is performed using:

-   The Kubernetes Python client
-   The RBAC permissions granted to the MCP server

This ensures that updates are secure, controlled, and compliant with
cluster governance policies.

------------------------------------------------------------------------

## 3. list_agents Tool

### Description

The `list_agents` tool retrieves information about agents currently
deployed in the cluster.

### How It Works

It returns relevant metadata about existing agents.

This tool is particularly important for the main orchestrator agent,
which uses the list of deployed agents to decide whether to:

-   Update an existing agent
-   Deploy a new agent

The decision is based on the current state of agents in the cluster.

------------------------------------------------------------------------

## Security and Access Control

The MCP tools are exposed exclusively through AgentGateway on route **/mcp-server** .

All requests must pass through AgentGateway, ensuring:

-   Controlled access
-   Proper authentication and authorization
-   Secure execution of operations inside the cluster

This architecture guarantees that only authorized entities can request
operations, ensuring strong security and governance.
