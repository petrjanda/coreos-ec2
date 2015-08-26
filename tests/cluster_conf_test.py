import unittest
import lib.coreos
from lib.cluster_conf import ClusterConf

class TestClusterConf(unittest.TestCase):
    args = ['s-1', 'ami', 'key_pair']

    def test_basic(self):
        conf = ClusterConf(*self.args)
        self.assertEqual(conf.instance_type, 'm1.small')
        self.assertEqual(conf.cluster_name, 's-1')
        self.assertEqual(conf.ami, 'ami')
        self.assertEqual(conf.key_pair_name, 'key_pair')

    def test_default_instances_count(self):
        conf = ClusterConf(*self.args)
        self.assertEqual(conf.instances_count, 1)

    def test_instance_type(self):
        conf = ClusterConf(*self.args, instance_type = 'c4.large')
        self.assertEqual(conf.instance_type, 'c4.large')

    def test_props_with_instances_count(self):
        conf = ClusterConf(*self.args, instances_count = 2)
        self.assertEqual(conf.props, {
            'ImageId': 'ami', 
            'UserData': '',
            'MinCount':1, 
            'MaxCount':2,
            'KeyName':'key_pair',
            'InstanceType':'m1.small',
            'Monitoring':{
                'Enabled': True
            },

            'BlockDeviceMappings': []
        })

    def test_volume(self):
        conf = ClusterConf(*self.args, instances_count = 2) \
        .volume(
            DeviceName='/dev/sdb', 
            Ebs=dict(VolumeSize=100,VolumeType='gp2', DeleteOnTermination = True)
        )

        self.assertEqual(conf.block_device_mappings, [
            {
                'DeviceName': '/dev/sdb',
                'Ebs': {
                    'VolumeSize': 100,
                    'VolumeType': 'gp2',
                    'DeleteOnTermination': True
                }
            }
        ])

    def test_empheral_volume(self):
        conf = ClusterConf(*self.args, instances_count = 2) \
        .volume(
            DeviceName='/dev/sdb', 
            VirtualName='empheral0'
        )

        self.assertEqual(conf.block_device_mappings, [
            {
                'DeviceName': '/dev/sdb',
                'VirtualName': 'empheral0'
            }
        ])


    def test_security_groups(self):
        conf = ClusterConf(*self.args, instances_count = 2) \
            .security_group(
                action = 'find',
                name = 'ssh'
            ) \
            .security_group(
                action = 'create',
                name = 'spark',
                allow_inbound = [
                    dict(protocol = 'tcp', from_port = 8080, to_port = 8080, ip = '0.0.0.0/0')
                ]
            )

        self.assertEqual(conf.security_groups, [
            dict(
                action = 'find',
                name = 'ssh'
            ),
            dict(
                action = 'create',
                name = 'spark',
                allow_inbound = [
                    dict(protocol = 'tcp', from_port = 8080, to_port = 8080, ip = '0.0.0.0/0')
                ]
            )

        ])

