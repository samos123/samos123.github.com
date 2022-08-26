Title: GKE GPU timesharing and resource quotas experiment
Date: 2022-08-26 22:02
Author: Sam Stoelinga
Category: K8s
Tags: k8s, kubernetes, gke, gpu, timesharing
Slug: gke-gpu-timesharing-resource-quotas

You only got a few GPUs and want to pretend to your end-users that you got
many? Then GKE GPU timesharing might just be the feature for you. In this
blog post you will learn:

1. Creating a GKE nodepool with timesharing enabled
2. Configure GPU based ResourseQuotas on multiple namespaces
3. How it's possible to request 4 GPUs in different namespaces even though there is only a single physical GPU


## Creating the cluster and nodepool
Create a cluster that meets the requirements of timesharing. At the time of
writing the blog post this requires using the rapid release channel.
This creates a cluster with a default CPU only nodepool using e2-medium.
System services will run on the default CPU only nodepool.

```
gcloud container clusters create gpu-gpu-timesharing \
  --region us-central1 --node-locations=us-central1-a \
  --machine-type e2-medium --max-nodes=3 --min-nodes=1 \
  --enable-autoscaling --release-channel rapid \
  --shielded-integrity-monitoring --shielded-secure-boot
```
 

Create the T4 GPU nodepool with timesharing enabled
```
gcloud container node-pools create gpu-time-sharing \
    --cluster=gke-gpu-timesharing \
    --machine-type=n1-standard-4 \
    --num-nodes=1 \
    --region=us-central1 \
    --node-locations=us-central1-a \
    --accelerator=type=nvidia-tesla-t4,count=1,gpu-sharing-strategy=time-sharing,max-shared-clients-per-gpu=8 \
    --shielded-secure-boot --shielded-integrity-monitoring
```

Install the nvidia GPU device drivers:
```
kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/container-engine-accelerators/master/nvidia-driver-installer/cos/daemonset-preloaded-latest.yaml
```

You should now have a working GKE cluster with 2 nodepools. A CPU only nodepool and a GPU nodepool with 1 GPU node that has 1 T4.
This T4 GPU can be used by up to 8 clients at the same time. So it could be used by 8 pods each
requesting 1 GPU or it could be used by 2 pods each requesting 4 GPUs.


## Creating  the namespaces and resource quotas
The example will use 2 fictional tenants: tenant-a and tenant-b.

Create the namespaces for both tenants:
```
kubectl create ns tenant-a
kubectl create ns tenant-b
```


Create a quota for tenant-a
```
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ResourceQuota
metadata:
  name: test-gpu-quota-1
  namespace: tenant-a
spec:
  hard:
    requests.nvidia.com/gpu: 1
    limits.nvidia.com/gpu: 1
    requests.cpu: 1
    limits.cpu: 1
EOF
```

Create a quota for tenant-b
```
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ResourceQuota
metadata:
  name: test-gpu-quota-1
  namespace: tenant-b
spec:
  hard:
    requests.nvidia.com/gpu: 10
    limits.nvidia.com/gpu: 10
    requests.cpu: 2
    limits.cpu: 2
EOF
```

# Creating a GPU pod in tenant-a and tenant-b
Let's create 4 pods in tenant-a and 4 pods in tenant-b where each pod
is requesting a single GPU.


The job that we will use in both tenants.
```
cat > gpu-deployment.yml << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cuda-simple
spec:
  replicas: 4
  selector:
    matchLabels:
      app: cuda-simple
  template:
    metadata:
      labels:
        app: cuda-simple
    spec:
      containers:
      - name: cuda-simple
        image: nvidia/cuda:11.0.3-base-ubi7
        command:
        - bash
        - -c
        - |
          /usr/local/nvidia/bin/nvidia-smi -L; sleep 300
        resources:
          limits:
            nvidia.com/gpu: 1
EOF
```

launch it in tenant-a and tenant-b
```
kubectl apply -f gpu-deployment.yml -n tenant-a
kubectl apply -f gpu-deployment.yml -n tenant-b
```

You should see 1 pod running in tenant-a:
```
kubectl get pods -n tenant-a
```
this demonstrates that resourcequotas are effective
and able to limit GPUs that are timeshared.

You should see 4 pods running in tenant-a:
```
kubectl get pods -n tenant-b
```

Verify that pods in both tenant-a see the whole GPU being usable
```
kubectl exec -n tenant-a deploy/cuda-simple -ti -- sh
nvidia-smi
exit
```

Verify that pods in tenant-b  see the whole GPU being usable
```
kubectl exec -n tenant-b deploy/cuda-simple -ti -- sh
nvidia-smi
exit
```

You can also take a look at the GPU node to see that it will
report having 8 GPU devices even though it only has a single GPU
attached to the VM. This is due to the fact of timesharing being
enabled with the setting `max-shared-clients-per-gpu=8`. 

Run the following to get node details of the GPU nodes with tesla t4s
```
kubectl get node -l cloud.google.com/gke-accelerator=nvidia-tesla-t4 -o yaml
```

You should see something like this in the output:
```
    allocatable:
      attachable-volumes-gce-pd: "127"
      cpu: 3920m
      ephemeral-storage: "47093746742"
      hugepages-1Gi: "0"
      hugepages-2Mi: "0"
      memory: 12663300Ki
      nvidia.com/gpu: "1"
      pods: "110"
```


## Summary
Demonstrated how to use timesharing GPUs in GKE and verified that each tenant
will think they're getting the whole GPU even when they are being shared.
We are able to limit how much GPUs a single tenant can request by applying
resource quotas. GPU timesharing is a great way to reduce costs of GPUs when the
GPU utilization of a single tenant/user is low.
