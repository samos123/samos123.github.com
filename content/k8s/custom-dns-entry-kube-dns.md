Title: Custom DNS entry with KubeDNS stubdomain
Date: 2021-03-11 22:02
Author: Sam Stoelinga
Category: K8s
Tags: k8s, kubernetes, gke, dns
Slug: custom-dns-entry-kube-dns-stubdomain-coredns

An example use case that I've seen is where you have a K8s service exposed
on the ClusterIP and you want to make that service accessible over a domain
name that you don't control.


You can do to the following steps to set this up:

1. Deploy CoreDNS with custom DNS entries
2. Configure kube-dns to use stubDomain that points to CoreDNS

## 1. Deploying CoreDNS with custom DNS entries
Create the namespace for coredns k8s resources:
```bash
kubectl create ns coredns
```

Create a file called `core-dns-cm.yaml` with the following content:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: coredns
  namespace: coredns
data:
  Corefile: |
    .:53 {
        errors
        health {
          lameduck 5s
        }
        ready
        cache 30
        log
        reload
        loadbalance
        file /etc/coredns/example.db example.org
    }
  example.db: |
    ; example.org test file
    example.org.            IN      SOA     sns.dns.icann.org. noc.dns.icann.org. 2015082541 7200 3600 1209600 3600
    example.org.            IN      NS      b.iana-servers.net.
    example.org.            IN      NS      a.iana-servers.net.
    example.org.            IN      A       10.200.0.1
```
In the configmap you definte the custom dns entries. In the example, the A
record for example.org has been overriden to point to 10.200.0.1. You would
change example.org and the specific DNS entries depending on your needs.

Create the configmap:
```bash
kubectl apply -f core-dns-cm.yaml
```

Create a file named `core-dns-deployment.yaml`:
```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: coredns
  namespace: coredns
  labels:
    k8s-app: coredns
    kubernetes.io/name: "CoreDNS"
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
  selector:
    matchLabels:
      k8s-app: coredns
  template:
    metadata:
      labels:
        k8s-app: coredns
    spec:
      containers:
      - name: coredns
        image: coredns/coredns:1.8.3
        imagePullPolicy: IfNotPresent
        resources:
          limits:
            memory: 170Mi
          requests:
            cpu: 100m
            memory: 70Mi
        args: [ "-conf", "/etc/coredns/Corefile" ]
        volumeMounts:
        - name: config-volume
          mountPath: /etc/coredns
          readOnly: true
        ports:
        - containerPort: 53
          name: dns
          protocol: UDP
        - containerPort: 53
          name: dns-tcp
          protocol: TCP
        securityContext:
          allowPrivilegeEscalation: false
          capabilities:
            add:
            - NET_BIND_SERVICE
            drop:
            - all
          readOnlyRootFilesystem: true
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
            scheme: HTTP
          initialDelaySeconds: 60
          timeoutSeconds: 5
          successThreshold: 1
          failureThreshold: 5
        readinessProbe:
          httpGet:
            path: /ready
            port: 8181
            scheme: HTTP
      dnsPolicy: Default
      volumes:
        - name: config-volume
          configMap:
            name: coredns
            items:
            - key: Corefile
              path: Corefile
            - key: example.db
              path: example.db
```

Create the deployment that uses the configmap:

```shell
kubectl apply -f core-dns-deployment.yaml
```

Create a file named `core-dns-svc.yaml`:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: coredns
  namespace: coredns
  labels:
    k8s-app: coredns
    kubernetes.io/cluster-service: "true"
    kubernetes.io/name: "CoreDNS"
spec:
  clusterIP: 10.0.6.177
  selector:
    k8s-app: coredns
  ports:
  - name: dns
    port: 53
    protocol: UDP
  - name: dns-tcp
    port: 53
    protocol: TCP
```
Notice that we set a static cluster IP so this blog post is easier to follow.
You will probably want to remove that and let it asign a random clusterIP and
note down the cluster IP. You will need the CoreDNS cluster IP in the next
step during configuring kube-dns.

Create the coredns k8s service:
```bash
kubectl apply -f core-dns-svc.yaml
```

## 2.  Configure kube-dns to use stubDomain that points to CoreDNS

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: kube-dns
  namespace: kube-system
data:
  stubDomains: |
        {"example.org" : ["10.0.6.177"]}
```
