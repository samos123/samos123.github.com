Title: Deploying K8s on your laptop with minikube
Date: 2022-12-09 08:44
Author: Sam Stoelinga
Category: K8s
Tags: k8s, kubernetes, minikube
Slug: deploying-k8s-on-laptop-with-minikube

<iframe width="560" height="315" src="https://www.youtube.com/embed/AJVoHzb9KeQ" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

K8s on your laptop is helpful for initial development and testing environment. Minikube
makes it easy to get K8s deployed on your laptop. Let's get K8s installed by doing
the following:

1. Installing required tools: docker, minikube and kubectl
2. Deploying the minikube cluster with minikube start
3. Verifying you can deploy an application to your minikube cluster


## Installing required tools
Install docker by following the steps outlined [here](https://docs.docker.com/engine/install/ubuntu/#install-using-the-convenience-script):

```sh
# These steps are for ubuntu, you can follow steps for another distro if needed
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

Verify docker was installed succesfully by running:
```sh
docker run hello-world
```

Note if you get permission denied then you might need to add yourself to the docker
group. You can do this by running:
```sh
sudo usermod -a -G docker $USER
# make the change effective in current shell
newgrp docker
```

Install kubectl by following the steps outlined [here](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/):

```sh
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```


Install minikube by following the steps outlined [here](https://minikube.sigs.k8s.io/docs/start/):

```sh
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

All required tools have now been installed.

## Deploying K8s on your laptop
Follow steps of the "Start your cluster" section outlined [here](https://minikube.sigs.k8s.io/docs/start/):

```sh
minikube start
```

Verify that you can access your cluster by running:

```sh
kubectl get nodes
```

## Deploying an application to your K8s cluster
Let's deploy a simple web application by running:

```sh
kubectl create deployment hello-minikube \
  --image=kicbase/echo-server:1.0
```

You can expose the application on port 8080 by running:
```sh
kubectl expose deployment hello-minikube --type=NodePort --port=8080
minikube service hello-minikube
```
The `minikube service` command should have setup port forwarding for you and opened
a browser so you can access the application.
