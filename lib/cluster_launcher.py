import boto3 as aws

from .cluster import Cluster

class ClusterLauncher:
  """ Cluster formation """

  coreos_ami = { 
    "eu-west-1": { 
      "pv": "ami-0c10417b" 
    },

    "eu-central-1": { 
      "pv": "ami-b8cecaa5" 
    },

    "us-east-1": { 
      'pv': 'ami-3b73d350',
      'hvm': 'ami-3d73d356'
    }
  }

  def __init__(self, region, key_name):
    self.ec2 = aws.resource('ec2')
    self.key_name = key_name
    self.region = region

  def launch(self, cluster_name, cloud_config, count = 1, instance_type = 'm1.small'):
    image_type = 'hvm'
    self.ami = self.coreos_ami[self.region][image_type]

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

    print("--> Creating %s instances" % count)
    instances = self.ec2.create_instances(
      ImageId=self.ami, 
      UserData=cloud_config,
      MinCount=1, 
      MaxCount=count,
      KeyName=self.key_name,
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

    print("--> Tagging instances with cluster name '%s'" % cluster_name)
    for i, instance in enumerate(instances):
      instance.create_tags(
        Tags=[
          {'Key': 'Name', 'Value': cluster_name + '-' + str(i + 1)},
          {'Key': 'Cluster', 'Value': cluster_name}
        ]
      )

    print("--> Waiting for instances to be in 'running' state")
    for i, instance in enumerate(instances):
      instance.wait_until_running()

    return Cluster(self.ec2, cluster_name)


