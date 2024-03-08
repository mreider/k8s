#!/bin/bash
sudo snap install docker
sudo snap install microk8s --classic --channel=1.28/stable
sudo microk8s enable registry
# Ask for Dynatrace endpoint and token
read -p "Enter your Dynatrace tenant (ex: live.dt.com): " DT_ENDPOINT
read -p "Enter your Dynatrace token: " DT_TOKEN
# Containerize using Docker
echo "Building"
docker build -t backend:latest ./apps/backend
docker build -t frontend:latest ./apps/frontend
docker build -t proxy:latest ./apps/proxy
docker tag backend:latest localhost:32000/backend:latest
docker tag frontend:latest localhost:32000/frontend:latest
docker tag proxy:latest localhost:32000/proxy:latest
# Push to local registry
echo "Pushing to local registry"
docker push localhost:32000/backend:latest
docker push localhost:32000/frontend:latest
docker push localhost:32000/proxy:latest
# Create secret for Dynatrace
echo "Creating Kubernetes secret for Dynatrace credentials..."
kubectl create secret generic dynatrace-otelcol-dt-api-credentials -n orders --from-literal=DT_API_ENDPOINT="https://$DT_ENDPOINT" --from-literal=DT_API_TOKEN="$DT_TOKEN"
# Deploy
echo "Deploying"
kubectl apply -f deployments/namespace-orders.yaml
kubectl apply -f deployments/deployment-dynatrace-collector.yaml
kubectl apply -f deployments/deployment-backend.yaml
kubectl apply -f deployments/deployment-frontend.yaml
kubectl apply -f deployments/deployment-proxy.yaml
kubectl set env deployment/backend -n orders UPDATE_TIME="$(date)"
kubectl set env deployment/frontend -n orders UPDATE_TIME="$(date)"
kubectl set env deployment/proxy -n orders UPDATE_TIME="$(date)"
echo "Setup complete."