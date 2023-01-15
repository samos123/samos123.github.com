Title: Preventing Privileged pods using Pod Security Admission / Standards
Date: 2023-01-14 18:38
Author: Sam Stoelinga
Category: K8s
Tags: k8s, kubernetes, security
Slug: Preventing-Privileged-pods-using-Pod-Security-Admission-Standards

In a Kubernetes cluster, a privileged pod is a pod that has been given
extended permissions beyond the default set of permissions. These extended
permissions can include the ability to access the host's network, devices,
and other sensitive resources. While privileged pods can be useful in
certain situations, they also present a significant security risk.

In this blog post, you will learn how to prevent privileged pods using Pod
Security Admission and applying Pod Security Standards. Note that using Pod Security
Policy has been deprecated in 1.23 and removed in 1.25.


## Introduction to Pod Security Standards and Pod Security Admission Controller

K8s comes with three predefined Pod Security Standards (PSS):

* Privileged: No restrictions at all, which is the same as having no PSS applied at all.
* Baseline: Minimally restrive and prevents known high security risk
  configurations such as **privileged pods**
* Restricted: Most restrictive following secururity hardening best practices 


K8s offers a built-in Pod Security Admission (PSA) controller that to enforce Pod
Security Standards across namespaces. The built-in Pod Security Admission controller
is included by default since K8s 1.23.

## Preventing privileged pods with PSS
The baseline and restricted Pod Security Standard would both prevent privileged
pods. However, the restricted PSS would likely be too restrictive for your pod and
would require you to update your Pod Spec and potentially your application. So if
all you need is preventing privileged pods then Baseline would likely be an easier
option.

## Enforcing the baseline Pod Security Standard
Enforcing a pod security standard to a namespace has the risk of preventing
new pods from being deployed to the namespace. So lets do a dry-run first
instead of directly enforcing baseline.

Run a dry-run and check if any warnings are thrown:
```sh
kubectl label --dry-run=server --overwrite ns default \
    pod-security.kubernetes.io/enforce=baseline
```
If you saw `namespace/default labeled` without any warnings then that means
all the currently running pods inside the namespace `default` would have been
admitted if `baseline` was enforced.


Assuming you had no warnings. Let's start by enforcing the baseline standard
on the `default` namespace:
```sh
kubectl label --overwrite ns default \
    pod-security.kubernetes.io/enforce=baseline
```
Notice that this time the `--dry-run=server` parameter is not added.

Let's verify that privileged pods indeed are getting blocked.

Create a file named `nginx-priv.yaml` with the following content:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-priv
spec:
  containers:
  - name: nginx-priv
    image: nginx:1.14.2
    ports:
    - containerPort: 80
    securityContext:
      privileged: true
```

Try to create the privileged pod:
```sh
kubectl apply -f nginx-priv.yaml
```

You should see the following output:
```
Error from server (Forbidden): error when creating "nginx-priv.yaml": pods "nginx-priv" is forbidden: violates PodSecurity "baseline:latest": privileged (container "nginx-priv" must not set securityContext.privileged=true)
```
