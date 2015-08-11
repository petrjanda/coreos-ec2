import unittest
import lib.coreos

class TestAmi(unittest.TestCase):
    def test_get_ami(self):
        ami = lib.coreos.get_ami('us-east-1', 'c4.xlarge')
        self.assertEqual(ami, 'ami-3d73d356')
