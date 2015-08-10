import boto3 as aws
import logging

from .cluster import Cluster

class ClusterLauncher:
  """ Cluster formation """

  def __init__(self):
      self.ec2 = aws.resource('ec2')

  def launch(self, cluster_name, cloud_config, ami, key_pair_name, count = 1, instance_type = 'm1.small'):
      group = self.create_security_group(cluster_name)

      # key_pair_name = self.create_key_pair(cluster_name).name

      logging.info("--> Creating %s instances of %s" % (count, ami))
      instances = self.ec2.create_instances(
          ImageId=ami, 
          UserData=cloud_config,
          MinCount=1, 
          MaxCount=count,
          KeyName=key_pair_name,
          SecurityGroupIds=[group.id],
          InstanceType=instance_type,
          Monitoring={
              'Enabled': True
          },

          BlockDeviceMappings=[
              {
                  'DeviceName': '/dev/sdb',
                  'Ebs': {
                      'VolumeSize': 100,
                      'VolumeType': 'gp2',
                      'DeleteOnTermination': True
                  }
              }
          ]
      )

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

      return Cluster(cluster_name)

  def create_key_pair(self, cluster_name):
    key_pair = self.ec2.create_key_pair(
        KeyName = cluster_name
    )

    key_pair.save('./' + cluster_name + '.pem')

    return key_pair

  def create_security_group(self, cluster_name):
      group = self.ec2.create_security_group(
          GroupName = cluster_name,
          Description = cluster_name + ' security'
      )

      group.authorize_ingress(
          SourceSecurityGroupName = cluster_name
      )

      group.authorize_ingress(
          IpProtocol = 'tcp',
          FromPort = 22,
          ToPort = 22,
          CidrIp = '0.0.0.0/0'
      )

      return group
