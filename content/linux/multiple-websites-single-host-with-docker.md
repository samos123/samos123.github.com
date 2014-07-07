Title: Docker Multiple websites/domains on single ip/host tutorial using a HAproxy as reverse proxy
Date: 2014-07-07 10:15
Author: Sam Stoelinga
Category: Linux
Tags: linux, docker, container
Slug: docker-multi-website-single-ip-host-haproxy

This post will describe how to expose multiple docker containers
running websites on port 80 using HAproxy as a reverse proxy.
This makes it possible to run multiple websites on different domains
on a single public ip of the host.

The basic setup is to create 1 container for haproxy which is exposed to
the host on port 80. This HAproxy container will forward the incoming
HTTP request to the correct container based on the domain name.

![Reverse haproxy docker diagram](/images/haproxy_reverse_proxy_docker.png)<br/>
Picture drawn with <a href="http://draw.io" target="_blank">draw.io</a>.

First launch the containers which run different websites. In our example
we will use a
<a href="https://registry.hub.docker.com/u/tutum/hello-world/"
   target="_blank">hello-world php demo container</a>
and a 
<a href="https://registry.hub.docker.com/u/tutum/wordpress/"
   target="_blank">wordpress site container</a>.

    :::console
    $ # Run hello world php demo container (test1.domain.com)
    $ docker run -d tutum/hello-world
    01ec10276761
    $ docker inspect -f "{{.NetworkSettings.IPAddress}}" 01ec10276761
    172.17.0.26

    $ # Run wordpress container (test2.domain.com)
    $ docker run -d tutum/wordpress
    4d23f10f6b35
    $ docker inspect -f "{{.NetworkSettings.IPAddress}}" 4d23f10f6b35
    172.17.0.25

Now we need to create our haproxy configuration to configure HAproxy as
reverse proxy for our docker containers. Because HAProxy is also running
inside a container we need to be able to access the hello-world and
wordpress container by their private ip accessible from all containers.
We got this IP using the command: `docker inspect -f "{{.NetworkSettings.IPAddress}}" $CONTAINERID`.
Make sure to note down these IPs as they will be used in the haproxy.cfg file.


    :::console
    $ # On the host(not container) create directory containing our haproxy config file
    $ mkdir ~/haproxy-config

    $ # Create ~/haproxy-config/haproxy.cfg
    $ vim ~/haproxy-config/haproxy.cfg
    global
            log 127.0.0.1   local0
            log 127.0.0.1   local1 notice
            user haproxy
            group haproxy
            # daemon

    defaults
            log     global
            mode    http
            option  httplog
            option  dontlognull
            option forwardfor
            option http-server-close
            contimeout 5000
            clitimeout 50000
            srvtimeout 50000
            errorfile 400 /etc/haproxy/errors/400.http
            errorfile 403 /etc/haproxy/errors/403.http
            errorfile 408 /etc/haproxy/errors/408.http
            errorfile 500 /etc/haproxy/errors/500.http
            errorfile 502 /etc/haproxy/errors/502.http
            errorfile 503 /etc/haproxy/errors/503.http
            errorfile 504 /etc/haproxy/errors/504.http
            stats enable
            stats auth username:password
            stats uri /haproxyStats

    frontend http-in
            bind *:80

            # Define hosts based on domain names
            acl host_test1 hdr(host) -i test1.domain.com
            acl host_test2 hdr(host) -i test2.domain.com

            ## figure out backend to use based on domainname
            use_backend test1 if host_test1
            use_backend test2 if host_test2


    backend test1 # test1.domain.com container
        balance roundrobin
        option httpclose
        option forwardfor
        server s2 172.17.0.26:80 # This ip should be the ip of hello-world container

    backend test2 # test2.domain.com container
        balance roundrobin
        option httpclose
        option forwardfor
        server s1 172.17.0.26:80 # This ip should be ip of wordpress container

    $ # Run haproxy and map the host directory ~/haproxy-config to /haproxy-override of the container
    $ # See the image README and Dockerfile for info about this override behaviour.
    $ # HAProxy is exposed on port 80 because all requests to the public ip should
    $ # go to the HAProxy container.
    $ docker run -d -p 80:80 -v ~/haproxy-config:/haproxy-override dockerfile/haproxy

The HAProxy configuration could be automated possibly with the use of etcd to store
information about services or use a similar method to
<a href="http://jasonwilder.com/blog/2014/03/25/automated-nginx-reverse-proxy-for-docker/"
   target="_blank">Automated nginx reverse proxy for docker</a>. The automated nginx reverse
proxy didn't work for me though.

Thanks to
<a href="http://oskarhane.com/haproxy-as-a-static-reverse-proxy-for-docker-containers/"
   target="_blank">HAProxy as static reverse proxy for docker containers</a> for the
haproxy config file. Although I think it's better to run HAproxy in a container.
