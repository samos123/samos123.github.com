Title: GKE Nodepool Add Labels Without overwriting existing labels
Date: 2023-04-07 21:55
Author: Sam Stoelinga
Category: K8s
Tags: k8s, kubernetes, gke
Slug: GKE-nodepool-add-label-without-overwriting-existing-labels

GKE has a feature to add node labels to all nodes in the nodepool. GKE will add the label
to both the nodes already running in the cluster and also to newly added nodes.

You can use the feature like this:
```bash
gcloud container node-pools update my-node-pool \
  --cluster my-cluster --labels sam=test
```

That would add the label `sam: test` all your nodepools. The docs however do mention the
following: "The label update overwrites any existing labels on the node pool. If the
node pool has existing labels that you want to keep, you must include those
labels along with any new labels that you want to add."

Well that's lame. But worry not. It's relatively easy to script this with a few lines 
of bash.

Create a file named `gke-nodepool-add-label.sh` with the following content:
```bash
#!/usr/bin/env bash

set -x

CLUSTER_NAME="$1"
POOL_NAME="$2"
NEW_LABEL="$3"
LABELS=$(gcloud container node-pools describe $POOL_NAME \
         --cluster $CLUSTER_NAME --format "get(config.labels)" | tr ";" ",")
echo "Current labels: $LABELS"
gcloud container node-pools update $POOL_NAME \
  --cluster $CLUSTER_NAME --node-labels="$LABELS,$NEW_LABEL"
```

Make the file executable:
```bash
chmod +x gke-nodepool-add-label.sh
```

Now you can run the script like this to add a label without overwriting existing labels:
```bash
./gke-nodepool-add-label.sh my-cluster my-nodepool sam=test
```
