import os, sys, argparse, botocore, utils, logging
from lib.cluster_conf import ClusterConf
from lib.cloud_config import CloudConfig

coreos_ami = { 
    "eu-west-1": { 
        "pv": "ami-0c10417b" 
    },

    "eu-central-1": { 
        "pv": "ami-b8cecaa5" 
    },

    "us-east-1": { 
        'pv': 'ami-3b73d350',
        'hvm': 'ami-3d73d356'
    }
}

image_types = {
    't2': 'hvm',
    'm1': 'pv',
    'c4': 'hvm'
}

def get_ami(region, instance_type):
    image_type = image_types[instance_type.split('.')[0]]

    return coreos_ami[region][image_type]

def get_cluster_conf(cluster_name, region, cloud_config_path, key_pair_name, instance_type = 'm1.small', instances_count = 1, allocate_ip_address = False):
    ami = get_ami(region, instance_type)

    logging.info("--> Fetching CoreOS etcd discovery token")
    cloud_config_file = open(cloud_config_path)
    cloud_config = CloudConfig(
        cloud_config_file.read()
    ).with_new_token(instances_count)
    cloud_config_file.close()

    return ClusterConf(
        cluster_name, ami, key_pair_name, 
        user_data = cloud_config,
        instance_type = instance_type, 
        instances_count = instances_count, 
        allocate_ip_address = allocate_ip_address
    )
