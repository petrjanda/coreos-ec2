import os, sys, argparse, botocore, utils, logging
from lib.coreos import get_ami
from lib.cluster_conf import ClusterConf 
from lib.cloud_config import CloudConfig

class CoreOSClusterConf(ClusterConf):
  def __init__(self, cluster_name, region, cloud_config_path, key_pair_name, instance_type = 'm1.small', instances_count = 1, allocate_ip_address = False):
        ami = get_ami(region, instance_type)

        logging.info("--> Fetching CoreOS etcd discovery token")
        cloud_config = CloudConfig(
            open(cloud_config_path).read()
        ).with_new_token(instances_count)

        super(CoreOSClusterConf, self).__init__(
            cluster_name, ami, key_pair_name, 
            user_data = cloud_config,
            instance_type = instance_type, 
            instances_count = instances_count, 
            allocate_ip_address = allocate_ip_address
        )
