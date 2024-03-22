# My VM setup

I am logging in via

```
ssh -i ~/.ssh/google_key matthew.reider@quacker.eu
```

Install k3s

```
curl -sfL https://get.k3s.io | sh -
```

Install nerdctl

```
wget https://github.com/containerd/nerdctl/releases/download/v1.7.5/nerdctl-full-1.7.5-linux-amd64.tar.gz
tar -xvf nerdctl-full-1.7.5-linux-amd64.tar.gz
sudo mv libexec/* /usr/libexec/
sudo mv bin/* /usr/local/bin/
sudo mv lib/* /usr/local/lib/
sudo systemctl enable --now buildkit
```

Install k9s

```
wget https://github.com/derailed/k9s/releases/download/v0.32.4/k9s_linux_amd64.deb
sudo dpkg -i k9s_linux_amd64.deb 
```

Install kubectl

```
sudo apt-get install -y apt-transport-https gnupg2 curl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x ./kubectl
sudo mv ./kubectl /usr/local/bin/kubectl
mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown $USER:$USER ~/.kube/config
echo "export KUBECONFIG=~/.kube/config" >> ~/.bashrc
alias k3s-nerdctl='sudo nerdctl -a /run/k3s/containerd/containerd.sock'
source ~/.bashrc
```


I am syncing my local directory with:

(add to .bash_profile)

```
alias synck8s='rsync -avz -e "ssh -i ~/.ssh/google_key" --delete ~/k8s matthew.reider@quacker.eu:/home/matthew.reider/'
```