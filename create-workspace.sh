#!/usr/bin/env bash

set +x

# MACHINE_TYPE=a2-highgpu-1g
MACHINE_TYPE=g2-standard-8
gcloud compute instances create workspace-1 \
    --machine-type=$MACHINE_TYPE \
    --zone=us-central1-a \
    --provisioning-model=SPOT \
    --scopes=cloud-platform \
    --no-address \
    --disk=auto-delete=no,boot=yes,device-name=workspace-1,mode=rw,name=workspace-1,scope=zonal

