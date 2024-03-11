# Colima local setup

## About

This is my Colima setup for my Mac Silicon

What it does:

1. Asks for a Dynatrace token
2. Containerizes a small Python app
3. Pushes the app and the Dynatrace Otel Collector to local k3s
5. Sends OTel data to Dynatrace

## Install Colima

```
brew install colima
```

Then clone this repo and run the setup

```
git clone https://github.com/mreider/k8s.git
cd k8s
./setup.sh

```

Enter your Dynatrace API endpoint
Enter your Dynatrace Token:

That's it!


