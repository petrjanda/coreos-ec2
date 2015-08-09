import os, sys, argparse, botocore
import lib.env as env
import logging

from lib.cluster import Cluster
from lib.cluster_launcher import ClusterLauncher
from lib.cloud_config import CloudConfig
from lib.coreos import Ami as CoreOSAmi

env.check()

parser = argparse.ArgumentParser()
parser.add_argument("cluster_name")
parser.add_argument("instance_type")
parser.add_argument("instances_count")
parser.add_argument("key_pair_name")
parser.add_argument("cloud_config_path")
args = parser.parse_args()

region = os.getenv("AWS_DEFAULT_REGION")

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

logging.info("--> Fetching CoreOS etcd discovery token")
cloud_config = CloudConfig(
  open(args.cloud_config_path).read()
).with_new_token(args.instances_count)

try:
  launcher = ClusterLauncher()
  ami = CoreOSAmi.get_ami(region, args.instance_type)

  launcher.launch(
    args.cluster_name, 
    cloud_config, 
    ami,
    args.key_pair_name,
    count = int(args.instances_count),
    instance_type = args.instance_type
  )

  instances = Cluster(args.cluster_name).instances

  logging.info("--> " + str([i.public_dns_name for i in instances]))
except botocore.exceptions.WaiterError:
  logging.error("--x Failed to launch instances, Please check your AWS console, some machines may be already running!") 
