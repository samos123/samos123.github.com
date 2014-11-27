Title: Neutron Multiple allocation pools single subnet (Solve Fragmented floating ips problem)
Date: 2014-11-24 12:01
Author: Sam Stoelinga
Category: Openstack
Tags: openstack, networking, neutron
Slug: neutron-multiple-allocation-pools-single-subnet

In a lab environment in the university I only had access to a list of fragmented
public routable IP addresses in a single subnet. For example I got access to the following ips
50.15.15.10, 55.15.15.12-15, 55.15.15.17. But I am not allowed
to use 55.15.15.11 and 55.15.15.16. 

**Update**: The Openstack neutron API supports fragmented floating ips but not through the CLI.
You have to use the Python API like below:

    :::python
    import logging
    from neutronclient.neutron import client

    auth_url = "http://192.168.33.11:5000/v2.0"

    logging.basicConfig(level=logging.DEBUG)
    neutron = client.Client('2.0', username="admin", password="password", tenant_name="demo", auth_url=auth_url)

    print "".join(neutron.list_subnets())

    req = {"subnet": {"allocation_pools": [{"start": "10.0.2.3", "end": "10.0.2.15"}, {"start": "10.0.2.17", "end": "10.0.2.17"}, {"start": "10.0.2.19", "end": "10.0.2.254"}]}}

    neutron.update_subnet("d5d48930-7bfb-4f0c-8968-13f8af785868", req)



## Old hacky way:
It seems that currently the only way to solve this is to manually change the database
bypassing the API. I used the following SQL insert statements to solve my problem.
This is assuming that 55.15.15.10 is already part of the pool.

    :::sql
    use neutron;
    select * from ipallocationpools;
    +--------------------------------------+--------------------------------------+----------------+-----------------+
    | id                                   | subnet_id                            | first_ip       | last_ip         |
    +--------------------------------------+--------------------------------------+----------------+-----------------+
    | 78857059-658b-4027-909d-7b8c6d62e52f | c58d4e69-d614-4d05-91e5-95b5cc48b670 | 55.15.15.10    | 55.15.15.10     |
    | c2931835-050b-40a0-bfc6-6dcb833517f6 | eda970d4-21c0-4488-85b2-0d3d0000ebb9 | 192.168.111.2  | 192.168.111.254 |
    +--------------------------------------+--------------------------------------+----------------+-----------------+
    
    insert into ipallocationpools VALUES (UUID(), "c58d4e69-d614-4d05-91e5-95b5cc48b670", 
                                          "55.15.15.12", "55.15.15.15"); 
    insert into ipallocationpools VALUES (UUID(), "c58d4e69-d614-4d05-91e5-95b5cc48b670", 
                                          "55.15.15.17", "55.15.15.17"); 

After inserting the ips, the floating ips can be allocated automatically using horizon and be successfuly assigned to
instances. But please note that this is not officially supported and hacky! I haven't seen any
problems as of now, but there probably are some problems with this approach. I just used it
for testing.

### Side note
Previously in nova-network you could easily add single floating ips or smaller ranges within
a subnet. But with neutron the CLI and API's seems to not support this. So after looking at the
code I noticed that the data model in fact supports multiple allocation pools for a single subnet:

    :::py
    class IPAllocationPool(model_base.BASEV2, HasId):
        """Representation of an allocation pool in a Neutron subnet."""

        subnet_id = sa.Column(sa.String(36), sa.ForeignKey('subnets.id',
                                                           ondelete="CASCADE"),
                              nullable=True)
        first_ip = sa.Column(sa.String(64), nullable=False)
        last_ip = sa.Column(sa.String(64), nullable=False)
        available_ranges = orm.relationship(IPAvailabilityRange,
                                            backref='ipallocationpool',
                                            lazy="joined",
                                            cascade='all, delete-orphan')


    class Subnet(model_base.BASEV2, HasId, HasTenant):
        """Represents a neutron subnet.

        When a subnet is created the first and last entries will be created. These
        are used for the IP allocation.
        """

        name = sa.Column(sa.String(255))
        network_id = sa.Column(sa.String(36), sa.ForeignKey('networks.id'))
        ip_version = sa.Column(sa.Integer, nullable=False)
        cidr = sa.Column(sa.String(64), nullable=False)
        gateway_ip = sa.Column(sa.String(64))
        allocation_pools = orm.relationship(IPAllocationPool,
                                            backref='subnet',
                                            lazy="joined",
                                            cascade='delete')
    

