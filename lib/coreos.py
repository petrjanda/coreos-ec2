import os, sys, argparse, botocore, logging, json
import lib.utils as utils
import yaml

from lib.cluster_conf import ClusterConf
import lib.cloud_config

channels = ["alpha", "beta", "stable"]
ami_list_file_name = "coreos_production_ami_all.json"
version_file_name = "version.txt"

image_types = {
    't2': 'hvm',
    'm1': 'pv',
    'c4': 'hvm'
}

def coreos_release_metadata_url(channel, file_name):
    return "http://{0}.release.core-os.net/amd64-usr/current/{1}".format(channel, file_name)

def get_ami(channel, region, instance_type):
    ami_file_path = "ami/{0}/{1}".format(channel, ami_list_file_name)
    amis = utils.file_to_json(ami_file_path)
    image_type = image_types[instance_type.split('.')[0]]
    return [ ami for ami in amis['amis'] if ami['name'] == region ][0][image_type]

def get_cluster_conf(cluster_name, region, cloud_config_path, key_pair_name, coreos_channel, instance_type = 'm1.small', instances_count = 1, allocate_ip_address = False):
    ami = get_ami(coreos_channel, region, instance_type)

    logging.info("--> Fetching CoreOS etcd discovery token")
    cloud_config_file = open(cloud_config_path)

    cloud_config = lib.cloud_config.with_new_token(
        cloud_config_file.read(), instances_count
    )
    cloud_config_file.close()

    return ClusterConf(
        cluster_name, ami, key_pair_name, coreos_channel,
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
        c['coreos_channel'],
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

def update_amis():

    for channel in channels:
        version_file_url = coreos_release_metadata_url(channel, version_file_name)
        ami_list_file_url = coreos_release_metadata_url(channel, ami_list_file_name)
        logging.info("downloading " + version_file_url)
        logging.info("downloading " + ami_list_file_url)
        utils.download_file(version_file_url, "ami/{0}/{1}".format(channel, version_file_name))
        utils.download_file(ami_list_file_url, "ami/{0}/{1}".format(channel, ami_list_file_name))