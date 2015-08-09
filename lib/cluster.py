import boto3 as aws

class Cluster:
    """ CoreOS cluster """

    def __init__(self, name):
        self.name = name
        self.ec2 = aws.resource('ec2')

    @property
    def instances(self):
        return self.ec2.instances.filter(
            Filters=[
                {'Name': 'tag-key', 'Values': ['Cluster']},
                {'Name': 'tag-value', 'Values': [self.name]},
            ]
        )

    @property
    def status(self):
        statuses = set([i.state['Name'] for i in list(self.instances)])

        if(len(statuses) > 1):
            raise Exception("Cluster in inconsistent state '%s'!" % statuses)

        return list(statuses)[0]

    def terminate(self):
        print('--> Terminate instances')
        self.instances.terminate()
        for instance in self.instances:
            instance.wait_until_terminated()

    def stop(self):
        print('--> Stop instances')
        self.instances.stop()
        for instance in self.instances:
            instance.wait_until_stopped()

    def start(self):
        print('--> Start instances')
        self.instances.start()
        for instance in self.instances:
            instance.wait_until_started()

    def cleanup(self):
        print("--> Delete security group '%s'" % self.name)
        aws.client('ec2').delete_security_group(
            GroupName = self.name
        )

    def find_instances(self):
        return self.ec2.instances.filter(
            Filters=[
                {'Name': 'tag-key', 'Values': ['Cluster']},
                {'Name': 'tag-value', 'Values': [self.name]},
            ]
        )
      
    def exists(self):
        return len(list(self.instances)) > 0
