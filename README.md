install agentgateway-crd
install kagent-crd
install kubernetes-api-gateway-extension

helm upgrade --install agentgateway ./agentgateway-install -n agentgateway-system --create-namespace

helm upgrade --install keycloak ./keycloak -n keycloak


helm upgrade --install cert-manager ./cert-manager -n cert-manager --create-namespace --set installCRDs=true
helm upgrade --install postgres ./postgresql -n database --create-namespace

helm upgrade --install opentelemetry-collector-audit ./opentelemetry-collector -n telemetry --create-namespace
helm upgrade --install loki ./loki -n telemetry --create-namespace
helm upgrade --install tempo ./tempo -n telemetry --create-namespace
helm upgrade --install grafana ./grafana -n telemetry --create-namespace

install opentelemetry collector

install telemetry

docker build
kind load docker-image
install kagent (kagent y kmcp)