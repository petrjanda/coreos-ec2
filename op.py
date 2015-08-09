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

elif args.op == 'scp':
    import paramiko, base64
    from paramiko import SSHClient
    from scp import SCPClient

    dns_name = list(cluster.instances)[0].public_dns_name
    key = paramiko.RSAKey.from_private_key_file(
        '/Users/petr/Downloads/gwi-us-east.pem'
    )

    ssh = SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname = dns_name, username = 'core', pkey = key)

    scp = SCPClient(ssh.get_transport())
    scp.put('op.py', 'op.py')
    scp.close()

elif args.op == "cleanup":
    utils.confirm("You are about to terminate and remove the whole cluster.")
    cluster.terminate()
    cluster.cleanup()
