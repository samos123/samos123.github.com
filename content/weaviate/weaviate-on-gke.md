Title: Deploying Weaviate on GKE
Date: 2023-02-06 12:14
Author: Sam Stoelinga
Category: Weaviate
Tags: weaviate, gke
Slug: weaviate-on-gke

Weaviate has great docs on how to deploy on K8s using Helm, however
this guide is specifically focused on an end-to-end production deployment of
Weaviate on GKE. The following topics will be covered:

- Resource Planning: Estimating your desired Weaviate cluster size
- Recommended configuration for production cluster
- Creating and configuring your GKE cluster
- Deploying Weaviate with Helm
- Configuring Google as your OIDC provider for Weaviate

## 1. Estimating your desired Weaviate cluster size
Weaviate itself only consumes CPU, memory and disk. CPU impacts query and
import speed and memory impacts maximum amount of objects you can store.
Weaviate by default stores all vector objects in memory to be able to do
efficient vector search.

CPU: recommend giving at least 8 CPU per pod as a starting point

Memory: for this post we need to be able to store 100 million objects with 1536 dimensions, so that would
require `2 * 100,000,000 * 1536 * 4B = 1.23TB` of memory.

Assuming a replication factor of 3 and a database shards set to 9. Then that would mean
each node will host `3/9 = 1/3` of the total amount of objects. In that case each Weaviate node would
need to have at least `1.23TB * 1/3 = 410 GB` of memory.

Please also review the official Weaviate docs on
[resource planning](https://weaviate.io/developers/weaviate/concepts/resources).

Machine type: n2d-highmem-64 or other highmem shapes that have more than 410 GB of memory.

## 2. Production cluster configuration
Authentication: Production clusters should enable OIDC authentication for security
reasons. By default Weaviate is accessible to anyone. So anyone that can connect to
Weaviate is able to write, read or modify the schema. For this guide, Dex will be used
as the OIDC provider, however it's recommended to integrate with your existing OIDC
provider if you already have one.

High availability: Replication factor of 3 should be used such that
a single Weaviate node going down won't have an impact on your cluster.

Sharding: Shards should be set to 9 or higher because of our large dataset
and 1.23TB of memory being too large for most machine shapes.


## 3. Creating and configuring the GKE cluster
Based on the previous sections it's been clear that a 9 node GKE cluster
is needed and each node will be used in the n2d-highmem-64 machine shape.
Another approach could be to have more shards and use a smaller machine type.


Create the 9 node n2d-highmem-64 GKE cluster by running:
```sh
gcloud container clusters create weaviate \
  --disk-size 500GB --disk-type pd-ssd \
  --enable-shielded-nodes --shielded-integrity-monitoring \
  --shielded-secure-boot --image-type COS_CONTAINERD \
  --machine-type n2d-highmem-64 --num-nodes 9 \
  --region us-central1 --node-locations=us-central1-a \
  --release-channel stable
```
## Configure Google as OIDC provider for Weaviate

Steps for Creating the OAuth Consent Screen:

1. Go to console.cloud.google.com
2. Search for OAuth Consent Screen and click on it
3. Select User Type "Internal"
4. Only add email, profile and openid scopes
5. Save and Continue

Creating the OAuth 2.0 Client IDs
1. Go to console.cloud.google.com and search for "OAuth Credentials"
2. Click on "Credentials"
3. Click on "Create Credentials" and select "OAuth Client ID"
4. Select "Web Application" as application type
5. Click Create and copy paste the client ID and client secret somewhere safe
   because those will be needed in our Weaviate configuration

Note to self: need to check what should be added as authorized redirect URIs

## 4. Deploying Weaviate with Helm
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
