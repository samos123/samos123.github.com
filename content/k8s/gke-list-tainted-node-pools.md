Title: GKE list tainted nodepools with a specific taint
Date: 2023-03-09 19:47
Author: Sam Stoelinga
Category: K8s
Tags: k8s, kubernetes, gke
Slug: gke-list-tainted-nodepools-with-a-specific-taint

A use case for upgrades involved being able to list all the node pools
that have scaled down back to 0 and have a specific taint. This blog post
shows the commands you can use to get this information.

List the GKE nodepools that have been tainted with key=upgrade using GKE nodepool:
```
gcloud container node-pools list --cluster test-np-upgrades --flatten \
  --filter "config.taints.key=upgrade" --format 'value(name)'
```

For example in my case that returns:
```
default-pool
```

Now if you want to get the number of nodes in that nodepool you could run:
```sh
kubectl get nodes -l cloud.google.com/gke-nodepool=default-pool \
  --output name --no-headers | wc -l
```

