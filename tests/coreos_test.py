import unittest
import lib.coreos as coreos
import lib.utils as utils

from unittest.mock import patch

class RequestMock:
    def __init__(self, text):
        self.text = text

    def text(self):
        return self.text

class TestAmi(unittest.TestCase):
    def test_get_ami(self):
        ami = coreos.get_ami('stable', 'us-east-1', 'c4.xlarge')
        stable_amis = utils.file_to_json("ami/stable/" + coreos.ami_list_file_name)
        expected_ami = [ ami for ami in stable_amis['amis'] if ami['name'] == 'us-east-1' ][0]['hvm']
        self.assertEqual(ami, expected_ami)

    @patch('lib.cloud_config.requests.get', return_value=RequestMock("test"))
    def test_get_cluster_conf(self, req):
        conf = coreos.get_cluster_conf(
            'p-1',
            'us-east-1',
            'tests/fixtures/cloud-config',
            'key_pair',
            coreos_channel = 'stable',
            instances_count = 2,
            instance_type = 'c4.large',
            allocate_ip_address = False
        )

        req.assert_called_with('https://discovery.etcd.io/new?size=2')

        self.assertEqual(conf.props, {
            'ImageId': 'ami-3d73d356',
            'UserData': '#cloud-config\n\ncoreos:\n  etcd2:\n    discovery: test\n',
            'MinCount':1,
            'MaxCount':2,
            'KeyName':'key_pair',
            'InstanceType':'c4.large',
            'Monitoring':{
                'Enabled': True
            },

            'BlockDeviceMappings': []
        })

