Title: SSH to server behind a firewall via an SSH tunnel
Date: 2014-05-10
Author: Sam Stoelinga
Category: Linux
Tags: linux, ssh, firewall, tunnel
Slug: ssh-to-server-behind-firewall-via-ssh-tunnel

A server behind a firewall was unaccesible from my home,
but another server which is on the same local network had
public SSH access from my home. So we can create an SSH tunnel
via this public server to the server behind a firewall.

For example the public ssh server is 8.8.8.8 and the
server on the private network that we want to access is 192.168.1.5. Then we
can create an SSH tunnel from my laptop at home in the
following way:

    :::bash
    ssh root@8.8.8.8 -L 2020:192.168.1.5:22

The above command creates an SSH tunnel, where the
local port 2020 on my laptop will be forwarded to port
22 of the private server behind the firewall.

After the tunnel is created  you can use the following command
to directly SSH from your home laptop to the private server
with ip 192.168.1.5:

    :::bash
    ssh ubuntu@localhost -p 2020
