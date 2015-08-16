import boto3 as aws
import itertools
import botocore
import logging

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
        logging.info('--> Terminate instances')
        self.instances.terminate()
        for instance in self.instances:
            instance.wait_until_terminated()

    def stop(self):
        logging.info('--> Stop instances')
        self.instances.stop()
        for instance in self.instances:
            instance.wait_until_stopped()

    def start(self):
        logging.info('--> Start instances')
        self.instances.start()
        for instance in self.instances:
            instance.wait_until_running()

    def cleanup(self):
        logging.info("--> Delete security groups")
        groups = set([g['GroupId'] for g in itertools.chain(*map(lambda i: i.security_groups, self.instances))])
        
        self.terminate()

        for g in groups:
            try:
                self.ec2.SecurityGroup(g).delete()

                logging.info("--> " + g + " deleted")
            except botocore.exceptions.ClientError as e:
                logging.info("--> " + g + " couldn't be deleted")
      
    def exists(self):
        return len(list(self.instances)) > 0
