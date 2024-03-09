#!/bin/bash
brew install multipass kubectl
multipass launch --name microk8s-vm --memory 4G --disk 40G
multipass exec microk8s-vm -- /bin/bash -c "cd ~; [ \$(uname -m) = aarch64 ] && curl -Lo kind https://kind.sigs.k8s.io/dl/v0.22.0/kind-linux-arm64 && chmod +x kind && sudo mv kind /usr/local/bin/kind"
multipass exec microk8s-vm -- /bin/bash -c "sudo snap install kubectl --classic"
multipass exec microk8s-vm -- /bin/bash -c "sudo snap install docker --classic"
multipass exec microk8s-vm -- /bin/bash -c "git clone https://github.com/mreider/k8s.git && cd k8s"
multipass exec microk8s-vm -- /bin/bash -c "kind create cluster --name orders --config deployments/kind-config.yaml"
multipass exec microk8s-vm -- /bin/bash -c "kubectl cluster-info --context kind-orders"
multipass exec microk8s-vm -- /bin/bash -c "./setup.sh"