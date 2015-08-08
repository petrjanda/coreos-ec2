import boto3 as aws
import os, sys
import argparse
import env

from cluster import Cluster
from cluster_launcher import ClusterLauncher


env.check()

parser = argparse.ArgumentParser()
parser.add_argument("cluster_name")
parser.add_argument("op")
args = parser.parse_args()

cluster = Cluster(aws.resource('ec2'), args.cluster_name)

if args.op == "dns":
  print([i.public_dns_name for i in cluster.instances])
elif args.op == "status":
  print([i.state['Name'] for i in cluster.instances])
elif args.op == "terminate":
  cluster.terminate()
