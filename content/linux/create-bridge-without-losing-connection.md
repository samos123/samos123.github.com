Title: Create Linux bridge without losing existing connection
Date: 2015-06-19 14:25
Author: Sam Stoelinga
Category: Linux
Tags: linux, networking, bridge
Slug: create-linux-bridge-without-losing-connection

The dillemma: You're accessing your server via SSH through interface eth1.102 with the ip 10.20.0.2/24 and gateway 10.20.0.1.
Now you want to add eth1 to a linux bridge so you can hookin VMs on a vlan trunk.

Solution: Create a script which does everything in 1 go and call this script from screen. Make sure the script is flawless else you still loose your connection.

This is the script I create-bridge.sh used:

    :::bash
    # First remove the old vlan device
    ip link set dev eth1.102 down
    ip link delete eth1.102


    # Create the bridge 
    brctl addbr br-eth1
    brctl addif br-eth1 eth1 

    ip link set eth1 up
    ip link set br-eth1 up

    # Add the vlan tagging ontop of the bridge
    vconfig add br-eth1 102

    ip link set br-eth1.102 up
    ip a add 166.111./24 dev br-eth1.102
    ip route add default via 166.111.80.10


Now you should first open a screen session(maybe optional) and then call `./create-bridge.sh`, which create your bridge and setup the previous interface ontop of the bridge without losing your SSH connection :)
