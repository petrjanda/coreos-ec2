import os, sys
import argparse
import lib.env as env

from lib.cluster import Cluster
from lib.cluster_launcher import ClusterLauncher


env.check()

parser = argparse.ArgumentParser()
parser.add_argument("cluster_name")
parser.add_argument("op")
args = parser.parse_args()

cluster = Cluster(args.cluster_name)

if args.op == "dns":
  print([i.public_dns_name for i in cluster.instances])
elif args.op == "status":
  print([i.state['Name'] for i in cluster.instances])
elif args.op == "terminatecleanup":
  cluster.terminate()
  cluster.cleanup()
