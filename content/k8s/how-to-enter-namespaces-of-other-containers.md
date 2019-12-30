Title: How to enter network namespaces of other containers from a pod in K8s?
Date: 2019-12-30 10:02
Author: Sam Stoelinga
Category: K8s
Tags: k8s, kubernetes, network, namespace
Slug: enter-namespace-of-other-containers-from-a-pod

You might be in a situation where you need to troubleshoot the networking
stack on a container where you don't have the tools necessary. Or you might
need to figure out which veth belongs to a container. For both these
scenarios you will need to be able to get into the network namespace of
another container. This blog post describes how to get into the network
namespace of another container by running a privileged container on
the same K8s node.


At a high-level the following steps are needed:

1. Deploy a privileged container
2. Find out the PID of the target container
2. Use `nsenter` to enter namespace of target container and relate veth

### 1. Deploy a privileged container
First, we'll need to deploy a container that uses host networking and has
privileges to enter namespaces. Note that this container has full access to
node host networking stack and all other containers, potential security
concern.

The image that we'll be using is `samos123/docker-toolbox`, which can be found
on [GitHub:samos123/docker-toolbox](https://github.com/samos123/docker-toolbox).

Create the file `debug-pod.yaml` with the following contents:

    :::yaml
    apiVersion: v1
    kind: Pod
    metadata:
      name: debug-pod
      labels:
        app: debug
    spec:
      hostNetwork: true
      hostPID: true
      containers:
      - name: debug-pod
        image: samos123/docker-toolbox:latest
        command: [ "/bin/bash", "-c", "--" ]
        args: [ "while true; do sleep 30; done;" ]
        volumeMounts:
          - name: dockersock
            mountPath: "/var/run/docker.sock"
        securityContext:
          privileged: true
          capabilities:
            add: ["NET_ADMIN"]
      volumes:
      - name: dockersock
        hostPath:
          path: /var/run/docker.sock


Create the pod by running:

    :::bash
    kubectl apply -f debug-pod.yaml

Verify you can access docker of the host:

    :::bash
    docker ps

## 2. Find the PID of the target container
The target container is the container of which you want to find the namespace
and corresponding interface. You can use `docker ps --filter name=nginx` to
list all containers that have the nginx in their name.

Now use the container ID to get the PID of the container:

    :::bash
    pid=$(docker inspect --format '{{.State.Pid}}' $containerID)

## 3. Enter the container network namespace
`nsenter` can be used to enter the namespace using the PID:

    :::bash
    nsenter -t $pid -n ip a

You will notice that there is an `eth0@ifX` interface inside the container
network namespace. The `X` tells you the interface index on the host network.
This index can then be used to figure out which veth belongs to the container.

Run the following commands to find the veth interface:

    :::bash
    ifindex=$(nsenter -t $pid -n ip link | sed -n -e 's/.*eth0@if\([0-9]*\):.*/\1/p')
    veth=$(ip -o link | grep ^$ifindex | sed -n -e 's/.*\(veth[[:alnum:]]*@if[[:digit:]]*\).*/\1/p')
    echo $veth


I've created a script in the following repo: [samos123/docker-veth](https://github.com/samos123/docker-veth)
