# Microk8s local setup

## About

This is my Kind setup for my Mac Silicon

What it does:

1. Asks for a Dynatrace token
2. Containerizes a small Ruby app
3. Pushes the app
4. Pushes the Dynatrace Otel Collector
5. Sends OTel data to Dynatrace

## Install Podman Desktop and Minikube

Visit the podman release page and install the latest

[Podman on Github](https://github.com/containers/podman/releases)

Visit the Minkube release page, grab the latest, and put it in /usr/local/bin/

[Minikube on Github](https://github.com/kubernetes/minikube/releases)


```
git clone https://github.com/mreider/k8s.git
cd k8s
./setup.sh

```

Enter your Dynatrace API endpoint
Enter your Dynatrace Token:

That's it!


