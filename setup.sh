# Ask for Dynatrace endpoint and token
read -p "Enter your Dynatrace tenant (ex: live.dt.com): " DT_ENDPOINT
read -p "Enter your Dynatrace token: " DT_TOKEN
# Containerize using Docker
echo "Building"
docker build -t localhost:5000/backend:v1.0 ./apps/backend
docker build -t localhost:5000/frontend:v1.0 ./apps/frontend
docker build -t localhost:5000/proxy:v1.0 ./apps/proxy
# Push to local registry
echo "Pushing to local registry"
podman push localhost:5000/backend:v1.0 --tls-verify=false
podman push localhost:5000/frontend:v1.0 --tls-verify=false
podman push localhost:5000/proxy:v1.0 --tls-verify=false
# Deploy
echo "Deploying"
kubectl  apply -f deployments/namespace-orders.yaml
kubectl create secret generic dynatrace-otelcol-dt-api-credentials -n orders --from-literal=DT_API_ENDPOINT="https://$DT_ENDPOINT" --from-literal=DT_API_TOKEN="$DT_TOKEN"
kubectl  apply -f deployments/deployment-dynatrace-collector.yaml
kubectl  apply -f deployments/deployment-backend.yaml
kubectl  apply -f deployments/deployment-frontend.yaml
kubectl  apply -f deployments/deployment-proxy.yaml
kubectl  set env deployment/backend -n orders UPDATE_TIME="$(date)"
kubectl  set env deployment/frontend -n orders UPDATE_TIME="$(date)"
kubectl  set env deployment/proxy -n orders UPDATE_TIME="$(date)"
echo "Setup complete."
