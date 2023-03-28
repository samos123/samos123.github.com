Title: GKE custom OSS K8s cluster autoscaler
Date: 2021-03-12 22:02
Modified: 2023-03-27 19:13
Author: Sam Stoelinga
Category: K8s
Tags: k8s, kubernetes, gke, autoscaler
Slug: gke-custom-oss-cluster-autoscaler

Update 2023-03-27: Added instructions for clusters using Workload Identity

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
* Bug in the GKE bundled autoscaler that isn't fixed yet but is already
  fixed in the OSS K8s cluster autoscaler

## How?
You're stubborn and persistent and still believe you have to do this then
let's look at how this can be done.

### 1. Create a GKE cluster without cluster autoscaler enabled
```bash
PROJECT_ID=$(gcloud config get-value project)
GKE_VERSION="1.25.6-gke.1000"
gcloud container clusters create no-autoscaler \
  --no-enable-autoscaling \
  --region us-central1 --node-locations us-central1-a \
  --release-channel None \
  --cluster-version $GKE_VERSION \
  --workload-pool $PROJECT_ID.svc.id.goog
```

## 2. Configure Workload Identity
Create a serviceAccount to be used for cluster autoscaler:
```sh
gcloud iam service-accounts create k8s-cluster-autoscaler
```

Grant permission to the service account:
```sh
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member "serviceAccount:k8s-cluster-autoscaler@$PROJECT_ID.iam.gserviceaccount.com" \
    --role "roles/compute.instanceAdmin.v1"
```

Allow K8s Service Account to use the Google Service Account:
```sh
gcloud iam service-accounts add-iam-policy-binding k8s-cluster-autoscaler@$PROJECT_ID.iam.gserviceaccount.com \
    --role roles/iam.workloadIdentityUser \
    --member "serviceAccount:$PROJECT_ID.svc.id.goog[kube-system/cluster-autoscaler-gce-cluster-autoscaler]"
```


### 3. Deploy the K8s cluster autoscaler using helm
Create a file named `values.yaml` that contains the config for autoscaler:
```yaml
autoscalingGroupsnamePrefix:
  # The name prefix of of the GCE managed instance groups
  # this will be different in your case and in general follows this pattern
  # gke-$CLUSTER_NAME (in my case cluster name is no-autoscaler)
  - name: gke-no-autoscaler
    minSize: 1
    maxSize: 10

autoDiscovery:
  # the cluster name of the GKE cluster, change to your cluster name
  clusterName: no-autoscaler

extraArgs:
  # I had to do this to prevent this error:
  # lock is held by gke-2ff9d20265d64621837d-14fa-96a3-vm and has not yet expired
  # failed to acquire lease kube-system/cluster-autoscaler
  leader-elect: false

cloudProvider: gce
image:
  # Change the image tag version to match the GKE version. So if running
  # GKE 1.25.6 make sure this version also is 1.25.0. there is no 1.25.6 image
  tag: v1.25.0
```

Deploy K8s cluster autoscaler with the just created `values.yaml`:
```bash
helm repo add autoscaler https://kubernetes.github.io/autoscaler
helm install cluster-autoscaler autoscaler/cluster-autoscaler -f values.yaml --namespace kube-system
```

You should now have a K8s cluster autoscaler working. Try spinning up many
pods with high resource requests and the cluster should automatically add
more nodes.
