from botocore.exceptions import ClientError
import yaml
import unittest
import boto3 as aws
import botocore

class TestAmi(unittest.TestCase):


    def test_get_current_ami(self):

        f = open("tests/security_groups_test.yml")
        c = yaml.load(f.read())
        f.close()

        ec2 = aws.resource('ec2')
        client = aws.client('ec2')

        sg = c['security_groups'][0]

        group = ec2.create_security_group(
            GroupName=sg['name'],
            Description=sg['name'] + ' security'
        )

        try:
            for ingress in sg['ingress']:
                group.authorize_ingress(**ingress)
        except ClientError as e:
            print(e)
            client.delete_security_group(
                GroupName=sg['name']
            )

