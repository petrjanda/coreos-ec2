import os, sys, argparse, botocore, utils, logging
import lib.env as env
import paramiko, base64

from paramiko import SSHClient
from scp import SCPClient
 
from lib.cluster import Cluster
from lib.cluster_launcher import ClusterLauncher
from lib.coreos import get_cluster_conf
from lib.cluster_conf import ClusterConf

env.check()

parser = argparse.ArgumentParser()
parser.add_argument("cluster_name")
subparsers = parser.add_subparsers(dest='op')

parser_scp =  subparsers.add_parser('scp')
parser_scp.add_argument('key_pair_path')
parser_scp.add_argument('from_path')
parser_scp.add_argument('to_path')

parser_launch = subparsers.add_parser('launch')
parser_launch.add_argument("instance_type")
parser_launch.add_argument("instances_count")
parser_launch.add_argument("key_pair_name")
parser_launch.add_argument("cloud_config_path")

parser_start = subparsers.add_parser('start')
parser_stop = subparsers.add_parser('stop')
parser_cleanup = subparsers.add_parser('cleanup')
parser_status = subparsers.add_parser('status')
parser_dns = subparsers.add_parser('dns')
parser_ip = subparsers.add_parser('ip')

args = parser.parse_args()
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

region = os.getenv("AWS_DEFAULT_REGION")
cluster = Cluster(args.cluster_name)

if args.op == 'launch':
    try:
        conf = get_cluster_conf(
            args.cluster_name, 
            region, 
            args.cloud_config_path, 
            args.key_pair_name,
            instances_count = int(args.instances_count),
            instance_type = args.instance_type,
            allocate_ip_address = False
        ) \
        .volume(
            name = '/dev/sdb', 
            size = 100, 
            volume_type = 'gp2', 
            delete_on_termination = True
        ) \
        .find_or_create_security_group(
            name = 'spark',
            allow_inbound = [
                dict(protocol = 'tcp', from_port = 8080, to_port = 8080, ip = '0.0.0.0/0'),
                dict(protocol = 'tcp', from_port = 4040, to_port = 4040, ip = '0.0.0.0/0')
            ]
        ) \
        .create_security_group(
            name = args.cluster_name,
            allow_ssh_from = '0.0.0.0/0',
            allow_all_own_traffic = True
        )

        ClusterLauncher().launch(conf)
        instances = Cluster(args.cluster_name).instances

        logging.info("--> " + str([i.public_dns_name for i in instances]))
    except botocore.exceptions.WaiterError:
        logging.error("--x Failed to launch instances, Please check your AWS console, some machines may be already running!") 
        cluster.terminate()
        cluster.cleanup()

elif args.op == "status":
    print(cluster.status)

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

elif args.op == "cleanup":
    utils.confirm("You are about to terminate and remove the whole cluster.")
    cluster.terminate()
    cluster.cleanup()
