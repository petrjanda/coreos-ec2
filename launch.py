import boto3 as aws
import os, sys
import argparse
from cluster import Cluster
from cluster_launcher import ClusterLauncher

# Check necessary configuration
if os.getenv('AWS_ACCESS_KEY_ID') is None:
  print("ERROR: The environment variable AWS_ACCESS_KEY_ID must be set", file=sys.stderr)
  sys.exit(1)

if os.getenv('AWS_SECRET_ACCESS_KEY') is None:
  print("ERROR: The environment variable AWS_SECRET_ACCESS_KEY must be set", file=sys.stderr)
  sys.exit(1)

if os.getenv('AWS_DEFAULT_REGION') is None:
  print("ERROR: The environment variable AWS_DEFAULT_REGION must be set", file=sys.stderr)
  sys.exit(1)

parser = argparse.ArgumentParser()
parser.add_argument("cluster_name")
parser.add_argument("default_security_group")
parser.add_argument("default_key_pair_name")
parser.add_argument("instances_count")
parser.add_argument("cloud_config_path")
args = parser.parse_args()

# Launcher
# default_security_group = 'sg-561fb433'

region = os.getenv("AWS_DEFAULT_REGION")
user_data = open(args.cloud_config_path).read()
launcher = ClusterLauncher(aws, region, args.default_key_pair_name, [args.default_security_group])
launcher.launch(args.cluster_name, user_data, count = int(args.instances_count))

instances = Cluster(aws.resource('ec2'), args.cluster_name).instances

print([i.public_dns_name for i in instances])
