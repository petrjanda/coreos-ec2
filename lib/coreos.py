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

def release_metadata_url(channel, version, file_name):
    return "http://{0}.release.core-os.net/amd64-usr/{1}/{2}".format(channel, version, file_name)

def confirm_version_change(msg):
    return input(msg).lower()

def get_ami(version, channel, region, instance_type):

    def resolve_current_version():
        version_file_url = release_metadata_url(channel, "current", version_file_name)
        version_metadata_file = utils.download_file_as_string(version_file_url)
        version_metadata_lines = version_metadata_file.split('\n')
        version_kv_pair = [ line for line in version_metadata_lines if line.startswith('COREOS_VERSION=') ][0]
        return version_kv_pair[15:]

    def version_as_float(numeric_version):
        return float(numeric_version[:numeric_version.rfind("."):])

    current_version = resolve_current_version()

    if version != "current" and version_as_float(current_version) != version_as_float(version):
        msg = "Current coreOS {0} channel version {1} differs from specified {2}, press 'i' to ignore it or 'e' to exit"
        choice = confirm_version_change(msg.format(channel, current_version, version))
        if not choice == 'i':
            sys.exit(0)

    ami_file_output = utils.download_file_as_string(release_metadata_url(channel, version, ami_list_file_name))
    amis = json.loads(ami_file_output)
    image_type = image_types[instance_type.split('.')[0]]
    return [ ami for ami in amis['amis'] if ami['name'] == region ][0][image_type]

def get_cluster_conf(cluster_name, region, cloud_config_path, key_pair_name, coreos_version, coreos_channel, instance_type='m1.small', instances_count=1, allocate_ip_address=False):
    ami = get_ami(coreos_version, coreos_channel, region, instance_type)

    logging.info("--> Fetching CoreOS etcd discovery token")
    cloud_config_file = open(cloud_config_path)

    cloud_config = lib.cloud_config.with_new_token(
        cloud_config_file.read(), instances_count
    )
    cloud_config_file.close()

    return ClusterConf(
        cluster_name, ami, key_pair_name, coreos_version, coreos_channel,
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
        c['coreos_version'],
        c['coreos_channel'],
        instances_count = int(c['instances_count']),
        instance_type = c['instance_type'],
        allocate_ip_address = c['allocate_ip_address']
    )

    for v in c['block_device_mappings']:
        conf = conf.volume(**v)

    for s in c['security_groups']:
        conf = conf.security_group(**s)

    return conf