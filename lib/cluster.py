""" CoreOS Cluster """

import boto3 as aws
import itertools
import botocore
import logging

class Cluster:
    """ CoreOS Cluster """

    def __init__(self, name):
        self.name = name
        self.ec2 = aws.resource('ec2')

    @property
    def instances(self):
        """ List of instances within the cluster """
        return self.ec2.instances.filter(
            Filters=[
                {'Name': 'tag-key', 'Values': ['Cluster']},
                {'Name': 'tag-value', 'Values': [self.name]},
            ]
        )

    @property
    def status(self):
        """ Overall status of cluster instances """
        statuses = set([i.state['Name'] for i in list(self.instances)])

        if len(statuses) > 1:
            raise Exception("Cluster in inconsistent state '%s'!" % statuses)

        return list(statuses)[0]

    def terminate(self):
        """ Terminate the cluster """

        logging.info('--> Terminate instances')
        self.instances.terminate()
        for instance in self.instances:
            instance.wait_until_terminated()

    def stop(self):
        """ Stop the cluster """

        logging.info('--> Stop instances')
        self.instances.stop()
        for instance in self.instances:
            instance.wait_until_stopped()

    def start(self):
        """ Start the cluster """

        logging.info('--> Start instances')
        self.instances.start()
        for instance in self.instances:
            instance.wait_until_running()

    def cleanup(self):
        """ Cleanup and terminate the cluster (remove security groups) """

        logging.info("--> Delete security groups")
        instance_security_groups = map(lambda i: i.security_groups, self.instances)
        groups = set([g['GroupId'] for g in itertools.chain(*instance_security_groups)])

        self.terminate()

        for group in groups:
            try:
                self.ec2.SecurityGroup(group).delete()

                logging.info("--> " + group + " deleted")
            except botocore.exceptions.ClientError:
                logging.info("--> " + group + " couldn't be deleted")

    def exists(self):
        """ Check for cluster existence """

        return len(list(self.instances)) > 0
