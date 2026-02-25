---
sidebar_Position: 3
sidebar_label: AgentGateway
---
### Agent Gateway Overview

The **Agent Gateway** acts as the primary connectivity hub between all of our services, from our **MCP server** to our application. 

The following configurations are managed within our **AgentGateway**:

* **Authentication Policies:** Integrated with **Keycloak** to validate **JWT tokens**.
* **Routing:** Standard routes such as `/mcp-server` are configured for applications to connect to our MCP server.
* **Backend Configurations:** Specific settings that point directly to the **MCP service**.
