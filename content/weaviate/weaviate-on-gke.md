Title: Deploying a Weaviate cluster on GKE
Date: 2023-02-07 12:14
Author: Sam Stoelinga
Category: Weaviate
Tags: weaviate, gke
Slug: weaviate-on-gke

Weaviate has great docs on how to deploy on K8s using Helm, however
this guide is specifically focused on an end-to-end deployment of
Weaviate on GKE with replication turned on. The following topics will be covered:

- Creating and configuring your GKE cluster
- Deploying Weaviate with Helm
- Tweaking the Weaviate helm values.yml

The Weaviate cluster deployed won't have authentication enabled and will
only allow you to run smaller datasets. A follow up blog post for production
ready Weaviate cluster that can host larger datasets will be posted later.

## 1. Creating and configuring the GKE cluster
For this sandbox environment, smaller nodes will be used to optimize for costs.
The e2-highmem-2 machine type is a great shape to get started with and comes
with 2 CPUs and 16 GB of memory but not recommended for production. 

For production with large datasets, you likely will need more memory, because Weaviate stores
the vectors in memory. For sandbox however the e2-highmem-2 should suffice.

Create a 3 node e2-highmem-2 GKE cluster by running:
```sh
gcloud container clusters create weaviate \
  --disk-size 500GB --disk-type pd-ssd \
  --enable-shielded-nodes --shielded-integrity-monitoring \
  --shielded-secure-boot --image-type COS_CONTAINERD \
  --machine-type e2-highmem-2 --num-nodes 3 \
  --region us-central1 --node-locations=us-central1-a \
  --release-channel stable
```


## 2. Deploying Weaviate with Helm
Verify you have access to the GKE cluster and that helm is installed:
```sh
kubectl get nodes
helm ls
```

Get the helm chart
```sh
helm repo add weaviate https://weaviate.github.io/weaviate-helm
helm show values weaviate/weaviate > values.yml
```

Modify `values.yaml` to utilize PD-SSD instead of default balanced disk by running:
```sh
sed -i 's/storageClassName: ""/storageClassName: "premium-rwo"/g' values.yml
```

Modify `values.yaml` to set Weaviate replication factor from 1 to 3 by running:
```sh
sed -i 's/^replicas:.*/replicas: 3/g' values.yml
```

Install using the helm chart:
```sh
helm install my-weaviate weaviate/weaviate --values values.yml
```

Verify that the statefulset has been created:
```
kubectl get statefulset
```
After a while, you should see that the statefulset will have 3 pods running.

You should now be able to access your website cluster on the LoadBalancer
external IP address. Run the following command to see the external IP:
```sh
kubectl get svc weaviate
```

You can access weaviate on the following URL: `http://$LB_EXTERNAL_IP`

Follow the [official Weaviate docs](https://weaviate.io/developers/weaviate/quickstart/end-to-end)
for a quickstart tutorial on how to use your deployed cluster.


Note that anyone on the internet by default can access that IP address

## (Optional) Restricting access to K8s cluster only
You have 2 choices if you do not want anyone on the internet to be able to access your cluster:

1. Change the K8s Service Type from LoadBalancer to Cluster IP, which we cover in this section
2. Enable Authentication for Weaviate which requires configuring an OIDC provider, which will be
   covered in another blog post

Changing the K8s Service Type of the Weaviate service to ClusterIP requires changing the
`values.yml` that was used during `helm install`.

Modify the `values.yml` by running the following command:
```sh
sed -i 's/type: LoadBalancer/type: ClusterIP/g' values.yml
```

Apply the change by executing `helm upgrade` with our updated `values.yml` file:
```sh
helm upgrade -f values.yml my-weaviate weaviate/weaviate
```

Verify the external-ip for the weaviate service is now gone by running:
```sh
kubectl get svc weaviate
```

Leave a comment if you have any other topics you want me to cover or if you
enjoyed this post.
