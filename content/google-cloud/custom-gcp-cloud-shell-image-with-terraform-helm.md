Title: Custom GCP Cloud Shell image with Terraform and Helm
Date: 2019-06-10 13:01
Author: Sam Stoelinga
Category: Google Cloud
Tags: google cloud, cloudshell, terraform, helm
Slug: custom-GCP-Cloud-Shell-image-with-Terraform-Helm

Inpatient people who just want the end-result, please go to:
[GitHub: GCP Cloud Shell image with Terraform and Helm](https://github.com/samos123/gcp-terraform-cloud-shell)

Cloud Shell is one of the convenient features of Google Cloud providing
you with a secure CLI directly from the browser. The default image contains
almost all the tools you could wish for, but in some cases you might need
more. In this blog post, you will learn how to create a custom Docker image
for Google Cloud Shell that includes the Helm client and Terraform.

At a high-level you have to do 2 things:

1. Create and publish a Docker image
2. Configure your custom image to be used in Cloud Shell

### 1. Create and Publish custom Cloud Shell Docker image
In this section we're going to create new Docker image that's based on the
default Cloud Shell image and then publish created image to Google Cloud
Container Registry.

1. Let's start by creating a new repo and setting the project ID where the Docker image should be published:

        :::bash
        mkdir gcp-cloud-shell-custom-image
        cd gcp-cloud-shell-custom-image
        GCP_PROJECT_ID=your-project-ID

2. Now with your file editor of choice create a file named `Dockerfile` with the
following content:

        :::Dockerfile
        FROM gcr.io/cloudshell-images/cloudshell:latest
        
        ENV TERRAFORM_VERSION="0.11.10" \
            HELM_VERSION="v2.14.0"
        
        WORKDIR /tmp
        
        RUN curl https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip > terraform_${TERRAFORM_VERSION}_linux_amd64.zip && \
            unzip terraform_${TERRAFORM_VERSION}_linux_amd64.zip -d /bin && \
            wget -q https://storage.googleapis.com/kubernetes-helm/helm-${HELM_VERSION}-linux-amd64.tar.gz -O - | tar -xzO linux-amd64/helm > /usr/local/bin/helm && \
            chmod +x /usr/local/bin/helm && \
            rm -f terraform_${TERRAFORM_VERSION}_linux_amd64.zip

3. Build the Docker image:  
`docker build -t gcr.io/$GCP_PROJECT_ID/cloud-shell-image .`
4. Push the Docker image to Google Cloud Container Registry:  
`docker push gcr.io/$GCP_PROJECT_ID/cloud-shell-image:latest`  
Note: You will need to configure Docker to authenticate with gcr by following
the steps [here](https://cloud.google.com/container-registry/docs/pushing-and-pulling).

### 2. Configure Cloud Shell Image to use the published image
1. Go to [Cloud Shell Environment settings](https://console.cloud.google.com/cloudshell/environment/view)
2. Click on Edit
3. Click on "Select image from project"
4. In the Image URL field enter: `gcr.io/$GCP_PROJECT_ID/cloud-shell-image:latest`
5. Click "Save"

Now open a new Cloud Shell session and you should see that the new custom image is used.
