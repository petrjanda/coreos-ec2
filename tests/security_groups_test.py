from botocore.exceptions import ClientError
import yaml
import unittest
import boto3 as aws
import lib.coreos as coreos
import lib.cluster_launcher as launcher


configuration = """
    security_groups:
      -
        name: es
        action: find_or_create
        authorize_ingress:
          -
            SourceSecurityGroupName: es
          -
            IpProtocol: tcp
            FromPort: 22
            ToPort: 22
            CidrIp: 91.219.244.207/32

"""

class TestSecurityGroups(unittest.TestCase):

    """
        def test_creating_security_groups(self):

            c = yaml.load(configuration)

            ec2 = aws.resource('ec2')
            client = aws.client('ec2')

            sg = c['security_groups'][0]

            group = ec2.create_security_group(
                GroupName=sg['name'],
                Description=sg['name'] + ' security'
            )

            try:
                for ingress in sg['authorize_ingress']:
                    group.authorize_ingress(**ingress)
            except ClientError as e:
                client.delete_security_group(
                    GroupName=sg['name']
                )
                raise e


        def test_add_security_group(self):
            conf = coreos.read_conf("whatever", "config/cluster-conf.yml.example")
            launcher.add_security_group(conf.security_groups[0])
    """