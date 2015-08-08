import boto3 as aws
import os, sys, argparse
import env

from cluster import Cluster
from cluster_launcher import ClusterLauncher
from cloud_config import CloudConfig

env.check()

parser = argparse.ArgumentParser()
parser.add_argument("cluster_name")
parser.add_argument("default_security_group")
parser.add_argument("default_key_pair_name")
parser.add_argument("instances_count")
parser.add_argument("cloud_config_path")
args = parser.parse_args()

region = os.getenv("AWS_DEFAULT_REGION")

print("--> Updating cloud-config")
cloud_config = CloudConfig(
  open(args.cloud_config_path).read()
).with_new_token(args.instances_count)

launcher = ClusterLauncher(
  region, args.default_key_pair_name, [args.default_security_group]
)

launcher.launch(
  args.cluster_name, 
  cloud_config, 
  count = int(args.instances_count)
)

instances = Cluster(aws.resource('ec2'), args.cluster_name).instances

print([i.public_dns_name for i in instances])
