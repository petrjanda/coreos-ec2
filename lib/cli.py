import os, sys, argparse, botocore, logging
import lib.utils as utils
import lib.env as env
import paramiko, base64
import boto3 as aws

from paramiko import SSHClient
from scp import SCPClient
 
from lib.cluster import Cluster
from lib.cluster_launcher import ClusterLauncher
from lib.coreos import get_cluster_conf, read_conf
from lib.cluster_conf import ClusterConf

def main():
    env.check()

    parser = argparse.ArgumentParser()
    parser.add_argument("cluster_name")
    subparsers = parser.add_subparsers(dest='op')

    parser_scp =  subparsers.add_parser('scp')
    parser_scp.add_argument('key_pair_path')
    parser_scp.add_argument('from_path')
    parser_scp.add_argument('to_path')

    parser_launch = subparsers.add_parser('launch')
    parser_launch.add_argument('cluster_conf_path')

    parser_start = subparsers.add_parser('start')
    parser_stop = subparsers.add_parser('stop')
    parser_cleanup = subparsers.add_parser('cleanup')
    parser_status = subparsers.add_parser('status')
    parser_dns = subparsers.add_parser('dns')
    parser_ip = subparsers.add_parser('ip')
    subparsers.add_parser('test')
    subparsers.add_parser('terminate')

    args = parser.parse_args()
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

    region = os.getenv("AWS_DEFAULT_REGION")
    cluster = Cluster(args.cluster_name)

    if args.op == 'launch':
        try:
            conf = read_conf(args.cluster_name, args.cluster_conf_path)
            ClusterLauncher().launch(conf)
        except botocore.exceptions.WaiterError:
            logging.error("--x Failed to launch instances, Please check your AWS console, some machines may be already running!") 
            cluster.terminate()
            cluster.cleanup()

    elif args.op == "status":
        print(cluster.status)

    elif args.op == "test":
        groups = list(cluster.instances)[0].security_groups

        for g in groups:
            try:
                aws.resource('ec2').SecurityGroup(g['GroupId']).delete()
            except botocore.exceptions.ClientError as e:
                print(g['GroupName'])

    elif args.op == "dns":
        print([i.public_dns_name for i in cluster.instances])

    elif args.op == "ip":
        print([i.public_ip_address for i in cluster.instances])

    elif args.op == "stop":
        cluster.stop()

    elif args.op == "start":
        cluster.start()

    elif args.op == 'scp':
        dns_name = list(cluster.instances)[0].public_dns_name
        key = paramiko.RSAKey.from_private_key_file(args.key_pair_path)

        ssh = SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname = dns_name, username = 'core', pkey = key)

        scp = SCPClient(ssh.get_transport())
        scp.put(args.from_path, args.to_path)
        scp.close()

    elif args.op == "terminate":
        utils.confirm("You are about to terminate the whole cluster.")
        cluster.terminate()

    elif args.op == "cleanup":
        utils.confirm("You are about to terminate and remove the whole cluster.")
        cluster.cleanup()
