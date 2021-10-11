Title: GKE move system services (kube-dns, calico) to dedicated nodepool
Date: 2021-10-11 14:32
Author: Sam Stoelinga
Category: K8s
Tags: k8s, kubernetes, gke, dns
Slug: gke-system-services-kube-dns-dedicated-nodepool

GKE by default deploys kube-dns and other system services to any of your
nodepools. This is probably fine for most cases, but certain use cases
might require preventing system services from running on the same nodes as
your where your applications are running. This blog post provides instructions
on how to force kube-dns and other GKE system services onto a specific nodepool.

Some of the use cases this is helpful for:

- Cluster autoscaler unable to scale down a node that's running kube-dns
- Ensuring all capacity of a nodepool is usable instead of some of it being
  taken up by system services
- Preventing an application from possibly messing around with your system
  services

The easiest way to achieve this is to use `nodeSelector` and specify the label
of the system services nodepool. Let's take a look at how to modify the
deployments in the `kube-system` namespace and add a `nodeSelector`.

First, create the patch to add a nodeSelector by creating a file named
`nodeSelector-patch.yaml` with the following content:
```yaml
spec:
  template:
    spec:
      nodeSelector:
        cloud.google.com/gke-nodepool: system
```
Note: this assumes you have a nodepool named `system` where all your system
services will be deployed. You will need to adjust the name of the nodepool to
match your own environment. In my case I have multiple nodepools where 1 of the
nodepools is named `system`.

Now let's patch all the deployments in the `kube-system` namespace. Before
we do that let's take a quick look what's in the `kube-system` namespace:
```text
kubectl get deployment -n kube-system
NAME                                 READY   UP-TO-DATE   AVAILABLE   AGE
calico-node-vertical-autoscaler      1/1     1            1           342d
calico-typha                         1/1     1            1           342d
calico-typha-horizontal-autoscaler   1/1     1            1           342d
calico-typha-vertical-autoscaler     1/1     1            1           342d
config-management-operator           1/1     1            1           236d
event-exporter-gke                   1/1     1            1           342d
gke-oidc-envoy                       1/1     1            1           137d
kube-dns                             2/2     2            2           342d
kube-dns-autoscaler                  1/1     1            1           342d
l7-default-backend                   1/1     1            1           342d
metrics-server-v0.3.6                1/1     1            1           342d
```

That looks fine in my case, but your output may differ so make sure to review
before you add a nodeSelector to all these deployments.

Let's add the nodeSelector by patching all the deployments in `kube-system`:
```bash
kubectl get deployment -o NAME -n kube-system | xargs -n 1 -I {} kubectl patch {} -n kube-system --patch "$(cat nodeSelector-patch.yaml)"
```

In my case this was the output:
```text
deployment.apps/calico-node-vertical-autoscaler patched
deployment.apps/calico-typha patched (no change)
deployment.apps/calico-typha-horizontal-autoscaler patched
deployment.apps/calico-typha-vertical-autoscaler patched
deployment.apps/config-management-operator patched
deployment.apps/event-exporter-gke patched
deployment.apps/gke-oidc-envoy patched
deployment.apps/kube-dns patched (no change)
deployment.apps/kube-dns-autoscaler patched
deployment.apps/l7-default-backend patched
deployment.apps/metrics-server-v0.3.6 patched
```

Now the pods belonging to those deployment should be terminated in the old
nodepool and be running in the nodepool named `system`. You can verify this
by checking for example on which node the kube-dns pods are running:
```bash
kubectl get pods -n kube-system -l k8s-app=kube-dns -o wide
NAME                       READY   STATUS    RESTARTS   AGE   IP         NODE                                 NOMINATED NODE   READINESS GATES
kube-dns-848bb8c5d-fzh7h   4/4     Running   0          28m   10.4.3.3   gke-cluster-1-system-2db0a54b-jx6s   <none>           <none>
kube-dns-848bb8c5d-l72fh   4/4     Running   0          28m   10.4.4.3   gke-cluster-1-system-2db0a54b-ll3p   <none>           <none>
```
