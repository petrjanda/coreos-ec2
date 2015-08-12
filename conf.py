spark = ClusterConf(
    args.cluster_name, ami, args.key_pair_name,
    user_data = cloud_config,
    instances_count = int(args.instances_count),
    instance_type = args.instance_type,
    allocate_ip_address = False
) \
.volume(
    name = '/dev/sdb', 
    size = 100, 
    volume_type = 'gp2', 
    delete_on_termination = True
)
