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

## Attached volume

Your attached volume is automatically mounted in `/media/ebs` using `ext4` file system (as specified in `cloud-config`).
