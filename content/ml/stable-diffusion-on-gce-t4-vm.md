Title: Deploying Stable Diffusion Web UI using Docker on GCE T4 VM
Date: 2023-05-23 19:36
Author: Sam Stoelinga
Category: ML
Tags: ml, docker, stable-diffusion
Slug: deploying-stable-diffusion-web-ui-with-docker-on-gce-t4-vm

A short guide on how to deploy Stable Diffusion Web UI on a Google Cloud
Compute Engine VM with 1 T4 GPU.

Creating the GCE VM with T4 using the Google Cloud Deep Learning Image:
```
export IMAGE_FAMILY="common-cu110-ubuntu-2004"
export ZONE="us-west1-b"
export INSTANCE_NAME="stable-diffusion"
export INSTANCE_TYPE="n1-standard-4"
gcloud compute instances create $INSTANCE_NAME \
        --zone=$ZONE \
        --image-family=$IMAGE_FAMILY \
        --image-project=deeplearning-platform-release \
        --maintenance-policy=TERMINATE \
        --accelerator="type=nvidia-tesla-t4,count=1" \
        --machine-type=$INSTANCE_TYPE \
        --boot-disk-size=120GB \
        --boot-disk-type=pd-ssd \
        --provisioning-model=SPOT \
        --instance-termination-action=STOP \
        --metadata="install-nvidia-driver=True"
```
Note: I'm using a spot VM to reduce cost. You might want to use a regular VM
instead by removing `--provisioning-model=SPOT` from the parameters.

The VM will come pre-installed with the nvidia drivers.

SSH into the VM:
```
gcloud compute ssh $INSTANCE_NAME
```

Verify that docker can use GPUs:
```
sudo docker run --rm --runtime=nvidia --gpus all nvidia/cuda:11.6.2-base-ubuntu20.04 nvidia-smi
```

Add yourself to the docker group so you don't have to sudo:
```
sudo usermod -aG docker $USER
newgrp docker
```

Build the docker image inside your VM:
```
git clone https://github.com/samos123/stable-diffusion-webui-docker
cd stable-diffusion-webui-docker
docker build -t sd-webui-docker .
```

Run the docker image:
```
DOCKER_BUILDKIT=1 docker run --name sd -p 7860:7860 -d --runtime=nvidia --gpus all sd-webui-docker
```

Verify that the Stable Diffusion web UI has launched succesfully:
```
docker logs sd
```

You should see something like this after ~30 seconds in the logs:
```
Running on local URL:  http://0.0.0.0:7860
```

Exit out of your SSH session by running:
```
exit
```

Setup port-forwarding to access the Stable Diffusion Web UI securely:
```
gcloud compute ssh $INSTANCE_NAME -- -NL 7860:localhost:7860
```
This is helpful for when your virtual machine doesn't have a public IP address or has
firewall rules setup.

You should now be able to acces the Stable Diffusion Web UI by going to the following
URL in your browser: [http://localhost:7860](http://localhost:7860)

Want to be even cooler? Learn [how to deploy Stable Diffusion on GKE autopilot](
https://samos-it.com/posts/deploying-stable-diffusion-gke-autopilot.html)
