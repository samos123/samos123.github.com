Title: Fuel: Separate Ceph Public from Management using Network Templates
Date: 2016-08-27 14:01
Author: Sam Stoelinga
Category: Openstack
Tags: openstack, networking, fuel, ceph, mirantis
Slug: fuel-separate-ceph-public-from-management

This post will demonstrate using Network Templates in Fuel to
separate Ceph Public Network from Management Network. By default
Fuel combines the ceph public network with the management network.
The Ceph Public network is used for communicating from the compute nodes
to the Ceph nodes. So in high performant storage networks we would like to be
able to isolate this network from any other network such that we can
guarantee performance.

Fuel Network Templates allow us separate or combine networks. The general workflow
for separating the Ceph Public network is as follows:

1. Create a new Network Group for the new network
2. Write and upload a network template that defines how the newly created network should be used
3. Review and tune the actual deployment settings via the CLI

## Demo environment
This blog post is using the following example environment:

* 5 x VirtualBox VMs
* 1 x Fuel Master 9.0
* 1 x Controller node
* 1 x Compute node
* 2 x Ceph-OSD
* Each VM has 3 NICs: enp0s3, enp0s8, enp0s9
* enp0s3 is used for Admin/PXE network
* enp0s8 is used for Public/Floating network
* enp0s9 is used for Management, Storage, Private and Ceph Public network

## Create the new Ceph Public network group
First the newly defined Ceph Public network needs to be created. This is done
by creating a new network group via Fuel. In the demo, the nic enp0s9 is
used for ceph public and other networks via VLAN tagging. 
Although in a production environment you could
easily put the new Ceph Public network on a dedicated NIC.

The following steps show to create the Ceph Public network with VLAN tag 13:

    :::bash
    # First list the network groups to see what node-group is being used
    # group-id is usually the same as environment id
    fuel network-group
    # Create the new ceph-public network
    fuel network-group --create --node-group 6 --name ceph-public --vlan 13 --cidr 192.168.251.0/24


## Write and upload network template
After having created the new network we use Network Templates functionality
to assign the ceph/public network role to our newly created network. Note
that the order does not matter. You could also first create and upload
template and then create new Ceph Public network group.

The below template is based on the default template with a minor
modification to split out the ceph/public network role from the
management network.

    :::yaml
    adv_net_template:
      default: 
        nic_mapping:
          default:
            adm: enp0s3
            pub: enp0s8
            man: enp0s9.10
            priv: enp0s9.11
            stor: enp0s9.12
            cephpub: enp0s9.13
        templates_for_node_role:
            controller:
              - public
              - private
              - storage
              - ceph-public
              - common
            compute:
              - common
              - ceph-public
              - private
            cinder:
              - common
              - storage
            ceph-osd:
              - common
              - ceph-public
              - storage
        network_assignments: 
            storage:
              ep: br-storage
            ceph-public:
              ep: br-ceph-public
            private:
              ep: br-prv
            public:
              ep: br-ex
            management:
              ep: br-mgmt
            fuelweb_admin:
              ep: br-fw-admin
        network_scheme:
          storage:
            transformations:
              - action: add-br
                name: br-storage
              - action: add-port
                bridge: br-storage
                name: <% stor %>
            endpoints:
              - br-storage
            roles:
              cinder/iscsi: br-storage
              swift/replication: br-storage
              ceph/replication: br-storage
              storage: br-storage
          ceph-public:
            transformations:
              - action: add-br
                name: br-ceph-public
              - action: add-port
                bridge: br-ceph-public
                name: <% cephpub %>
            endpoints:
              - br-ceph-public
            roles:
              ceph/public: br-ceph-public
          private:
            transformations:
              - action: add-br
                name: br-prv
                provider: ovs
              - action: add-br
                name: br-aux
              - action: add-patch
                bridges:
                - br-prv
                - br-aux
                provider: ovs
                mtu: 65000
              - action: add-port
                bridge: br-aux
                name: <% priv %>
            endpoints:
              - br-prv
            roles:
              neutron/private: br-prv
          public:
            transformations:
              - action: add-br
                name: br-ex
              - action: add-br
                name: br-floating
                provider: ovs
              - action: add-patch
                bridges:
                - br-floating
                - br-ex
                provider: ovs
                mtu: 65000
              - action: add-port
                bridge: br-ex
                name: <% pub %>
            endpoints:
              - br-ex
            roles:
              public/vip: br-ex
              neutron/floating: br-floating
              ceph/radosgw: br-ex
              ex: br-ex
          common:
    # In this example the common network is created for Management and Admin traffic.
            transformations:
              - action: add-br
                name: br-fw-admin
              - action: add-port
                bridge: br-fw-admin
                name: <% adm %>
              - action: add-br
                name: br-mgmt
              - action: add-port
                bridge: br-mgmt
                name: <% man %>
            endpoints:
              - br-fw-admin
              - br-mgmt
            roles:
              admin/pxe: br-fw-admin
              fw-admin: br-fw-admin
              mongo/db: br-mgmt
              management: br-mgmt
              keystone/api: br-mgmt
              neutron/api: br-mgmt
              neutron/mesh: br-mgmt
              swift/api: br-mgmt
              sahara/api: br-mgmt
              ceilometer/api: br-mgmt
              cinder/api: br-mgmt
              glance/api: br-mgmt
              heat/api: br-mgmt
              nova/api: br-mgmt
              nova/migration: br-mgmt
              murano/api: br-mgmt
              horizon: br-mgmt
              mgmt/api: br-mgmt
              mgmt/memcache: br-mgmt
              mgmt/database: br-mgmt
              mgmt/messaging: br-mgmt
              mgmt/corosync: br-mgmt
              mgmt/vip: br-mgmt
              mgmt/api: br-mgmt

Save the above file with the name `network_template_6.yaml` on your Fuel node. Fuel network template requires that the file name is in the following
format: `network_template_{{ env_id }}.yaml`. If your fuel doesn't match the format you won't be able to upload.

Now upload the the file `network_template_6.yaml` to Fuel via:

    :::bash
    fuel network-template --env 6 --upload --dir .

## Review and tune final deployment settings
This last step is to make sure that the Network settings set by Network Templates
and Network group match expectations. Download the final deployment settings
for the environment using the below command:

    :::bash
    fuel deployment --default --env 6

This will create a directory called `deployment_6` containing deployment settings
for the actual deployment. Open for example `deployment_6/master.yaml` or `deployment_6/10.yaml`
and verify that ceph/public network role is assigned to controllers and ceph-osd nodes. Next to
that make sure that ceph/public is assigned a specific IP address on each node.

Now we're ready to deploy and can trigger the deployment with:

    :::bash
    fuel deploy-changes --env 6

If you're lucky enough to not have made mistakes and hit bugs, then you will be running in no time :)
This isn't easy to use functionality, without the help of my colleague xarxes I wasn't able to get it
working.
