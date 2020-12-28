Title: Securing Redis with Istio TLS origination
Date: 2020-12-28 10:42
Author: Sam Stoelinga
Category: Istio
Tags: Anthos, GKE, Istio, networking
Slug: securing-redis-istio-tls-origniation-termination

Istio is daunting and not all use cases are well documented. The public docs
focus mostly on using the egress gateway for TLS orignation. The use case
of using the sidecar for TLS origination with a database isn't documented
well. This blog post hopes to solve that.

So you've actually done security well and are using an external Redis provider
that only allows TLS to talk to it. You could simply configure each of your
applications to use TLS from the application pod or you can use Istio to
handle the TLS part. This blog is focused on how to use Istio to do TLS
origination for Redis (TCP) using the sidecar instead of the egress gateway.

TLS origination occurs when an Istio proxy (sidecar or egress gateway)
is configured to accept unencrypted internal HTTP connections, encrypt
the requests, and then forward them to HTTPS servers that are secured using
simple or mutual TLS. This is the opposite of TLS termination where an
ingress proxy accepts incoming TLS connections, decrypts the TLS, and
passes unencrypted requests on to internal mesh services.

The blog post contains the following sections:
1. Creating the Redis instance with Aiven
2. Creating the Istio resources
3. Validating that TLS origination worked

### 1. Creating the Redis instance with Aiven or Redislabs
Aiven is a managed database provider and provides a managed Redis service.
The Redis service allows you to require TLS which is what will be used in
this blog post. You can use any TLS Redis service instead of Aiven.

Go to [aiven.io/redis](https://aiven.io/redis) and follow
the steps to create a Redis service using the 30 day free trial. Aiven was
really convenient for me. Redislabs the creators of Redis provide similar
service with a [free 30MB Redis instance](https://redislabs.com/try-free/).
You might want to support the creators of Redis by using Redislabs.

In this blog post the variables will be used:
```bash
export REDIS_HOST=redis-1425a1d9-google-bc39.aivencloud.com
export REDIS_PORT=16222
```
You will need to set these variables to your environment specifics.

### 2. Creating the Istio resources
In this section, you will create the following Istio resources:
- DestinationRule: To configure how outgoing connections to Redis should
  be handled. For example, this is how we configure the TLS settings.
- ServiceEntry: Such that Istio knows about the external Redis service

Create the Redis namespace which is used for testing:
```bash
kubectl create ns redis
# If you use kubectx
kubens redis 
```

Create the following ServiceEntry:
```bash
cat <<EOF | kubectl apply --namespace=redis -f -
apiVersion: networking.istio.io/v1beta1
kind: ServiceEntry
metadata:
  name: external-aiven-redis
spec:
  hosts:
  - $REDIS_HOST
  location: MESH_EXTERNAL
  resolution: DNS
  ports:
  - number: $REDIS_PORT
    name: tcp-redis
    protocol: TCP
EOF
```

Create the DestinationRule:
```bash
cat <<EOF | kubectl apply -f -
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: external-aiven-redis
  namespace: redis
spec:
  host: $REDIS_HOST
  trafficPolicy:
    tls:
      mode: SIMPLE
      caCertificates: /etc/ssl/certs/ca-certificates.crt
EOF
```
Note that Istio has a security issue that if you do not specify the
caCertificates that it will not validate the cert at all. So in the
destination rule we simply point it to the system certs. For more
info on this issue see [#25652](https://github.com/istio/istio/issues/25652).

The destination rule tells Istio that TLS should be used and mode simple
means that this is using standard TLS instead of mutual TLS.

That was all that's needed from the Istio side.

### 3. Validating that TLS origination worked
Create a pod that has redis-client installed:
```bash
cat << EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis-client
  namespace: redis
  labels:
    app: redis-client
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis-client
  template:
    metadata:
      labels:
        app: redis-client
      annotations:
        sidecar.istio.io/logLevel: debug
        sidecar.istio.io/inject: "true"
    spec:
      containers:
        - image: redis
          name: redis-client
          command: [ "/bin/bash", "-c", "--" ]
          args: [ "while true; do sleep 30; done;" ]
EOF
```
Wait for the pods to come up....

Get a shell to the redis-client container:
```bash
kubectl exec -ti deploy/redis-client -c redis-client -- bash
redis-cli -h REPLACE_WITH_REDIS_HOST -p REPLACE_WITH_REDIS_PORT -a REPLACE_WITH_YOUR_PASSWORD
set "hello" "world"
get "hello"
```
The above should return "world". The redis client is using standard TCP while the
Istio sidecar upgraded the connection to TLS in the background.
If you need even more validation, go and create another deployment but this time
set the annotation to `sidecar.istio.io/inject: "false"`. That will prevent Istio
from injecting a sidecar. After you do that you will notice that you can not
connect to Redis anymore if your Redis is enforcing TLS.


You can also Check the logs of the istio-proxy to see that Istio is indeed making
the TLS connections.

```bash
kubectl logs deploy/redis-client -c istio-proxy
```
In my case the following logs could be seen in the Istio proxy logs:
```text
2020-12-28T21:57:43.055354Z     debug   envoy connection        [C486] write flush complete
2020-12-28T21:57:43.058429Z     debug   envoy connection        [C486] remote early close
2020-12-28T21:57:43.058465Z     debug   envoy connection        [C486] closing socket: 0
2020-12-28T21:57:43.058534Z     debug   envoy conn_handler      [C486] adding to cleanup list
2020-12-28T21:57:43.187286Z     debug   envoy upstream  DNS refresh rate reset for zipkin.istio-system, (failure) refresh rate 5000 ms
2020-12-28T21:57:43.531497Z     debug   envoy upstream  transport socket match, socket default selected for host with address 35.238.219.217:
16222
2020-12-28T21:57:43.531562Z     debug   envoy upstream  DNS refresh rate reset for redis-1425a1d9-google-bc39.aivencloud.com, refresh rate 14
000 ms
2020-12-28T21:57:45.050182Z     debug   envoy conn_handler      [C487] new connection
2020-12-28T21:57:45.050333Z     debug   envoy http      [C487] new stream
2020-12-28T21:57:45.050424Z     debug   envoy http      [C487][S11853156146631931010] request headers complete (end_stream=true):
```

### Summary
You were able to use Istio to do TLS originiation using the sidecar instead
of using the egress gateway by just using a DestinationRule and a ServiceEntry.
You also validated that TLS origination is working as expected.
