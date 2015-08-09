import os, sys, argparse, botocore
import lib.env as env

from lib.cluster import Cluster
from lib.cluster_launcher import ClusterLauncher
from lib.cloud_config import CloudConfig

env.check()

parser = argparse.ArgumentParser()
parser.add_argument("cluster_name")
parser.add_argument("default_key_pair_name")
parser.add_argument("instances_count")
parser.add_argument("cloud_config_path")
args = parser.parse_args()

region = os.getenv("AWS_DEFAULT_REGION")

print("--> Fetching CoreOS etcd discovery token")
cloud_config = CloudConfig(
  open(args.cloud_config_path).read()
).with_new_token(args.instances_count)

launcher = ClusterLauncher(
  region, args.default_key_pair_name
)

try:
  launcher.launch(
    args.cluster_name, 
    cloud_config, 
    count = int(args.instances_count),
    instance_type = 'c4.large'
  )

  instances = Cluster(args.cluster_name).instances

  print("--> " + str([i.public_dns_name for i in instances]))
except botocore.exceptions.WaiterError:
  print("--x Failed to launch instances, Please check your AWS console, some machines may be already running!") 
except:
  print("--x Unexpected error:", sys.exc_info())
