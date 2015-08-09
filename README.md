## Start a Cluster

    python3 launch.py <cluster-name> <security-group-id> <key-pair-name> <instance-count> <cloud-config-path> 

    ➜  python-ec2 git:(master) ✗ python3 launch.py s-1 sg-xxxxxxx xxx 2 ./config/cloud-config.example
    --> Fetching CoreOS etcd discovery token
    --> Creating 2 instances
    --> Tagging instances with cluster name 's-1'
    --> Waiting for instances to be in 'running' state
    ['ec2-xx-x-xxx-xxx.compute-1.amazonaws.com', 'ec2-xx-x-xxx-xxx.compute-1.amazonaws.com'] 

## Stop a Cluster

    python3 op.py <cluster-name> terminate 

## Check cluster status

    python3 op.py <cluster-name> status

## Get cluster public DNS

    python3 op.py <cluster-name> dns

## Mount the attached volume

Your attached volume is automatically mounted in `/media/ebs` (as specified in `cloud-config`).

Manually:

    lsblk
    sudo mkfs -t ext4 /dev/xvdh 
    sudo mkdir /media/ebs1
    sudo mount /dev/xvdh /media/ebs1/


Fstab:

    vim /etc/fstab
    # /dev/xvdh      /media/ebs1/  ext4    defaults,nofail        0       2
    sudo mount -a
