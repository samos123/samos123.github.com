Title: OpenStack Salt MK22 Vagrant-based lab
Date: 2016-11-08 13:15
Author: Sam Stoelinga
Category: Openstack
Tags: openstack, salt
Slug: openstack-salt-mk22-vagrant-lab

The blog by [Sebastian](http://www.yet.org/2016/10/os-salt/) inspired me to try out OpenStack Salt in combination
with the new [MK22 Reclass  model](https://github.com/Mirantis/mk-lab-salt-model).
Instead of using the TCPcloud provided labs I'm using
my own laptop beast (ThinkPad W530 with 32GB of memory).
For that reason I created a Vagrantfile for the mk22-lab-basic environment to create VMs on my laptop. The
Vagrantfile creates the nessecary interfaces and internal networks to mimick
the model. At the bottom of this post you can find the Vagrantfile. I've also
created a static branch based on the upstream mk-lab-salt-model that I've verified
to be working with the instructions provided below. The instructions originally come from
Ales Komarek. They have been slightly modified to get them working.

Reclass model used in this blog:
[gh:samos123/mk-lab-salt-model branch:sam-vagrant-blog-post](https://github.com/samos123/mk-lab-salt-model/tree/sam-vagrant-blog-post).
The following commits have been created specifically for this post:
```
fcea636 Remove Horizon contrail integration because of missing pkgs
60af84f Del Mirantis Horizon them because pkg unavailable
cc527df Remove non-used node definitions
f76eab0 Disable monitoring due to resources
e55d0fe Remove ens4 nic dhcp config
5d71986 Change repo to samos123 b/sam-vagrant-blog-post
6222ff5 Add Vagrant file for mk22-lab-basic
```


The Vagrantfile defines and creates the following VMs:

- cfg01: 4GB RAM, used as Salt Master
- ctl01, ctl02, ctl03: 4GB RAM, used for Controllers and Contrail
- cmp01: 2GB
- prx01: 2GB

Each VM that gets created will get assigned the following networks automatically:
- eth0/enp0s3: 10.0.2.0/24, NAT interface for internet
- eth1/enp0s8: 172.16.10.0/24, host-only network for all OpenStack, Contrail and Data Network
- eth2/enp0s9: 192.168.10.0/24, host-only network for Salt to configure hosts


By following below instructions you can bring up an OpenStack cloud (I found it often still
requires debugging and tweaking to make it work):
```bash
# Manually setup the salt-master
vagrant up cfg01
vagrant ssh cfg01
echo "deb [arch=amd64] http://apt.tcpcloud.eu/nightly/ xenial main security extra tcp tcp-salt" > /etc/apt/sources.list
wget -O - http://apt.tcpcloud.eu/public.gpg | apt-key add -
apt-get update
apt-get upgrade
apt-get install -y salt-master reclass
apt-get install -y salt-formula-linux salt-formula-reclass salt-formula-salt \
                   salt-formula-openssh salt-formula-ntp salt-formula-git \
                   salt-formula-graphite salt-formula-collectd salt-formula-sensu salt-formula-heka
apt-get install -y salt-formula-sphinx salt-formula-horizon salt-formula-nginx \
                   salt-formula-memcached salt-formula-python salt-formula-supervisor
cat << 'EOF' >> /etc/salt/master.d/master.conf
file_roots:
  base:
  - /usr/share/salt-formulas/env
pillar_opts: False
open_mode: True
reclass: &reclass
  storage_type: yaml_fs
  inventory_base_uri: /srv/salt/reclass
ext_pillar:
  - reclass: *reclass
master_tops:
  reclass: *reclass
EOF

mkdir /etc/reclass
cat << 'EOF' >> /etc/reclass/reclass-config.yml
storage_type: yaml_fs
pretty_print: True
output: yaml
inventory_base_uri: /srv/salt/reclass
EOF

git clone https://github.com/samos123/mk-lab-salt-model /srv/salt/reclass -b sam-vagrant-blog-post
mkdir -p /srv/salt/reclass/classes/service
for i in /usr/share/salt-formulas/reclass/service/*; do ln -s $i /srv/salt/reclass/classes/service/; done

apt-get install -y salt-minion
cat << "EOF" >> /etc/salt/minion.d/minion.conf
id: cfg01.mk22-lab-basic.local
master: localhost
EOF

service salt-master restart
service salt-minion restart

# confirm cfg01 is accepted
salt-key 
# check reclass model is fine
reclass-salt --top
reclass-salt --pillar cfg01.mk22-lab-basic.local

salt 'cfg01*' state.sls reclass.storage
salt '*' saltutil.refresh_pillar

salt "cfg01*" state.sls git,linux,ntp
salt-call state.sls salt
salt "cfg01*" state.sls openssh,reclass,sphinx,nginx


# shows there are no nodes added to salt yet
salt-key
# exit back to Host running  vagrant
exit

# now bring up remaining nodes ctl[1-3], cmp01, prx01
vagrant up

vagrant ssh cfg01
# We need m2crypto to be installed else some states will fail
salt '*' pkg.install python-m2crypto
salt '*' state.sls ntp,linux,salt.minion,openssh
salt "ctl*" state.show_top
salt "ctl*" --state-output=mixed -b 1 state.sls keepalived
salt 'ctl01*' pillar.get keepalived:cluster:instance:VIP:address
salt 'ctl01*' cmd.run "ip a"
salt "ctl*" --state-output=mixed -b 1 state.sls memcached,rabbitmq

salt 'ctl*' state.sls glusterfs.server.service
salt 'ctl*' -b 1 state.sls glusterfs.server.setup
# gluterfs.server.setup fails because of issue with formula with older salt minons
# pr is submitted https://github.com/tcpcloud/salt-formula-glusterfs/pull/8
# if you still hit this issue, manually start the volume and rerun state again
salt "ctl01*" cmd.run "gluster volume start keystone-keys; gluster volume start glance"
salt 'ctl*' -b 1 state.sls glusterfs.server.setup

# verify that gluster is working
salt "ctl01*" cmd.run "gluster peer status; gluster volume status"

# install mysql
salt -C 'I@galera:master' state.sls galera
salt -C 'I@galera:slave' state.sls galera
salt -C 'I@galera:master' mysql.status




salt -C 'I@haproxy:proxy' state.sls haproxy
salt -C 'I@haproxy:proxy' service.status haproxy


# For some reason salt's keystone module doesn't work unless you restart the minion
salt 'ctl*' state.sls keystone -b 1
salt -C 'I@keystone:client' state.sls keystone.client
salt "ctl01*" cmd.run ". /root/keystonerc; keystone service-list"

salt 'ctl*' -b 1 state.sls glance
salt 'ctl*' state.sls glusterfs.client
salt 'ctl*' cmd.run 'df -h'
# need to rerun keystone for glance to work
salt 'ctl*' state.sls keystone
salt "ctl*" cmd.run ". /root/keystonerc; glance image-list"

salt -C 'I@nova:controller' state.sls nova -b 1
salt -C 'I@keystone:server' cmd.run ". /root/keystonerc; nova service-list"

# Cinder fails to install some packages
# workaround is to manually install linux-image-extra-virtual package
salt 'ctl*' pkg.install linux-image-extra-virtual
salt -C 'I@cinder:controller' state.sls cinder -b 1
salt -C 'I@keystone:server' cmd.run ". /root/keystonerc; cinder list"

# Neutron
salt -C 'I@neutron:server' state.sls neutron -b 1

# heat 2 states will fail but that's fine as it was created previously. 
# Should still be fixed though, this is the error seen:
# State 'keystone.role_present' was not found in SLS 'heat.server'
#              Reason: 'keystone' __virtual__ returned False
# also if heat-api isn't running make sure the following patch is merged
# https://review.openstack.org/#/c/394599/
salt -C 'I@heat:server' state.sls heat -b 1
salt -C 'I@keystone:server' cmd.run ". /root/keystonerc; heat resource-type-list"



# Several issues with horizon and dashboard
# 1. The package openstack-dashboard-contrail-panels is missing so I've disabled
#    Contrail integration by changing the reclass model. See commit #fcea6366ea50
# 2. The package openstack-dashboard-mirantis-theme is missing so I've disabled
#    mirantis them customization in the reclass model. See commit #60af84f237bab
# 3. The salt-formula-horizon fails when app.plugin is not set in pillar. For
#    this I've submitted a patch in the formula https://review.openstack.org/#/c/394618/
# You may have to apply the patch in point 3 manually ^^ horizon fails for me still.
salt -C 'I@horizon:server' state.sls horizon
salt -C 'I@nginx:server' state.sls nginx

# Install contrail
salt "ctl*" state.sls opencontrail -b 1
salt -C 'I@keystone:server' cmd.run ". /root/keystonerc; neutron net-list; nova net-list"

salt 'ctl01*' cmd.run "/usr/share/contrail-utils/provision_control.py --api_server_ip 172.16.10.254 --api_server_port 8082 --host_name ctl01 --host_ip 172.16.10.101 --router_asn 64512 --admin_password workshop --admin_user admin --admin_tenant_name admin --oper add"
salt 'ctl02*' cmd.run "/usr/share/contrail-utils/provision_control.py --api_server_ip 172.16.10.254 --api_server_port 8082 --host_name ctl02 --host_ip 172.16.10.102 --router_asn 64512 --admin_password workshop --admin_user admin --admin_tenant_name admin --oper add"
salt 'ctl03*' cmd.run "/usr/share/contrail-utils/provision_control.py --api_server_ip 172.16.10.254 --api_server_port 8082 --host_name ctl03 --host_ip 172.16.10.103 --router_asn 64512 --admin_password workshop --admin_user admin --admin_tenant_name admin --oper add"


# Configure compute nodes
salt 'cmp*' state.highstate
salt 'cmp*' state.highstate
salt 'ctl01*' cmd.run "/usr/share/contrail-utils/provision_vrouter.py --host_name cmp01 --host_ip 172.16.10.105 --api_server_ip 172.16.10.254 --oper add --admin_user admin --admin_password workshop --admin_tenant_name admin"

# Temporary workaround for mos packages
salt 'cmp*' cmd.run "find /etc -xdev -type f | xargs egrep -H 'unix_sock_group.*libvirt' | sed -e 's/:.*//' | xargs sed -i -e 's/unix_sock_group = \"libvirtd\"/unix_sock_group = \"libvirt\"/'"

# There is an issue with nova.conf because rabbit_host isn't set in default section
# I've submitted a patch here: https://review.openstack.org/#/c/395161/

# Try rebooting and see if it still works
salt 'cmp*' system.reboot
# For some reason I got an older libvirt from tcprepo instead of mos
# below installs the correct package. Bug filed here:
# https://github.com/tcpcloud/salt-formula-libvirt/issues/1
vim /usr/share/salt-formulas/env/nova/files/mitaka/nova-compute.conf.Debian
# change virt_type from kvm to qemu, bug has been filed about this here:
# https://bugs.launchpad.net/openstack-salt/+bug/1640314
salt 'cmp*' cmd.run "apt-get update"
salt 'cmp*' pkg.install libvirt-bin
salt 'cmp*' cmd.run "ip a"
salt 'cmp*' cmd.run "contrail-status"

# Exit and SSH into ctl01 to test the cloud
exit
vagrant ssh ctl01
sudo -i
source keystonerc
wget http://download.cirros-cloud.net/0.3.4/cirros-0.3.4-i386-disk.img
glance image-create --name cirros --visibility public --disk-format qcow2 --container-format bare --progress < /root/cirros-0.3.4-i386-disk.img
neutron net-create net1
neutron subnet-create --name subnet1 net1 192.168.32.0/24
keystone tenant-list
netuuid=$(neutron net-list | grep net1 | awk '{ print $2 }')
nova flavor-create --is-public true m1.macro auto 128 5 1
nova boot --nic net-id=$netuuid --image cirros --flavor m1.macro testvm1
```



Below is the Vagrantfile that is used in this blog post:
```
# -*- mode: ruby -*-
# vi: set ft=ruby :

$script = <<SCRIPT
echo "deb [arch=amd64] http://apt.tcpcloud.eu/nightly/ trusty main security extra tcp tcp-salt" > /etc/apt/sources.list
wget -O - http://apt.tcpcloud.eu/public.gpg | apt-key add -
apt-get update
apt-get install -y salt-minion
cat << "EOF" >> /etc/salt/minion.d/minion.conf
id: {{x}}.mk22-lab-basic.local
master: 192.168.10.100
EOF
SCRIPT

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/trusty64"

  config.vm.provider "virtualbox" do |vb|
     # Display the VirtualBox GUI when booting the machine
     vb.gui = true
  
     # Customize the amount of memory on the VM:
     vb.memory = "4096"
  end

  config.vm.define "cfg01" do |cfg01|
    cfg01.vm.box = "ubuntu/xenial64"
    cfg01.vm.network "private_network", ip: "172.16.10.100"
    cfg01.vm.network "private_network", ip: "192.168.10.100"
  end

  config.vm.define "ctl01" do |ctl01|
    ctl01.vm.box = config.vm.box
    ctl01.vm.provision "shell", inline: $script.sub(/{{x}}/, "ctl01")
    ctl01.vm.network "private_network", ip: "172.16.10.101"
    ctl01.vm.network "private_network", ip: "192.168.10.101"
  end

  config.vm.define "ctl02" do |ctl02|
    ctl02.vm.box = config.vm.box
    ctl02.vm.provision "shell", inline: $script.sub(/{{x}}/, "ctl02")
    ctl02.vm.network "private_network", ip: "172.16.10.102"
    ctl02.vm.network "private_network", ip: "192.168.10.102"
  end

  config.vm.define "ctl03" do |ctl03|
    ctl03.vm.box = config.vm.box
    ctl03.vm.provision "shell", inline: $script.sub(/{{x}}/, "ctl03")
    ctl03.vm.network "private_network", ip: "172.16.10.103"
    ctl03.vm.network "private_network", ip: "192.168.10.103"
  end

  config.vm.define "cmp01" do |cmp01|
    cmp01.vm.box = config.vm.box
    cmp01.vm.provision "shell", inline: $script.sub(/{{x}}/, "cmp01")
    cmp01.vm.network "private_network", ip: "172.16.10.105"
    cmp01.vm.network "private_network", ip: "192.168.10.105"

    cmp01.vm.provider "virtualbox" do |vb|
       vb.memory = "2048"
    end
  end

  config.vm.define "prx01" do |prx01|
    prx01.vm.box = config.vm.box
    prx01.vm.provision "shell", inline: $script.sub(/{{x}}/, "prx01")
    prx01.vm.network "private_network", ip: "172.16.10.107"
    prx01.vm.network "private_network", ip: "192.168.10.107"

    prx01.vm.provider "virtualbox" do |vb|
       vb.memory = "2048"
    end
  end



end
```



