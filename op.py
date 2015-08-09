import os, sys
import argparse
import lib.env as env
import utils

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
  print(cluster.status)

elif args.op == "stop":
  cluster.stop()

elif args.op == "start":
  cluster.start()

elif args.op == "cleanup":
  utils.confirm("You are about to terminate and remove the whole cluster.")
  cluster.terminate()
  cluster.cleanup()
