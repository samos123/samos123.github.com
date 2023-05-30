Title: Deploying Stable Diffusion Web UI on GKE Autopilot
Date: 2023-05-30 19:36
Author: Sam Stoelinga
Category: ML
Tags: ml, k8s, stable-diffusion
Slug: deploying-stable-diffusion-gke-autopilot

Deploying Stable Diffusion WebUI on K8s can be challenging, but no more.
Learn how to do it by:

1. Creating a GKE autopilot cluster
2. Deploying AUTOMATIC1111 Stable Diffusion Web UI
3. Accessing the UI through port forwarding


Create a GKE Autopilot cluster:
```
gcloud container clusters create-auto sd \
    --region us-central1
```

Create a file named `stable-diffusion.yaml` with the following content:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: stable-diffusion-webui
spec:
  replicas: 1
  selector:
    matchLabels:
      app: stable-diffusion-webui
  template:
    metadata:
      labels:
        app: stable-diffusion-webui
    spec:
      nodeSelector:
        cloud.google.com/gke-accelerator: "nvidia-tesla-t4"
        # remove this node selector if you don't want to use spot
        cloud.google.com/gke-spot: "true"
      containers:
      - name: sd
        image: ghcr.io/samos123/stable-diffusion-webui
        resources:
          limits:
            nvidia.com/gpu: 1
          requests:
            cpu: "3500m"
            memory: "14Gi"
```

Create the deployment:
```
kubectl apply -f stable-diffusion.yaml
```

Access the Stable Diffusion WebUI by forwarding ports:
```
kubectl port-forward deployment/stable-diffusion-webui 7860:7860
```

In your browser go to the following URL:
[http://localhost:7860](http://localhost:7860)

You should now see Stable Diffusion Web UI like this:
```

```
