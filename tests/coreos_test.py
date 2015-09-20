import unittest, json
import lib.coreos as coreos
import lib.utils as utils
from unittest.mock import patch

from unittest.mock import patch

class RequestMock:
    def __init__(self, text):
        self.text = text

    def text(self):
        return self.text

class TestAmi(unittest.TestCase):

    def assert_ami_matches(self, version, channel, region, instance_type, category):
        ami = coreos.get_ami(version, channel, region, instance_type)
        ami_file = utils.download_file_as_string(coreos.release_metadata_url(channel, version, coreos.ami_list_file_name))
        stable_current_amis = json.loads(ami_file)
        expected_ami = [ ami for ami in stable_current_amis['amis'] if ami['name'] == region ][0][category]
        self.assertEqual(ami, expected_ami)

    def test_get_current_ami(self):
        self.assert_ami_matches('current', 'stable', 'us-east-1', 'c4.xlarge', 'hvm')

    @patch('lib.coreos.confirm_version_change', return_value='i')
    def test_get_old_ami(self, input):
        self.assert_ami_matches('801.0.0', 'alpha', 'eu-central-1', 'm1.small', 'pv')

    @patch('lib.coreos.confirm_version_change', return_value='e')
    def test_get_old_ami(self, input):
        # "Session should have exited because user doesn't ignore coreos version change"
        with self.assertRaises(SystemExit):
            coreos.get_ami('801.0.0', 'alpha', 'eu-central-1', 'm1.small')

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

