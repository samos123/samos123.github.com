Title: GKE docker registry with HTTP proxy
Date: 2021-05-21 10:52
Author: Sam Stoelinga
Category: K8s
Tags: k8s, kubernetes, gke, proxy, registry
Slug: gke-docker-registry-http-proxy

You are at one of those places that requires you to use a proxy to access
your company wide Docker registry. Sometimes HTTP proxies are used to supposedly
improve security or to workaround IP based rate limits.
Well good luck, you're in for a ride on how to do this with GKE and I've made
this easier for you by documenting the steps needed to get this to work on GKE.

The high-level solution is to configure HTTP proxy environment variables for
the docker daemon running on the GKE nodes. This is done by following these
steps:

1. Create a script that places a file with proxy config under
   under `/etc/systemd/system/docker.service.d/` on the
   GKE nodes.
2. Create a K8s DaemonSet that runs the script on each node


## Creating the docker HTTP proxy script as ConfigMap
There are 2 things the script needs to do:

1. Place the docker HTTP proxy configuration under `/etc/systemd/system/docker.service.d/`
2. Reload systemd configuration and restart docker daemon

Now create the file called `proxy-inject-cm.yml` with the following content:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: proxy-injector
  namespace: kube-system
data:
  proxy-injector.sh: |
    #!/bin/bash
    
    cat > /mnt/etc/systemd/system/docker.service.d/http-proxy.conf << EOF
    [Service]
    Environment="HTTP_PROXY=http://sams-proxy:3128"
    EOF
    nsenter --target 1 --mount systemctl daemon-reload
    nsenter --target 1 --mount systemctl restart docker
```

Note that you will need to edit this line in `proxy-inject-cm.yml`:
```text
    Environment="HTTP_PROXY=http://sams-proxy:3128"
```
You need to change `HTTP_PROXY=http://sams-proxy:3128` to your actual HTTP
proxy.


Create the K8s configmap:
```bash
kubectl apply -f proxy-inject-cm.yml
```

## Creating the proxy injector DaemonSet
The DaemonSet simply runs the script on each node during node startup.
Create a file called `proxy-injector-dm.yml`:

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: proxy-injector
  namespace: kube-system
  labels:
    app: proxy-injector
spec:
  selector:
    matchLabels:
      app: proxy-injector
  template:
    metadata:
      labels:
        app: proxy-injector
    spec:
      hostPID: true
      initContainers:
      - name: proxy-injector
        image: ubuntu
        command:
          - /usr/local/bin/proxy-injector.sh
        volumeMounts:
          - name: etc
            mountPath: "/mnt/etc"
          - name: bins
            mountPath: "/usr/local/bin"
        securityContext:
          privileged: true
      volumes:
      - name: etc
        hostPath:
          path: /etc
      - name: bins
        configMap:
          name: proxy-injector
      containers:
      - name: pause
        image: gcr.io/google_containers/pause
      priorityClassName: system-node-critical
      tolerations:
        - effect: NoSchedule
          operator: Exists
```

Before you execute this next command, please note that this will cause
disruption to existing pods because docker is force restarted. So be extra
careful before running it. Create the K8s DaemonSet:

```bash
kubectl apply -f proxy-injector-dm.yml
```

## Summary
We have rolled out a daemonset that modifies the docker HTTP proxy settings.
Your GKE nodes will now use the HTTP proxy when pulling down images. Note
that you would need to create a similar DaemonSet or simple bash script
that SSHs into the GKE nodes to remove the proxy settings because simply
delete the DaemonSet will leave the existing proxy settings.
