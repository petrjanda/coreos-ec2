""" Module to execute EC2 cluster launch """

import boto3 as aws

import logging
from lib.security_group \
    import create_security_group, find_security_group, find_security_group_by_name

from .cluster import Cluster

class ClusterLauncher:
    """ Cluster formation """

    def __init__(self):
        self.ec2 = aws.resource('ec2')
        self.client = aws.client('ec2')

    def launch(self, conf):
        """ Launch new cluster according to provided conf """

        cluster_name = conf.cluster_name

        groups = [add_security_group(g) for g in conf.security_groups]
        group_ids = [g.id for g in groups]

        # key_pair_name = self.create_key_pair(cluster_name).name

        instance_props = conf.props
        instance_props['SecurityGroupIds'] = group_ids

        logging.info("--> Creating instances")
        instances = self.ec2.create_instances(**instance_props)

        logging.info("--> Tagging instances with cluster name '%s'" % cluster_name)
        for i, instance in enumerate(instances):
            instance.create_tags(
                Tags=[
                    {'Key': 'Name', 'Value': cluster_name + '-' + str(i + 1)},
                    {'Key': 'Cluster', 'Value': cluster_name}
                ]
            )

        logging.info("--> Waiting for instances to be in 'running' state")
        for i, instance in enumerate(instances):
            instance.wait_until_running()

        if conf.allocate_ip_address is True:
            logging.info("--> Creating IP addresses")
            for instance in instances:
                ip_address = self.client.allocate_address(
                    Domain='standard'
                )

                self.client.associate_address(
                    InstanceId=instance.id,
                    PublicIp=ip_address['PublicIp']
                )

        return Cluster(cluster_name)

    def create_key_pair(self, cluster_name):
        """ Create new keypair """

        key_pair = self.ec2.create_key_pair(
            KeyName=cluster_name
        )

        key_pair.save('./' + cluster_name + '.pem')

        return key_pair

def add_security_group(kwargs):
    """ Find or create a security group """

    if kwargs['action'] == 'find':
        return find_security_group(kwargs['name'])

    elif kwargs['action'] == 'find_or_create':
        group = find_security_group_by_name(kwargs['name'])

        if group is None:
            return create_security_group(kwargs)

        return group
    else:
        return create_security_group(kwargs)
