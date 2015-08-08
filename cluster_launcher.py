import boto3 as aws

from cluster import Cluster

class ClusterLauncher:
  """ Cluster formation """

  coreos_ami = { 
    "eu-west-1": { "pv": "ami-0c10417b" },
    "eu-central-1": { "pv": "ami-b8cecaa5" },
    "us-east-1": { "pv": "ami-3b73d350" },
  }

  def __init__(self, region, key_name, security_groups):
    self.ec2 = aws.resource('ec2')
    self.ami = self.coreos_ami[region]["pv"]
    self.key_name = key_name
    self.security_groups = security_groups 

  def launch(self, cluster_name, cloud_config, count = 1, instance_type = 'm1.small'):
    print("--> Creating instances")
    instances = self.ec2.create_instances(
      ImageId=self.ami, 
      UserData=cloud_config,
      MinCount=1, 
      MaxCount=count,
      KeyName=self.key_name,
      SecurityGroupIds=self.security_groups,
      InstanceType=instance_type,
      Monitoring={
        'Enabled': True
      }
    )

    print("--> Tagging instances")
    for i, instance in enumerate(instances):
      instance.create_tags(
        Tags=[
          {'Key': 'Name', 'Value': cluster_name + '-' + str(i + 1)},
          {'Key': 'Cluster', 'Value': cluster_name}
        ]
      )

    print("--> Waiting for instances")
    for i, instance in enumerate(instances):
      instance.wait_until_running()

    return Cluster(self.ec2, cluster_name)

