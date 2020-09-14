Title: Creating L2 connectivity between GCE VMs in GCP using VXLAN
Date: 2020-09-13 22:42
Author: Sam Stoelinga
Category: Google Cloud
Tags: google cloud, gcp, vxlan, networking, gce
Slug: gce-vm-vxlan-l2-connectivity

Cloud providers often prevent you from using L2 protocols such as ARP. These
protocols however are heavily used in existing software such as keepalived.
This can make it hard for to move certain workloads to the cloud.
This blog post demonstrates a method for creating L2 connectivity between
Virtual Machines (VMs) running in GCP. The method used relies on VXLAN to
create an L2 mesh between all the VMs. 

In this blog post, we'll be creating the 2 VMs, named `vm-1` and `vm-2`.
The VMs will be launched on the default VPC network. Each of the VMs
will have an additional `vxlan0` interface, this interface we'll
be using the `10.200.0.0/24` subnet.


### 1. Create the VMs
In this section you will create 2 Ubuntu 20.04 VMs

1. Let's start by creating `vm-1`

        :::bash
        gcloud compute instances create vm-1 \
                  --image-family=ubuntu-2004-lts --image-project=ubuntu-os-cloud \
                  --zone=us-central1-a \
                  --boot-disk-size 20G \
                  --boot-disk-type pd-ssd \
                  --can-ip-forward \
                  --network default \
                  --machine-type n1-standard-2

2. Repeat the same command creating `vm-2` this time:

        :::bash
        gcloud compute instances create vm-2 \
                  --image-family=ubuntu-2004-lts --image-project=ubuntu-os-cloud \
                  --zone=us-central1-a \
                  --boot-disk-size 20G \
                  --boot-disk-type pd-ssd \
                  --can-ip-forward \
                  --network default \
                  --machine-type n1-standard-2



3. Verify that SSH to both VMs is available and up. You might need o be patient.

        :::bash
        gcloud compute ssh root@vm-1 --zone us-central1-a --command "echo 'SSH to vm-1 succeeded'"
        gcloud compute ssh root@vm-2 --zone us-central1-a --command "echo 'SSH to vm-2 succeeded'"

### 2. Setup VXLAN mesh between the VMs
In this section, you will be creating the VXLAN mesh between `vm-1` and `vm-2`
that you just created.

1. Create bash variables that will be used for setting up the VXLAN mesh

        :::bash
        VM1_VPC_IP=$(gcloud compute instances describe vm-1 \
                       --format='get(networkInterfaces[0].networkIP)')
        VM2_VPC_IP=$(gcloud compute instances describe vm-2 \
                       --format='get(networkInterfaces[0].networkIP)')
        echo $VM1_VPC_IP
        echo $VM2_VPC_IP


2. Create the VXLAN device and mesh on `vm-1`

        :::bash
        gcloud compute ssh root@vm-1 --zone us-central1-a  << EOF
        set -x
        ip link add vxlan0 type vxlan id 42 dev ens4 dstport 0
        bridge fdb append to 00:00:00:00:00:00 dst $VM2_VPC_IP dev vxlan0
        ip addr add 10.200.0.2/24 dev vxlan0
        ip link set up dev vxlan0
        EOF

3. Create the VXLAN device and mesh on `vm-2`

        :::bash
        gcloud compute ssh root@vm-2 --zone us-central1-a  << EOF
        set -x
        ip link add vxlan0 type vxlan id 42 dev ens4 dstport 0
        bridge fdb append to 00:00:00:00:00:00 dst $VM1_VPC_IP dev vxlan0
        ip addr add 10.200.0.3/24 dev vxlan0
        ip link set up dev vxlan0
        EOF

4. Start a tcpdump on vm-1

        :::bash
        gcloud compute ssh root@vm-1 --zone us-central1-a
        tcpdump -i vxlan0 -n

5. In another session ping `vm-2` from `vm-1`  and take a look at tcpdump output. Notice the arp.

        :::bash
        gcloud compute ssh root@vm-1 --zone us-central1-a
        ping 10.200.0.3


### Summary
You have setup a VXLAN mesh between 2 VMs and can now easily repeat this to
more VMs. If you want to have a mesh between more VMs than for each additional
VM you would need to run `bridge fdp append`.

This blog post wouldn't have been possible without Mikal's blog on
[Setting up VXLAN on Google Compute Engine](https://www.madebymikal.com/setting-up-vxlan-on-google-compute-engine/).
