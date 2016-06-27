Title: Creating a KVM VM for StackLight on Fuel 8.0 master node
Date: 2016-06-01 09:31
Author: Sam Stoelinga
Category: Openstack
Tags: fuel, centos, openstack
Slug: creating-vm-on-fuel-8.0-master

Creating a KVM VM on the Fuel master node is a nice way
to better utilize server resources for small environments.
We can run Controller, Monitoring or MongoDB as VM on the Fuel
node. This blog post explains in detail how to create a KVM VM
on the Fuel master node, which can be used for any role defined by
Fuel. In this example we assign the StackLight monitoring role
to the VM created on the Fuel master node.

The general steps are:

1. Install KVM on Fuel master node (Enable CentOS repo, install kvm and libvirt packages)
2. Create network bridges on the Fuel master node for Admin/PXE and Management network
3. Create the KVM VM through libvirt using an XML template
4. PXE boot the KVM VM such that it gets discovered by Fuel
5. Assign your desired role to the VMs via Fuel and deploy

# 1. Install KVM and libvirt on the Fuel master
The first step is install KVM and libvirt on the Fuel master node. SSH into Fuel Master node and
execute the ollowing steps:

1. Create the file `/etc/yum.repos.d/CentOS-base.repo` with the following content:

        :::text
        # CentOS-Base.repo
        [base]
        name=CentOS-$releasever - Base
        mirrorlist=http://mirrorlist.centos.org/?release=$releasever&arch=$basearch&repo=os&infra=$infra
        #baseurl=http://mirror.centos.org/centos/$releasever/os/$basearch/
        gpgcheck=1
        gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7
    
        #released updates
        [updates]
        name=CentOS-$releasever - Updates
        mirrorlist=http://mirrorlist.centos.org/?release=$releasever&arch=$basearch&repo=updates&infra=$infra
        #baseurl=http://mirror.centos.org/centos/$releasever/updates/$basearch/
        gpgcheck=1
        gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7
    
        #additional packages that may be useful
        [extras]
        name=CentOS-$releasever - Extras
        mirrorlist=http://mirrorlist.centos.org/?release=$releasever&arch=$basearch&repo=extras&infra=$infra
        #baseurl=http://mirror.centos.org/centos/$releasever/extras/$basearch/
        gpgcheck=1
        gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7
    
        #additional packages that extend functionality of existing packages
        [centosplus]
        name=CentOS-$releasever - Plus
        mirrorlist=http://mirrorlist.centos.org/?release=$releasever&arch=$basearch&repo=centosplus&infra=$infra
        #baseurl=http://mirror.centos.org/centos/$releasever/centosplus/$basearch/
        gpgcheck=1
        enabled=0
        gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7

2. Now install the required packages from CentOS repo

        :::bash
        yum install libvirt qemu-kvm kvm


## 2. Create networking bridges for KVM VM
Here we create network bridges on the Fuel master node for Admin/PXE and Management network.

1. Prevent libvirt from starting dnsmasq. Execute the following command, delete the parts with dhcp
   and change forwarding to none:

        :::bash
        virsh net-edit default

2.  Create the bridge for Admin/PXE network. This step is not using
    the standard way to create the bridge, because I didn't want to change
    the network device name to which the IP is bound. It seems that some
    containers by default use eth0 and host networking. I don't recommend
    doing it this way, but it "works".

    I created a script which doesn't change eth0, but instead renames
    eth0 to net0 and then creates a bridge named eth0 and assigns the original
    net0 ip address to eth0. I tried to use udev but couldn't get it to work,
    so here we go with a hacky script.

    Create a file `/usr/bin/create-eth0-bridge.sh` with the following content:

        :::bash
        #!/bin/bash
    
        ETH0ADDR=10.20.0.2/24
    
        # Rename eth0 to net0
        ip a flush dev eth0
        ip link set eth0 down
        ip link set eth0 name net0
        ip link set net0 up 
    
        # Create bridge eth0 with net0 as interface
        brctl addbr eth0
        ip link set eth0 up
        brctl addif eth0 net0
    
        # Add original eth0addr to bridge
        ip a add $ETH0ADDR dev eth0

3. Create a systemd service to launch the script after network was done.
   Create the file `/etc/systemd/system/create-eth0-bridge.service` with
   the following content:

        :::bash
        [Unit]
        Description=Create eth0 network bridge for Stacklight VM
        Wants=network-online.target
        After=network-online.target
    
        [Service]
        ExecStart=/usr/bin/create-eth0-bridge.sh
    
        [Install]
        WantedBy=multi-user.target
    
    Now enable the service to be run on startup by executing the command:

        :::bash
        systemctl enable create-eth0-bridge

4. Create the bridge which contains other possible networks. Please
   note that if you used VLAN tagging then you should add the VLAN
   trunk port to your bridge. In this example I have a vlan trunk
   which contains the management network on eth2.

    Create the bridge named br-eth2 and add eth2 as port to the bridge
    with the following commands:

        :::bash
        brctl addbr br-eth2
        brctl addif br-eth2 eth2

    To make the changes persistent accross reboots create
    the file `/etc/sysconfig/network-scripts/ifcfg-br-eth2` with the following content:

        :::text
        DEVICE=br-eth2
        BOOTPROTO=none
        ONBOOT=yes
        TYPE=Bridge
        NM_CONTROLLED=no
        DELAY=0

    and the file `/etc/sysconfig/network-scripts/ifcfg-eth2` with the following content:

        :::text
        TYPE=Ethernet
        BOOTPROTO=none
        NAME=eth2
        UUID=fe45432f-f08a-4537-9851-d53be572aa00
        DEVICE=eth2
        ONBOOT=yes
        NM_CONTROLLED=no
        BRIDGE=br-eth2


## 3. Create the KVM VM
In this part we create the KVM VM using libvirt XML to describe
the VM. In the XML we specify to boot from network first, which
enables us to use Fuel's PXE booting.

1. First create the disk for our KVM VM with the following command:

        :::bash
        qemu-img create -f qcow2 -o preallocation=metadata /var/lib/libvirt/images/monitoring-1.img 300G

2. Create a file `monitoring1-vm.xml` with the following content:

        :::xml
        <domain type='kvm' id='2'>
          <name>monitoring-1</name>
          <memory unit='KiB'>8388608</memory>
          <vcpu placement='static' cpuset='0-7'>8</vcpu>
          <os>
            <type arch='x86_64'>hvm</type>
            <boot dev='network'/>
            <boot dev='hd'/>
            <boot dev='cdrom'/>
            <bootmenu enable='yes'/>
          </os>
          <features>
            <acpi/>
            <apic/>
            <pae/>
          </features>
          <clock offset='utc'/>
          <devices>
            <disk type='file' device='disk'>
              <driver name='qemu' type='qcow2'/>
              <source file='/var/lib/libvirt/images/monitoring-1.img'/>
              <target dev='sda' bus='scsi'/>
            </disk>
            <interface type='bridge'>
              <source bridge='eth0'/>
              <model type='virtio'/>
            </interface>
            <interface type='bridge'>
              <source bridge='br-eth2'/>
              <model type='virtio'/>
            </interface>
            <graphics type='vnc' port='-1' listen='127.0.0.1'/>
          </devices>
        </domain>

    Note you may need to tweak the parameters such as vcpus, memory
    and bridges according to your actual environment.

3. Launch and create the VM from the xml file:

        :::bash
        virsh define monitoring-1.xml
        virsh start monitoring-1

## 4. Fuel PXE booting and assigning roles
After you have done the previous steps correctly, you should see
a new unallocated node pop up. You can now assign any role to this
new node.
