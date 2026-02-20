# template-agent Agent

This is a template-agent agent that can be used to test KAgent BYO agent with ADK.

## Model Configuration

This agent is configured to use the **gemini** provider with model **gemini-2.0-flash**.

## Usage

1. Build the agent image and push it to the local registry using the KAgent CLI

```bash
kagent build template-agent
```

2. Deploy the agent

```bash
kagent deploy template-agent --api-key <api-key>
```

Or create a secret with the api key

```bash
kubectl create secret generic my-secret -n <namespace> --from-literal=<PROVIDER>_API_KEY=$API_KEY --dry-run=client -oyaml | k apply -f -
```

And then deploy the agent

```bash
kagent deploy template-agent --api-key-secret "my-secret"
```