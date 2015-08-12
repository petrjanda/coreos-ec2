import boto3 as aws
import logging

from .cluster import Cluster

class ClusterLauncher:
  """ Cluster formation """

  def __init__(self):
      self.ec2 = aws.resource('ec2')
      self.client = aws.client('ec2')

  def launch(self, conf):
      cluster_name = conf.cluster_name
      count = conf.instances_count
      instance_type = conf.instance_type

      groups = [self.create_security_group(g) for g in conf.security_groups]
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

      if(conf.allocate_ip_address is True):
          logging.info("--> Creating IP addresses")
          for instance in instances:
              ip_address = self.client.allocate_address(
                  Domain = 'standard'
              )

              self.client.associate_address(
                  InstanceId = instance.id,
                  PublicIp = ip_address['PublicIp']
              )

      return Cluster(cluster_name)

  def create_key_pair(self, cluster_name):
    key_pair = self.ec2.create_key_pair(
        KeyName = cluster_name
    )

    key_pair.save('./' + cluster_name + '.pem')

    return key_pair

  def create_security_group(self, **kwargs):
      if(kwargs['name']): # <<< if only name
          return self.ec2.security_group(
              Name = kwargs['name']
          )

      group = self.ec2.create_security_group(
          GroupName = kwargs['name'],
          Description = kwargs['name'] + ' security'
      )

      if(kwargs['allow_all_own_traffic'] is True):
          group.authorize_ingress(
              SourceSecurityGroupName = cluster_name
          )

      for inbound in kwargs['allow_inbound']:
          group.authorize_ingress(
              IpProtocol = inbound['protocol'],
              FromPort = inbound['from_port'],
              ToPort = inbound['to_port'],
              CidrIp = inbound['ip']
          )

      return group
