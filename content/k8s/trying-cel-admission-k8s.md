Title: Trying ValidationAdmissionPolicy aka CEL Admission in K8s 1.26
Date: 2022-12-14 22:44
Author: Sam Stoelinga
Category: K8s
Tags: k8s, kubernetes, security
Slug: trying-cel-admission-control-validation-admission-policy

<iframe width="560" height="315" src="https://www.youtube.com/embed/OaXgy6BmV-k" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

CEL for admission control is a new 1.26 feature. With the feature, define
ValidationAdmissionPolicy to express your desired policy
and ValidationAdmissionPolicyBinding to assign the policy to e.g. a namespace.

This post has the following sections:

1. Creating a 1.26 cluster with ValidationAdmissionPolicy / CEL Admission enabled
2. Configure the policies
3. Verifying the policy is working as expected


## Creating a 1.26 cluster
We will be using kind to create a cluster with `ValidatingAdmissionPolicy` feature
gate enabled and runtimeConfig set to `admissionregistration.k8s.io/v1alpha1`.

Create a kind configuration file named `cluster.yaml` with the following content:
```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
featureGates:
  "ValidatingAdmissionPolicy": true
  runtimeConfig:
    "admissionregistration.k8s.io/v1alpha1": true
    nodes:
    - role: control-plane
      image: kindest/node:v1.26.0@sha256:691e24bd2417609db7e589e1a479b902d2e209892a10ce375fab60a8407c7352
```


Create the kind cluster by running:
```sh
kind create cluster --config cluster.yaml
```

Verify the cluster is up and running:
```sh
kubectl get nodes
```


## Configure the policies
For this example, we want a simple policy that prevents creating
a deployment that has the name `samos`.

Create a file named `cel-policy.yaml` with the following content:
```yaml
apiVersion: admissionregistration.k8s.io/v1alpha1
kind: ValidatingAdmissionPolicy
metadata:
  name: "example-policy"
spec:
  failurePolicy: Fail
  matchConstraints:
    resourceRules:
    - apiGroups:   ["apps"]
      apiVersions: ["v1"]
      operations:  ["CREATE", "UPDATE"]
      resources:   ["deployments"]
  validations:
    - expression: "object.metadata.name != 'samos'"
```

Create the policy by running:
```sh
kubectl apply -f cel-policy.yaml
```

Create a file named `cel-policy-binding.yaml` with the following content:
```sh
apiVersion: admissionregistration.k8s.io/v1alpha1
kind: ValidatingAdmissionPolicyBinding
metadata:
  name: "example-policy-test"
spec:
  policyName: "example-policy"
  matchResources:
    namespaceSelector:
      matchLabels:
        test: sam
```

The binding tells K8s to apply the ValidationAdmissionPolicy named example-policy
to any namespace that has the label `test=sam`.

Let's add the label `test=sam` to the default namespace by running:
```sh
kubectl label namespaces default test=sam
```

The policy should now be effective on the default namespace.

## Verify everything works

Create a file named `deployment.yaml` with the following content:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  namespace: default
  name: samos
  labels:
    app: nginx
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.14.2
        ports:
        - containerPort: 80
```

Try and create the deployment by running:
```sh
kubectl apply -f deployment.yaml
```

You should see an error like this:
```
The deployments "samos" is invalid: : ValidatingAdmissionPolicy 'example-policy' with binding 'example-policy-test' denied request: failed expression: object.metadata.name != 'samos'
```
