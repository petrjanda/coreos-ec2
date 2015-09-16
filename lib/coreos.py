import os, sys, argparse, botocore, logging
import lib.utils as utils
import yaml

from lib.cluster_conf import ClusterConf
import lib.cloud_config

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
    },

    "us-west-2": {
        'pv': 'ami-87ada4b7',
        'hvm': 'ami-85ada4b5'
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

    cloud_config = lib.cloud_config.with_new_token(
        cloud_config_file.read(), instances_count
    )
    cloud_config_file.close()

    return ClusterConf(
        cluster_name, ami, key_pair_name, 
        user_data = cloud_config,
        instance_type = instance_type, 
        instances_count = instances_count, 
        allocate_ip_address = allocate_ip_address
    )

def read_conf(cluster_name, path):
    f = open(path)
    c = f.read().replace('$cluster_name', cluster_name)
    c = yaml.load(c)
    f.close()

    conf = get_cluster_conf(
        cluster_name, 
        c['region'], 
        c['cloud_config'], 
        c['key_pair'],
        instances_count = int(c['instances_count']),
        instance_type = c['instance_type'],
        allocate_ip_address = c['allocate_ip_address']
    )

    for v in c['volumes']:
        conf = conf.volume(**camelize_dict(v))

    for s in c['security_groups']:
        conf = conf.security_group(**s)

    return conf

def camelize_dict(d):
    """ Map dictionary keys to camel case (deeply for nested dicts) """

    if not isinstance(d, dict):
        return d

    return dict([(to_camel_case(v[0]), camelize_dict(v[1])) for v in d.items()])

def to_camel_case(snake_str):
    """ Transform snake case string to camel case """

    return "".join(x.title() for x in snake_str.split('_'))
