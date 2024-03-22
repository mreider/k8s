read -p "Enter your Dynatrace tenant (ex: live.dt.com): " DT_ENDPOINT
read -p "Enter your Dynatrace token: " DT_TOKEN
# Containerize using Docker compatibility with nerdctl
echo "Building"
sudo nerdctl -a /run/k3s/containerd/containerd.sock image prune --all --force
sudo nerdctl -a /run/k3s/containerd/containerd.sock build -t backend:v1.0 ./apps/backend
sudo nerdctl -a /run/k3s/containerd/containerd.sock  build -t frontend:v1.0 ./apps/frontend
sudo nerdctl -a /run/k3s/containerd/containerd.sock  build -t proxy:v1.0 ./apps/proxy
# Save and load container images
sudo nerdctl -a /run/k3s/containerd/containerd.sock save -o backend-v1.0.tar backend:v1.0
sudo nerdctl -a /run/k3s/containerd/containerd.sock save -o frontend-v1.0.tar frontend:v1.0
sudo nerdctl -a /run/k3s/containerd/containerd.sock save -o proxy-v1.0.tar proxy:v1.0
sudo nerdctl -a /run/k3s/containerd/containerd.sock -n k8s.io load -i backend-v1.0.tar
sudo nerdctl -a /run/k3s/containerd/containerd.sock -n k8s.io load -i frontend-v1.0.tar
sudo nerdctl -a /run/k3s/containerd/containerd.sock -n k8s.io load -i proxy-v1.0.tar
# Deploy to k3s
echo "Deploying"
kubectl delete namespace orders
kubectl create namespace orders
kubectl delete secret dynatrace-otelcol-dt-api-credentials -n orders
kubectl delete configmap dynatrace-otel-collector-config -n orders
kubectl create secret generic dynatrace-otelcol-dt-api-credentials -n orders --from-literal=DT_API_ENDPOINT="https://$DT_ENDPOINT" --from-literal=DT_API_TOKEN="$DT_TOKEN"
kubectl apply -f deployments/collector-configmap.yaml
kubectl apply -f deployments/deployment-jaeger.yaml
kubectl apply -f deployments/deployment-collector.yaml
kubectl apply -f deployments/deployment-backend.yaml
kubectl apply -f deployments/deployment-frontend.yaml
kubectl apply -f deployments/deployment-proxy.yaml
kubectl set env deployment/backend -n orders UPDATE_TIME="$(date)"
kubectl set env deployment/frontend -n orders UPDATE_TIME="$(date)"
kubectl set env deployment/proxy -n orders UPDATE_TIME="$(date)"
kubectl set env deployment/jaeger -n orders UPDATE_TIME="$(date)"
kubectl set env deployment/dynatrace-otel-collector-deployment -n orders UPDATE_TIME="$(date)"
rm -f backend-v1.0.tar frontend-v1.0.tar proxy-v1.0.tar
echo "Setup complete."

