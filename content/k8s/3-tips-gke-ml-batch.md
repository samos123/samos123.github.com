Title: 3 tips for GKE ML/batch workloads
Date: 2023-03-05 19:36
Author: Sam Stoelinga
Category: K8s
Tags: k8s, kubernetes, gke
Slug: 3-tips-gke-ml-batch-workloads

There has been an influx of large batch and ML training workloads on GKE. I've personally
had the please of working with one of those workloads. The things that
batch and ML workload often require from GKE are the following:

* Minimize pod disruptions since pods often can't simply be restarted on another node
* A single pod might need to stay running for many days
* Only spin up VM resources when a large job is launched and scale to 0 when job is done -> Cluster Autoscaler

## Top 3 tips for Batch ML workloads

1. Move your GKE system services to a separate nodepool

    You should create a separate nodepool for system services and run your batch/ML job
    in it's own nodepool. The largest benefit is this will allow you to 
    scale down your most expensive GPU/large VM nodepool back to 0. Otherwise, there might
    be a teeny-tiny kube-dns pod on your very expensive n2-highmem-128 VM preventing it to be removed
    by the autoscaler.

    Read my blog post on [how to move your GKE system services to a separate nodepool](
    https://samos-it.com/posts/gke-system-services-kube-dns-dedicated-nodepool.html)

2. Utilize release channels but prevent upgrades to the nodepools and minor release upgrades to control plane

    You can continiously set up a new 180 day maintenance exclusion using the
    `no_minor_or_node_upgrades` scope. This will prevent the control
    plane from going through a minor version upgrade and also prevent
    nodepools from being upgraded. (Unverified, planning to verify soon and write
    a blog post on this)

3. Create new nodepools instead of upgrading

    Do not rely on GKE upgrades instead create a new nodepool and safely decommission the old nodepool.

    GKE upgrades will forcefully drain your nodes causing pod disruptions. GKE only respects your
    pod disruption budget for up to 1 hour, however Batch/ML pods often require it be respected
    multiple days.

    So instead it's better to
    create a new nodepool with the new version and taint the old nodepool so no new pods get scheduled
    to the old nodepool. Eventually the old nodepool will get to 0 and then it's safe to delete it.

    View this [blog post to learn how to safely decommission a nodepool without pod disruptions](
    https://samos-it.com/posts/gke-safe-nodepool-drain.html)
