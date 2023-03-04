Title: GKE Safely Drain a Nodepool without pod disruptions
Date: 2023-03-04 14:06
Author: Sam Stoelinga
Category: K8s
Tags: k8s, kubernetes, gke
Slug: gke-safe-nodepool-drain

GKE/K8s wasn't originally designed for workloads that spin up single pods
and want those pods to stay up and running on the same node
for very time. That doesn't mean those kind of workloads
aren't running on GKE. In fact, there are large GKE ML/batch platform workloads
running in production that have these characteristics.

This post will show how to decomission / destroy / decomission a nodepool
that's running pods that should not be disrupted. The requirements for our
decomission of nodepool is as follows:

* Any node that's running a batch job pod should stay up for as long
  as the batch job is running
* The max lifetime of batch job pod is 16 days
* The nodepool should automatically scale back to 0 after all batch job pods
  have finished running
* New pods should not trigger the nodepool that's being decomissioned to scale
  up again

## How to safely drain the node without pod disruptions?
The approach we will be taking is using the new GKE nodepool taint feature.
This feature allows us to taint all existing nodes in the nodepool and
also apply the taint on any newly added nodes.

Let's try this feature on the nodepool named `default-pool` in the cluster `test-drain`:
```sh
export POOL=default-pool
export CLUSTER=test-np-upgrades
gcloud container nodepools update $POOL --cluster $CLUSTER \
  --node-taints upgrade=true:NoSchedule
```
Note: You might have to set a zone or region using `gcloud config set compute/region us-central1`.

You would get the following error if cluster autoscaler is enabled on the nodepool:
```
ERROR: (gcloud.container.node-pools.update) ResponseError: code=400, message=Updates for 'taints' are not supported in node pools with autoscaling enabled (as a workaround, consider temporarily disabling autoscaling or recreating the node pool with the updated values.).
```
In our case the nodepools all have cluster autoscaler enabled since this is a ML/batch
platform. So disabling autoscaler isn't an option.

You might be about to give up but do not! Let's carefully read the error
message. It says as a workaround consider **temporarily** disabling autoscaling.

Let's give that a try, disable autoscaler, apply taints, enable autoscaler again.
Run the following commands:
```sh
gcloud container node-pools update $POOL \
  --cluster $CLUSTER --no-enable-autoscaling 
gcloud container node-pools update $POOL \
  --cluster $CLUSTER --node-taints upgrade=true:NoSchedule
gcloud container node-pools update $POOL \
  --cluster $CLUSTER --enable-autoscaling --max-nodes 1000 --min-nodes 0
```
The `--max-nodes` value doesn't matter because the nodepool got tainted so it will never scale up again.

So looks like this workaround is working well to taint all nodes in a nodepool

## Why not use kubectl cordon or taint?
The issue with that approach is that it will cause the nodepool to scale
back up again from 0 to 1 because of cluster autoscaler. The cluster
autoscaler does not try to scale up again if the taint is set using
the GKE API. This is likely an implementation detail of how the
cluster autoscaler behaves on GKE.

## Verifying this meets our requirements
The test scenario is as follows. Before applying the taints, 4 pods were scheduled
and running that caused 4 nodes to be scaled up. So right now I still expect those 4 nodes
to be there. 

Verify the pods and nodes are still running:
```
kubectl get pods -o wide
```

Returns the following:
```
NAME   READY   STATUS   NODE
pod1   1/1     Running  gke-test-np-upgrades-default-pool-f9fd8128-cd6h
pod2   1/1     Running  gke-test-np-upgrades-default-pool-f9fd8128-tdsf
pod3   1/1     Running  gke-test-np-upgrades-default-pool-a6056569-c577
pod4   1/1     Running  gke-test-np-upgrades-default-pool-a6056569-dqff
```
So that looks good.

Let's try spinning up another pod that's targeting this tainted
nodepool.

Create a file named `pod5.yaml` with the following content:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod5
spec:
  nodeSelector:
    cloud.google.com/gke-nodepool: default-pool
  containers:
  - name: sleepy
    image: gcr.io/google_containers/pause-amd64:3.2
    resources:
      requests:
        memory: "2000Mi"
```

Create the pod:
```sh
kubectl apply -f pod5.yaml
```

Check to ensure cluster autoscaler won't scale up the nodepool. Run the following:
```sh
kubectl describe pod pod5
```

You should see this included in the output:
```sh
Status: Pending
..
Warning  FailedScheduling   default-scheduler   0/4 nodes are available: 4 node(s) had taint {upgrade: true}, that the pod didn't tolerate.
Normal   NotTriggerScaleUp  cluster-autoscaler  pod didn't trigger scale-up: 2 max node group size reached
```
This shows that the pod is pending and not triggering a scale up event. This is
great and exactly what was desired.

Now, let's verify the nodepool scales down automatically all the way to 0 when all
pods are deleted.

Delete all the batch jobs:
```
kubectl delete pod pod1 pod2 pod3 pod4
```
Note that in a normal situation you would wait for the pods to finish execution
instead of having to delete them. Once finished, the pod automatically is deleted
and autoscaler does the same scale down logic.

Wait for 10 to 15 minutes and then run:
```sh
kubectl get nodes
```

In my case, there seems to be 1 node still running. You might wonder why that is?
It turns out that kube-dns and other GKE system services are still running on
one of the nodes and are preventing the cluster autoscaling from scaling down.
You can solve this by following my blog post on [moving GKE
system services to a dedicated nodepool](
https://samos-it.com/posts/gke-system-services-kube-dns-dedicated-nodepool.html).

If you already moved your GKE system services then you would have seen 0 nodes left.

So this concludes that the GKE nodepool tainting feature is an effective way to
safely decomission nodepools without disrupting existing pods.

This was tested on GKE 1.21 and behavior is not guaranteed to stay the same in future releases
