Title: Enable SRIOV on OpenStack Juno
Date: 2015-07-15 16:31
Author: Sam Stoelinga
Category: Openstack
Tags: openstack, networking, sriov, sr-iov, fuel, mirantis openstack
Slug: sriov-openstack-juno-fuel-6-1

Update: Please take a look at the official
<a href="http://docs.openstack.org/networking-guide/adv_config_sriov.html" target="_blank">
Networking Guide: Using SRIOV functionality</a>. This is the
<a target="_blank" href="https://review.openstack.org/#/c/213985/">changeset</a> by me that
adds the SRIOV documentation.

<table class="table table-bordered table-hover">
<caption>Terms used</caption>
<thead>
<tr>
<th class="col-md-2">Term</th>
<th>Definition</th>
</tr>
<tbody>
<tr>
<th scope="row">SRIOV</th>
<td>Single Root IO Virtualization. SRIOV allows a PCIe device to appear to be multiple separate physical PCIe devices.
<a target="_blank" href="http://blog.scottlowe.org/2009/12/02/what-is-sr-iov/">What's SRIOV? By Scott Lowe</a></td>
</tr>
<tr><th scope="row">PF & VF</th><td>PF is a physical function. VF is a virtual function. 
A PF is the physical PCI-e network card. A VF is a virtual network card with it's own PCI address.</td>
</tr>
</tbody>
</table>


This post describes how to enable Neutron SRIOV functionality on Mirantis OpenStack Juno
deployed with Fuel 6.1 using Ubuntu 14.04 as host OS. This tutorial assumes you already have deployed OpenStack with
OVS + vlan mode for networking. Next to that for the private interface we have selected
eth3, which serves both as PF for the VFs and also as private vlan trunk for non SRIOV
instances. In our environment we're using the "Intel Corporation 82599" network card which is assigned to eth3.
We will create 7 VFs per PF.

I have created an ansible playbook to automate the whole process.
You can view this Ansible playbook here: [Fuel Ansible SRIOV](https://github.com/samos123/fuel-ansible-sriov)
Automated methods are recommended over manual configuring!

The following steps have to be taken to enable SRIOV manually for reference:
<ol>
<li>Enabling Virtual Functions in the host Operating System</li>
<li>Whitelist which PCI devices should be used for SRIOV in nova.conf on computes</li>
<li>Configuring Neutron server for SRIOV</li>
<li>Enabling the PCIDeviceScheduler in nova-scheduler</li>
<li>Creating your SRIOV instance</li>
</ol>

### 1. Enable Virtual Functions in Host OS
First we need to make sure SRIOV is enabled in BIOS, check for VT-d and make sure it's enabled.
After enabling VT-d we also need enable IOMMU on Linux by adding intel\_iommu=on to kernel parameters.

    :::bash
    vim /etc/default/grub
    change "GRUB_CMDLINE_LINUX_DEFAULT="nomdmonddf nomdmonisw"
    to "GRUB_CMDLINE_LINUX_DEFAULT="nomdmonddf nomdmonisw intel_iommu=on"

If you added new parameters you need to run:
    
    :::bash
    update-grub
    reboot

On each compute node we need to create the VFs via the PCI SYS interface.

    :::bash
    echo '7' > /sys/class/net/eth3/device/sriov_numvfs

Now verify that the VFs have been created correctly

    :::bash
    lspci | grep Ethernet
    

We just created the VFs for this session. If we would reboot the node these changes would get lost.
So we also add a line to /etc/rc.local to apply these settings on a reboot.
Note: The suggested way of making these settings persistent seems to be through sysfs.conf, but
for some reason it did not work for me hence the rc.local workaround.

    :::bash
    echo "echo '7' > /sys/class/net/eth3/device/sriov_numvfs" >> /etc/rc.local

Verify by rebooting your node that the settings persist.

### 2. Whitelist PCI devices nova.conf on computes

In /etc/nova/nova.conf add the line `pci_passthrough_whitelist={ "devname": "eth3", "physical_network": "physnet2"}`, this tells nova
that all VFs belonging to eth3 are allowed to be passed through to VMs. Restart nova compute to let the changes have effect
`service restart nova-compute`


### 3. Configuring Neutron server
Add sriovnicswitch to neutron ml2 conf

    :::bash
    sed -i "s/mechanism_drivers =openvswitch/mechanism_drivers =openvswitch,sriovnicswitch/g" /etc/neutron/plugins/ml2/ml2_conf.ini

Find out the vendor\_id and product\_id of your VFs. Please note this should be the VF not the PF

    :::bash
    lspci -nn | grep -i ethernet
    87:00.0 Ethernet controller [0200]: Intel Corporation 82599 10 Gigabit Dual Port Backplane Connection [8086:10f8] (rev 01)
    87:10.1 Ethernet controller [0200]: Intel Corporation 82599 Ethernet Controller Virtual Function [8086:10ed] (rev 01)
    87:10.3 Ethernet controller [0200]: Intel Corporation 82599 Ethernet Controller Virtual Function [8086:10ed] (rev 01)

In our case the vendor\_id is 8086 and the product\_id is 10ed. We need to tell Neutron the vendor\_id and product\_id of
the VFs that are supported.

    :::bash
    sed -i "s/# supported_pci_vendor_devs.*=.*/supported_pci_vendor_devs = 8086:10ed/g" /etc/neutron/plugins/ml2/ml2_conf_sriov.ini

Neutron also has support for running a special sriov-agent which is able set the admin state. I didn't see
any need for setting admin state, so to reduce complexity, we've disabled sriov-agent. 

    :::bash
    sed -i "s/# agent_required =.*/agent_required=false/g" /etc/neutron/plugins/ml2/ml2_conf_sriov.ini

We now need to add these new config files as parameter to the neutron-server daemon.

    :::bash
    vim /etc/init/neutron-server.conf
    change "--config-file /etc/neutron/neutron.conf"
    to "--config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugin.ini --config-file /etc/neutron/plugins/ml2/ml2_conf_sriov.ini"

Restart neutron-server on every controller

    :::bash
    service neutron-server restart


### 4. Enabling the PCIDeviceScheduler in nova-scheduler
On every controller node running nova-scheduler we need to add PCIDeviceScheduler to the filters.

    :::bash
    vim /etc/nova/nova.conf
    change "scheduler_default_filters=DifferentHostFilter,RetryFilter,AvailabilityZoneFilter,RamFilter,CoreFilter,DiskFilter,ComputeFilter,ComputeCapabilitiesFilter,ImagePropertiesFilter,ServerGroupAntiAffinityFilter,ServerGroupAffinityFilter"

    to "scheduler_default_filters=DifferentHostFilter,RetryFilter,AvailabilityZoneFilter,RamFilter,CoreFilter,DiskFilter,ComputeFilter,ComputeCapabilitiesFilter,ImagePropertiesFilter,ServerGroupAntiAffinityFilter,ServerGroupAffinityFilter,PciPassthroughFilter"

    also add the following line: "scheduler_available_filters=nova.scheduler.filters.pci_passthrough_filter.PciPassthroughFilter"
    below the line: "scheduler_available_filters=nova.scheduler.filters.all_filters"

    # Restart nova-scheduler
    service nova-scheduler restart

### 5. Launching an Instance with SRIOV ports
After configuring all components we can start trying to launch an instance through the CLI or API.
Horizon currently does not support creating SRIOV instances.

Get the id of the neutron network where you want the SR-IOV port to be created.

    :::bash
    net_id=`neutron net-show net04 | grep "\ id\ " | awk '{ print $4 }'`

Create the SR-IOV port. We specify vnic\_type direct, which means that this a SR-IOV port.

    :::bash
    port_id=`neutron port-create $net_id --name sriov_port --binding:vnic_type direct | grep "\ id\ " | awk '{ print $4 }'`

Create the VM specifying that as 1st nic we want to use the previously created sr-iov port.

    :::bash
    nova boot --flavor m1.large --image ubuntu_14.04 --nic port-id=$port_id --key-name sam test-sriov

References which deserve credit:
* [Red Hat Documentation on using SRIOV](https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/6/html/Virtualization_Host_Configuration_and_Guest_Installation_Guide/sect-Virtualization_Host_Configuration_and_Guest_Installation_Guide-SR_IOV-How_SR_IOV_Libvirt_Works.html)
* [OpenStack Wiki: SR-IOV-Passthrough-For-Networking](https://wiki.openstack.org/wiki/SR-IOV-Passthrough-For-Networking)
