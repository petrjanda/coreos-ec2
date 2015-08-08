import boto3 as aws

class Cluster:
  """ CoreOS cluster """

  def __init__(self, ec2, name):
    self.name = name
    self.ec2 = aws.resource('ec2')

  @property
  def instances(self):
    if not self.exists():
      raise Exception("Cluster %s doesn't exist!" % self.name)

    return self.find_instances()

  @property
  def status(self):
    statuses = set([i.state['Name'] for i in list(self.find_instances())])

    if(len(statuses) > 1):
      raise Exception("Cluster in inconsistent state '%s'!" % statuses)

    return list(statuses)[0]

  def terminate(self):
    self.instances.terminate()

  def find_instances(self):
    return self.ec2.instances.filter(
      Filters=[
        {'Name': 'tag-key', 'Values': ['Cluster']},
        {'Name': 'tag-value', 'Values': [self.name]},
      ]
    )
    
  def exists(self):
    return len(list(self.ec2.instances.filter(
      Filters=[
        {'Name': 'tag-key', 'Values': ['Cluster']},
        {'Name': 'tag-value', 'Values': [self.name]},
#        {'Name': 'instance-state-name', 'Values': ['running']}
      ]
    ))) > 0

