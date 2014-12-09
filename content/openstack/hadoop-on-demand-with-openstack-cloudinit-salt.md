Title: Hadoop on demand with Openstack, Cloudinit and Salt
Date: 2014-11-27 13:12
Author: Sam Stoelinga
Category: Openstack
Tags: openstack, salt, cloudinit, cloudconfig, hadoop, devops
Slug: hadoop-on-demand-with-openstack-cloudinit-salt

This post will describe the whole process of providing hadoop on demand
through Openstack, Cloudinit and Saltstack. We will use Openstack
to provision servers on demand, cloudconfig to install salt-master and
salt-minion and saltstack to deploy hadoop namenode and datanodes, all fully
automated. This makes us able to deploy a 5-100+ node (still need to test 20+) Hadoop HDFS
cluster within 5 minutes.

## Deploy salt-master with Cloudconfig
We will install and configure salt-master to
auto\_accept key files from the minions. Please note
that this is a security risk.

Create the following master-cloudconfig file:

    :::yaml
    #cloud-config
    apt_mirror: http://mirror.bjtu.edu.cn/ubuntu/

    apt_sources:
     - source: "ppa:saltstack/salt"

    packages:
     - python-software-properties
     - salt-master
     - git

    runcmd:
     - bash /tmp/bootstrap-master.sh

    write_files
     - content: |
            #!/bin/bash
            sed -i 's/^#auto_accept.*$/auto_accept: True/g' /etc/salt/master
            sudo service salt-master restart
       path: /tmp/bootstrap-master.sh
       permissions: "0755"


Now launch openstack instance with: `nova boot --image ubuntu_14.04 --user-data master-cloudconfig --flavor m1.medium --key-name sam salt_master`.
The salt-master that we launched in our case has as ip 192.168.111.66. You can ssh to this machine via ssh ubuntu@192.168.111.66


## Configuring the salt master to deploy a hadoop cluster
In order to be able to deploy hadoop on the salt-master we are going to
manually configure the salt-master with the official hadoop formula.
We could also automate this via cloudconfig, but for sake of demonstration
I'm going to list the manual steps here.

### Configuring salt to use hadoop-formula and it's dependencies
We are going to use the following formula: [Hadoop formula](https://github.com/saltstack-formulas/hadoop-formula), which
has as dependencies the [hostsfile-formula](https://github.com/saltstack-formulas/hostsfile-formula) and the
[sun-java-formula](https://github.com/saltstack-formulas/sun-java-formula).
The hostsfile formula is to make all nodes accessible by their hostname/fqdn and
the sun-java-formula lets you automatically install java from oracle.

    :::bash
    ssh ubuntu@192.168.111.66 # SSH into your salt-master
    sudo mkdir /srv/salt
    sudo mkdir /srv/salt/formulas
    sudo "cd /srv/salt/formulas && 
          git clone https://github.com/saltstack-formulas/hadoop-formula
          git clone https://github.com/saltstack-formulas/hostsfile-formula &&
          git clone https://github.com/saltstack-formulas/sun-java-formula"
    
    cat << EOF > /etc/salt/master.d/file_roots.conf
    file_roots:
      base:
        - /srv/salt
        - /srv/salt/formulas/hadoop-formula
        - /srv/salt/formulas/hostsfile-formula
        - /srv/salt/formulas/sun-java-formula
    EOF

    cat << EOF > /etc/salt/master.d/pillar_roots.conf
    pillar_roots:
      base:
        - /srv/pillar
    EOF

    sudo service salt-master restart


### Creating SSH keypairs for hadoop-formula

    :::bash
    cd /srv/salt/formulas/hadoop-formula/hadoop/files && ./generate-keypairs.sh


### Configuring the top.sls state file to include hadoop and deps

On the salt-master create the following file /srv/salt/top.sls:

    :::yaml
    base:
      'G@roles:hadoop_slave or G@roles:hadoop_master':
        - match: compound
        - hostsfile
        - hostsfile.hostname
        - sun-java
        - sun-java.env
        - hadoop
        - hadoop.hdfs

By using [pillar](http://docs.saltstack.com/en/latest/topics/pillar/) we can also change the parameters of hadoop.
You can check all available parameters that are change-able here: 
[hadoop-pillar.example](https://github.com/saltstack-formulas/hadoop-formula/blob/master/pillar.example).

Create the following top.sls pillar file /srv/pillar/top.sls:

    :::yaml
    base:
      'G@roles:hadoop_slave or G@roles:hadoop_master':
         - hadoop

and the following hadoop specific pillar file /srv/pillar/hadoop.sls:

    :::yaml
    hadoop:
      version: hdp-2.2.0 # ['apache-1.2.1', 'apache-2.2.0', 'hdp-1.3.0', 'hdp-2.2.0', 'cdh-4.5.0', 'cdh-4.5.0-mr1']
      users:
        hadoop: 6000
        hdfs: 6001


## Deploy salt-minions as hadoop nodes
Now that we have configured our salt-master we can start
deploying the salt-minions which will either server as hadoop-master(namenode)
or as hadoop-slave(datanode).

### Launching hadoop-master(namenode) nodes
First create our cloudconfig file used by openstack hadoopmaster-cloudconfig:

    :::yaml
    #cloud-config
    apt_mirror: "http://mirror.bjtu.edu.cn/ubuntu/"
    apt_sources: 
      - source: "ppa:saltstack/salt"
    packages: 
      - python-software-properties
      - salt-minion

    runcmd: 
     - bash /tmp/bootstrap-minion.sh

    write_files: 
      - content: |
             roles:
                - hadoop_master
        path: /etc/salt/grains
      - content: |
            #!/bin/bash
            sed -i 's/^#master.*$/master: 192.168.111.66/g' /etc/salt/minion
            sudo service salt-minion restart
        path: /tmp/bootstrap-minion.sh
        permissions: "0755"
      - content: |
            mine_functions:
                network.interfaces: []
                network.ip_addrs: []
                grains.items: []
        path: /etc/salt/minion.d/mine_functions.conf

Then create a new instance using openstack:
`nova boot --image ubuntu_14.04 --user-data hadoopmaster-cloudconfig --flavor m1.medium --key-name sam hadoop-master-1`

### Deploying hadoop-slave(datanode) nodes
Create a hadoopslave-cloudconfig:

    :::yaml
    #cloud-config
    apt_mirror: "http://mirror.bjtu.edu.cn/ubuntu/"
    apt_sources: 
      - source: "ppa:saltstack/salt"
    packages: 
      - python-software-properties
      - salt-minion

    runcmd: 
     - bash /tmp/bootstrap-minion.sh

    write_files: 
      - content: |
             roles:
                - hadoop_slave
        path: /etc/salt/grains
      - content: |
            #!/bin/bash
            sed -i 's/^#master.*$/master: 192.168.111.66/g' /etc/salt/minion
            sudo service salt-minion restart
        path: /tmp/bootstrap-minion.sh
        permissions: "0755"
      - content: |
            mine_functions:
                network.interfaces: []
                network.ip_addrs: []
                grains.items: []
        path: /etc/salt/minion.d/mine_functions.conf

Now launch 10 hadoop-slave nodes
`nova boot --num-instances 10 --image ubuntu_14.04 --user-data hadoopslave-cloudconfig --flavor m1.medium --key-name sam hadoop-slave`

### Let saltstack deploy hadoop
First make sure that the salt-master detected all our hadoop-master and hadoop-slave nodes. Execute the following comand: `salt '*' managed.up`
it should show your 11 nodes.

If all nodes are up and detected you can start deployment of hadoop with the following command:

    :::bash
    salt '*' state.highstate


## Accessing the hadoop HDFS cluster
After hadoop has been successfully deployed you can go to http://{hadoop\_masterip}:50070 and check that
10 live nodes are active.

Now you can login to any of the nodes and save files to hdfs like this:

    :::bash
    sudo -u hdfs -i
    hadoop fs -mkdir -p /user/hdfs"
    hadoop fs -put /tmp/bootstrap-minion.sh /user/hdfs/test.sh


Hope this tutorial was useful! 

Notes: You can also configure
[salt-minion directly through cloudconfig](https://github.com/number5/cloud-init/blob/master/doc/examples/cloud-config-salt-minion.txt) instead.
