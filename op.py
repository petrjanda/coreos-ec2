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

def confirm(message):
  choice = input(message + " Are you sure? y/n ").lower()
  if choice == 'y':
    return True
  else:
    sys.exit(0)

if args.op == "dns":
  print([i.public_dns_name for i in cluster.instances])

elif args.op == "status":
  print([i.state['Name'] for i in cluster.instances])

elif args.op == "cleanup":
  confirm("You are about to terminate and remove the whole cluster.")
  cluster.terminate()
  cluster.cleanup()
