import boto3 as aws
import botocore

ec2 = aws.resource('ec2')

def create_security_group(kwargs):
    """ Create new EC2 security group given the description """

    group = ec2.create_security_group(
        GroupName = kwargs['name'],
        Description = kwargs['name'] + ' security'
    )

    if('allow_all_own_traffic' in kwargs and kwargs['allow_all_own_traffic'] is True):
        group.authorize_ingress(
            SourceSecurityGroupName = kwargs['name']
        )

    if('allow_ssh_from' in kwargs):
        group.authorize_ingress(
            IpProtocol = 'tcp',
            FromPort = 22,
            ToPort = 22,
            CidrIp = kwargs['allow_ssh_from']
        )


    if('allow_inbound' in kwargs):
        for inbound in kwargs['allow_inbound']:
            group.authorize_ingress(
                IpProtocol = inbound['protocol'],
                FromPort = inbound['from_port'],
                ToPort = inbound['to_port'],
                CidrIp = inbound['ip']
            )

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

