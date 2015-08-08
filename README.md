## Start a Cluster

    python3 launch.py <cluster-name> <security-group-id> <key-pair-name> <instance-count> <cloud-config-path> 

## Stop a Cluster

    python3 op.py <cluster-name> terminate 

## Check cluster status

    python3 op.py <cluster-name> status

## Get cluster public DNS

    python3 op.py <cluster-name> dns
