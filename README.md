Aim of this project is to provide an easy to use way to start a CoreOS cluster on AWS EC2. Given the
appropriate cloud config and services to start, bootstrap scripts are supposed to do following fundamental
tasks:

1. Start cluster of `N` machines in specified EC2 region
2. Create, attach and mount EBS volume
3. Fetch and configure new unique ETCD discovery token
4. Deploy list of required services
5. Start required amount of services 
6. Provide additional tooling (inspect, start, stop, terminate, cleanup the cluster)

## Configuration

To start a CoreOS cluster, you have to choose appropriate Amazon EC2 Ami. This is done automatically by us depending
on your region and instance type according to (https://coreos.com/os/docs/latest/booting-on-ec2.html).

As any other CoreOS cluster, we're using `cloud-config` file to initiate each cluster node. As the `cloud-config`
is passed to each EC2 node as the `user-data` upon creation, we ensure that all initial cluster machines are
identical.

There are several important changes in our `config/cloud-config.example`:

### ETCD

ETCD needs a discovery token to be able to find other instances within the cluster. By default its on you to fetch
a new token when you're starting a cluster although we've included this step into the solution.

    etcd:
      discovery: $coreos_discovery_token
      addr: $private_ipv4:4001
      peer-addr: $private_ipv4:7001

The `$coreos_discovery_token` isn't part of CoreOS cloud-config by default, but if you run the cluster it will be
replaced by unique ETCD discovery token automatically. If this isn't what you want, feel free to use any arbitrary
value here, which means you don't have to use the automatically created one.

### Flannel

Flannel (https://coreos.com/flannel/docs/latest/flannel-config.html) is the virtual networking layer within the CoreOS cluster. It provides a mechanism, which will allow
docker to assign unique IP address to every running docker container. This not only greatly simpifies the operations
(avoid unnecessary port binding and exposing) but it also goes along more high level clustering management
solutions like Kubernetes. As flannel is very well integrated with the CoreOS, only necessary config change is to
start a unit which would specify Flannel's network address range:

    - name: flanneld.service
      command: start
      drop-ins:
        - name: 50-network-config.conf
          content: |
            [Service]
            ExecStartPre=/usr/bin/etcdctl set /coreos.com/network/config '{ "Network": "10.1.0.0/16" }'

### Mounted volume

By default, we've provided one mounted volume of EBS. Its created alongside the machine itself and by default is
specified to be attached as `/dev/sbd`. 

    BlockDeviceMappings=[
      {
        'DeviceName': '/dev/sdb',
        'Ebs': {
          'VolumeSize': 100,
          'VolumeType': 'gp2',
          'DeleteOnTermination': True
        }
      }
    ]

Ofc attaching volume itself wouldn't be enough so we go ahead and mount
it when cluster node is being started. This consists of 2 steps. First we
wipe the volume out and make sure it has file system (by default `ext4`). Once
that is done, we mount the volume to `/media/ebs` using the following CoreOS
units:

    - name: format-xvdb.service
      command: start
      content: |
        [Unit]
        Description=Formats the EBS drive
        After=dev-xvdb.device
        Requires=dev-xvdb.device

        [Service]
        Type=oneshot
        RemainAfterExit=yes
        ExecStart=/usr/sbin/wipefs -f /dev/xvdb
        ExecStart=/usr/sbin/mkfs.ext4 /dev/xvdb

    - name: media-ebs.mount
      command: start
      content: |
        [Unit]
        After=format-xvdb.service

        [Mount]
        What=/dev/xvdb
        Where=/media/ebs
        Type=ext4

Once your cluster is started, you can verify presence of your volume with `lsblk` command:

    core@ip-172-31-47-145 ~ $ lsblk
    NAME    MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
    xvda    202:0    0    8G  0 disk
    |-xvda1 202:1    0  128M  0 part
    |-xvda2 202:2    0    2M  0 part
    |-xvda3 202:3    0    1G  0 part /usr
    |-xvda4 202:4    0    1G  0 part
    |-xvda6 202:6    0  128M  0 part /usr/share/oem
    |-xvda7 202:7    0   64M  0 part
    `-xvda9 202:9    0  5.7G  0 part /
    xvdb    202:16   0  100G  0 disk /media/ebs

As you can see `/dev/xvdb` is mounted at `/media/ebs` correctly. See more at http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-using-volumes.html.

## Start a cluster

To start a cluster you will need a `conf` file which describes the cluster you would like to create. Here is the list of attributes you can specify:

  * `region` (required) - ID of one of the AWS regions (eu-east-1)
  * `cloud_config` (required) - path to the cloud config file which will be used to initialise CoreOS nodes
  * `key_pair` (required) - name of the EC2 key pair which you'll use to access your instances
  * `instances_count` (required) - number of instances to launch
  * `instance_type` (required) - type of the instance to be launched
  * `allocate_ip_address` (required) - yes/no value specifying if you want a static IP address allocated for each node
  * `volumes` (optional) - list of volumes you want attached to each node. Each needs to have a `name` (device name), `size` (in gigabytes), `volume_type` (gp2, standard, ...), and `delete_on_termination` (yes/no to specify if the volume should be destroyed when instance is terminated)
  * `security_groups` (optional) - TBA

Given our conf:

    region: us-east-1
    cloud_config: config/cloud-config.example
    key_pair: YOUR-KEY-PAIR 
    instances_count: 2
    instance_type: c4.large
    allocate_ip_address: yes

    volumes:
      - 
        name: /dev/sdb
        size: 100
        volume_type: gp2
        delete_on_termination: yes

    security_groups:
      - 
        name: spark
        action: find_or_create
        allow_inbound:
          - 
            protocol: tcp
            from_port: 8080
            to_port: 8080
            ip: 0.0.0.0/0
          - 
            protocol: tcp
            from_port: 4040
            to_port: 4040
            ip: 0.0.0.0/0
      - 
        name: p-1
        action: create
        allow_all_own_traffic: true
        allow_ssh_from: 0.0.0.0/0

Cluster of 2 nodes will be started with EBS volume attached and mounted. All nodes will be connected to single cluster with unique discovery token.
Additionally there will be new security group `p-1` created which will allow all traffic within the cluster and ports 8080, 4040 as well as `spark` security group which allows traffic from outside the cluster from any IP (be sure you're ok to publish
ports like that). 

    ➜  coreos-ec2 git:(master) ✗ python3 op.py p-1 launch config/cluster-conf.yml.example
    INFO: --> Fetching CoreOS etcd discovery token
    INFO: Starting new HTTPS connection (1): discovery.etcd.io
    INFO: Starting new HTTPS connection (1): ec2.us-east-1.amazonaws.com
    INFO: Calling ec2:create_security_group with {'Description': 'p-1 security', 'GroupName': 'p-1'}
    INFO: Starting new HTTPS connection (1): ec2.us-east-1.amazonaws.com
    INFO: Calling ec2:authorize_security_group_ingress with {'GroupId': 'sg-d42cb2b3', 'SourceSecurityGroupName': 'p-1'}
    INFO: Calling ec2:authorize_security_group_ingress with {'FromPort': 22, 'IpProtocol': 'tcp', 'GroupId': 'sg-d42cb2b3', 'ToPort': 22, 'CidrIp': '0.0.0.0/0'}
    INFO: --> Creating instances
    INFO: Calling ec2:run_instances with {'MinCount': 1, 'UserData': '#cloud-config\n\ncoreos:\n  etcd:\n    discovery: https://discovery.etcd.io/86952ca2bf0d49d7ecaff9a5783070d4\n    addr: $private_ipv4:4001\n    peer-addr: $private_ipv4:7001\n  etcd2:\n    discovery: https://discovery.etcd.io/86952ca2bf0d49d7ecaff9a5783070d4\n    advertise-client-urls: http://$private_ipv4:2379,http://$private_ipv4:4001\n    initial-advertise-peer-urls: http://$private_ipv4:2380\n    listen-client-urls: http://0.0.0.0:2379,http://0.0.0.0:4001\n    listen-peer-urls: http://$private_ipv4:2380,http://$private_ipv4:7001\n  units:\n    - name: etcd.service\n      command: start\n\n    - name: fleet.service\n      command: start\n\n    - name: format-xvdb.service\n      command: start\n      content: |\n        [Unit]\n        Description=Formats the EBS drive\n        After=dev-xvdb.device\n        Requires=dev-xvdb.device\n\n        [Service]\n        Type=oneshot\n        RemainAfterExit=yes\n        ExecStart=/usr/sbin/wipefs -f /dev/xvdb\n        ExecStart=/usr/sbin/mkfs.ext4 /dev/xvdb\n\n    - name: media-ebs.mount\n      command: start\n      content: |\n        [Unit]\n        After=format-xvdb.service\n\n        [Mount]\n        What=/dev/xvdb\n        Where=/media/ebs\n        Type=ext4\n\n    - name: flanneld.service\n      command: start\n      drop-ins:\n        - name: 50-network-config.conf\n          content: |\n            [Service]\n            ExecStartPre=/usr/bin/etcdctl set /coreos.com/network/config \'{ "Network": "10.1.0.0/16" }\'\n', 'Monitoring': {'Enabled': True}, 'InstanceType': 'c4.large', 'BlockDeviceMappings': [{'Ebs': {'VolumeSize': 100, 'DeleteOnTermination': False, 'VolumeType': 'gp2'}, 'DeviceName': '/dev/sdb'}], 'ImageId': 'ami-3d73d356', 'KeyName': 'gwi-us-east', 'SecurityGroupIds': ['sg-b350c0d4', 'sg-d42cb2b3'], 'MaxCount': 2}
    INFO: Starting new HTTPS connection (1): ec2.us-east-1.amazonaws.com
    INFO: --> Tagging instances with cluster name 'p-1'
    INFO: Calling ec2:create_tags with {'Resources': ['i-962e9e3d'], 'Tags': [{'Key': 'Name', 'Value': 'p-1-1'}, {'Key': 'Cluster', 'Value': 'p-1'}]}
    INFO: Calling ec2:create_tags with {'Resources': ['i-232e9e88'], 'Tags': [{'Key': 'Name', 'Value': 'p-1-2'}, {'Key': 'Cluster', 'Value': 'p-1'}]}
    INFO: --> Waiting for instances to be in 'running' state
    INFO: Calling ec2:wait_until_running with {'InstanceIds': ['i-962e9e3d']}
    INFO: Calling ec2:wait_until_running with {'InstanceIds': ['i-232e9e88']}
    ➜  coreos-ec2 git:(master) ✗

    # Get DNS
    (venv)➜  python-ec2 git:(master) ✗ python3 op.py p-1 dns
    ['ec2-54-86-26-171.compute-1.amazonaws.com', 'ec2-52-4-163-190.compute-1.amazonaws.com']

    # Get status
    (venv)➜  python-ec2 git:(master) ✗ python3 op.py p-1 status
    ['running', 'running']

    # Cleanup
    (venv)➜  python-ec2 git:(master) ✗ python3 op.py p-1 cleanup
    You are about to terminate and remove the whole cluster Are you sure? y/n y
    --> Stop instances
    --> Delete security group 'p-1'

## Cluster ops 

    python3 op.py <cluster-name> cleanup
    python3 op.py <cluster-name> status
    python3 op.py <cluster-name> dns
