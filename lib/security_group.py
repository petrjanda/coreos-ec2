import boto3 as aws
import botocore

ec2 = aws.resource('ec2')

def create_security_group(kwargs):
    """ Create new EC2 security group given the description """

    group = ec2.create_security_group(
        GroupName = kwargs['name'],
        Description = kwargs['name'] + ' security'
    )

    for ingress in kwargs['authorize_ingress']:
        group.authorize_ingress(**ingress)

    return group

def find_security_group(id):
    """ Find existing EC2 security group """

    return ec2.SecurityGroup(id)

def find_security_group_by_name(name):
    try:
        id = aws.client('ec2').describe_security_groups(
            GroupNames = [name]
        )['SecurityGroups'][0]['GroupId']

        return find_security_group(id)
    except botocore.exceptions.ClientError:
        return None

