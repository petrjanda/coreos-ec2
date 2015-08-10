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

As any other CoreOS cluster, we're using `cloud-config` file to initiate each cluster node. As the `cloud-config`
is passed to each EC2 node as the `user-data` upon creation, we ensure that all initial cluster machines are
identical.

There are several important changes in our `config/cloud-config.example`:

1. Flannel

Flannel is the virtual networking layer within the CoreOS cluster. It provides a mechanism, which will allow
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

2. Mounted volume

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

You can verify it if you SSH to your instance and run the `lsblk` command:

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

As you can see `/dev/xvdb` is mounted at `/media/ebs` correctly.

## Start a cluster

Cluster of `N` nodes will be started with EBS volume attached and mounted. All nodes will be connected to
single cluster with unique discovery token and EC2 security group.

Replace `xxx` by appropriate key-pair name:

    (venv)➜  python-ec2 git:(master) ✗ python3 launch.py p-1 c4.large 2 <xxx> ./config/cloud-config.example
    INFO: --> Fetching CoreOS etcd discovery token
    INFO: --> Creating 2 instances of ami-3d73d356
    INFO: --> Tagging instances with cluster name 'p-1'
    INFO: --> Waiting for instances to be in 'running' state
    INFO: --> ['ec2-54-86-26-171.compute-1.amazonaws.com', 'ec2-52-4-163-190.compute-1.amazonaws.com']

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
