Title: Docker Multiple websites/domains on single ip/host tutorial using a HAproxy as reverse proxy
Date: 2014-07-08 14:25
Author: Sam Stoelinga
Category: Linux
Tags: linux, docker, container
Slug: docker-get-private-ip-address-of-container

In order to access other containers from a container it's needed
to get the private IP address of the other containers. The following
command is able to get the private ip address of the container.

    :::console
    $ docker inspect --format="{{.NetworkSettings.IPAddress}}" $CONTAINER_ID_OR_NAME
    172.17.0.15
