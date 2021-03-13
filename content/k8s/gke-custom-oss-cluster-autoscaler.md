Title: GKE custom OSS K8s cluster autoscaler
Date: 2021-03-12 22:02
Author: Sam Stoelinga
Category: K8s
Tags: k8s, kubernetes, gke, autoscaler
Slug: gke-custom-oss-cluster-autoscaler

This blog post described how to deploy your own K8s cluster autoscaler instead
of the cluster autoscaler that's bundled with GKE. This can be helpful in the
rare case that the bundled GKE cluster autoscaler doesn't work for you.

Note that the GKE bundled cluster autoscaler is vastly different from the OSS
cluster autoscaler. GKE has done optimizations to make it perform better and
scale based on cost. So in general you are strongly recommended to use the
bundled GKE cluster autoscaler.

## Why?
Now you might ask why would I do this instead of just using the bundled GKE
cluster autoscaler? The short answer is you shouldn't unless you:

* Require to tweak parameters of the K8s cluster autoscaler that are not
  exposed to you. Ask yourself are tweaking these parameters really that
  important?
* Hit scaling limitations with the bundled GKE cluster autoscaler when
  running more than 5,000 nodes per cluster. Note that K8s OSS cluster
  autoscaler would likely also hit scaling limitations. Instead I would
  recommend working closely with the Google team when you're at that
  scale to see what options are available.

## How?
You're stubborn and persistent and still believe you have to do this then
let's look at how this can be done.

### 1. Create a GKE cluster without cluster autoscaler enabled
```bash
gcloud container clusters create no-autoscaler \
  --no-enable-autoscaling \
  --region us-central1 --node-locations us-central1-a \
  --cluster-version  1.17.17-gke.2800
```


### 2. Deploy the K8s cluster autoscaler using helm
Create a file named `values.yaml` that contains the config for autoscaler:
```yaml
autoscalingGroupsnamePrefix:
  # The name prefix of of the GCE managed instance group
  # this will be different in your case
  - name: gke-no-autoscaler
    minSize: 1
    maxSize: 10

autoDiscovery:
  # the cluster name of the GKE cluster, change to your cluster name
  clusterName: no-autoscaler

cloudProvider: gce
image:
  # Change the image tag version to match the GKE version. So if running
  # GKE 1.17 make sure this version also is 1.17
  tag: v1.17.3
```

Deploy K8s cluster autoscaler with the just created `values.yaml`:
```bash
helm repo add autoscaler https://kubernetes.github.io/autoscaler
helm install cluster-autoscaler autoscaler/cluster-autoscaler -f values.yaml
```

You should now have a K8s cluster autoscaler working. Try spinning up many
pods with high resource requests and the cluster should automatically add
more nodes.
