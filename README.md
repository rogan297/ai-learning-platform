# IA Learning Platform 

IA Learning Platform is an adaptive, AI-driven learning system where users define what they want to study, and the platform dynamically generates specialized learning agents for each subject.

Each agent is designed to deliver structured content, generate exercises, provide feedback, and guide progression based on the learner’s goals. The system continuously analyzes user interactions, performance, and preferences to adapt difficulty, pacing, and content strategy.

By leveraging a multi-agent architecture and continuous personalization, the platform creates a scalable and evolving educational environment tailored to each individual learner.


[Explore the IA Learning Platform Blog](https://rogan297.github.io/ai-learning-platform/blog)

---

## Prerequisites

Before starting, ensure you have the following tools installed:
* **[kind](https://kind.sigs.k8s.io/docs/user/quick-start/)**
* **[kubectl](https://kubernetes.io/docs/tasks/tools/)**
* **[Helm 3.19.0](https://helm.sh/docs/intro/install/)**
* **[Docker](https://www.docker.com/get-started/)** (for local builds)

---

##  Installation Steps
1. clone the repositories and create the kind cluster.
```bash
git clone https://github.com/rogan297/ai-learning-platform.git
cd ai-learning-platform
``` 
2. Create the kind cluster.
```bash
kind create cluster
```

3. Install the necessary CRDs for the Gateway API and the Agent components to ensure the cluster recognizes these resource types.

```bash
# Install Agent Gateway CRDs
helm upgrade -i --create-namespace \
  --namespace agentgateway-system \
  --version v2.2.1 agentgateway-crds \
  oci://ghcr.io/kgateway-dev/charts/agentgateway-crds

# Install KAgent CRDs
helm install kagent-crds oci://ghcr.io/kagent-dev/kagent/helm/kagent-crds \
  --namespace kagent \
  --create-namespace

# Install Standard Kubernetes Gateway API
kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.4.0/standard-install.yaml

```

4. Deploy the supporting services: Identity Management (Keycloak), Certificate Management, and the Database.
```bash
# Identity Provider
helm upgrade --install keycloak ./keycloak -n keycloak --create-namespace

# NOTE: You must manually create users and the Keycloak Realm.
# Default configuration: 
# username: agent
# password: 1234
# client_id: agent-client
# audience: agent-client
# Access the UI via port-forward:
kubectl port-forward svc/keycloak -n keycloak 8080:8080

# Database
helm upgrade --install postgres ./postgresql -n database --create-namespace
```

5. Deploy the LGTM stack (Loki, Grafana, Tempo) and OpenTelemetry for monitoring and auditing.

```bash
# OpenTelemetry Collector
helm upgrade --install opentelemetry-collector-audit ./opentelemetry-collector \
  -n telemetry --create-namespace \
  -f opentelemetry-collector/otel-collector-audit-values.yaml

# Logs, Traces, and Dashboards
helm upgrade --install loki ./loki -n telemetry --create-namespace -f loki/loki-values.yaml
helm upgrade --install tempo ./tempo -n telemetry --create-namespace -f tempo/tempo-values.yaml
helm upgrade --install grafana ./grafana -n telemetry --create-namespace \
  -f grafana/grafana-values.yaml \
  --set assertNoLeakedSecrets=false
```

6. Finally, deploy the gateway and the custom learning agents.
``` bash
# Install Agent Gateway
helm upgrade --install agentgateway ./agentgateway/agentgateway-install \
  -n agentgateway-system \
  --create-namespace \
  --set auth.keycloak.realm="agent-realm" \
  --set auth.jwt.audience="agent-client" \
  --set controlPlane.serviceName="mcp-agent-control-plane"

# Before upload the docker images, you have to set the api keys and providers to:
nano agents/orchestrator/agent.yaml
nano mcp-agent-control-plane/agent-template.yaml 


# Build and Load Local Image (for Kind environments)
docker compose build
kind load docker-image agent/custom/orchestrator:0.1.0 agent/custom/template-agent:0.1.0 mcp-agent-control-plane:0.1.0

# Install KAgent
helm upgrade --install kagent ./kagent/kagent-install \
  -n kagent \
  --create-namespace
  
# Monitor the MCP server status
kubectl get pod -n kagent -w

# Create the agent
kubectl apply -f agents/orchestrator/agent.yaml
```
7. Once the deployment is complete, you can verify the status of the components and start using the platform.

```bash
kubectl get pods -A

# Grafana Dashboards:
kubectl port-forward svc/grafana -n telemetry 3000:80

# Kagent User Interfaz
kubectl port-forward -n kagent service/kagent-ui 8082:8080
```
