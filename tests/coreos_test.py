import unittest
import lib.coreos
from unittest.mock import patch

class RequestMock:
    def __init__(self, text):
        self.text = text

    def text(self):
        return self.text

class TestAmi(unittest.TestCase):
    def test_get_ami(self):
        ami = lib.coreos.get_ami('us-east-1', 'c4.xlarge')
        self.assertEqual(ami, 'ami-3d73d356')

    @patch('lib.cloud_config.requests.get', return_value=RequestMock("test"))
    def test_get_cluster_conf(self, req):
        conf = lib.coreos.get_cluster_conf(
            'p-1', 
            'us-east-1', 
            'tests/fixtures/cloud-config', 
            'key_pair',
            instances_count = 2,
            instance_type = 'c4.large',
            allocate_ip_address = False
        )

        self.assertEqual(conf.props, {
            'ImageId': 'ami-3d73d356', 
            'UserData': '#cloud-config\n',
            'MinCount':1, 
            'MaxCount':2,
            'KeyName':'key_pair',
            'InstanceType':'c4.large',
            'Monitoring':{
                'Enabled': True
            },

            'BlockDeviceMappings': []
        })

