Title: Setup IPv6 in Tsinghua on Linux(ArchLinux))
Date: 2015-10-08 12:42
Author: Sam Stoelinga
Category: Linux
Tags: archlinux, ipv6, linux, isatap, isatapd
Slug: ipv6-tsinghua-linux-isatapd

Tsinghua university uses [ISATAP](https://en.wikipedia.org/wiki/ISATAP) to provide IPv6 connectivity to students.
In Linux you can use the [isatapd](http://www.saschahlusiak.de/linux/isatap.htm) program to create an ISATAP tunnel based on an IPv4 device.

You can use the isatapd command as follows to establish an ISATAPD tunnel:

    :::bash
    isatapd --router isatap.tsinghua.edu.cn

After connecting check that you have received an global IPv6 address with:

    :::bash
    ip -6 a

As a last check you need to check your default ipv6 routes. In some cases 2 default routes may get added:

    :::bash
    ip -6 route

If there are 2 default routes make sure to delete the route which goes out via your physical device e.g(eth0 or enp2u5). In my case I had to delete
one of the default routes as follows:

    :::bash
    ip -6 route del default via fe80::5efe:a66f:1501

## Archlinux
Archlinux provides an isatapd package, which you can install via `pacman -S isatapd`.
The package comes with a systemd service at `/usr/lib/systemd/system/isatapd@.service`. You
can start the service with: `systemctl start isatapd@isatap.tsinghua.edu.cn`

