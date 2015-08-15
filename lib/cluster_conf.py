class ClusterConf:
    def __init__(self, cluster_name, ami, key_pair_name, user_data = '', instance_type = 'm1.small', instances_count = 1, allocate_ip_address = False):
        self._cluster_name = cluster_name
        self._ami = ami
        self._user_data = user_data
        self._key_pair_name = key_pair_name
        self._instance_type = instance_type 
        self._instances_count = instances_count
        self._allocate_ip_address = allocate_ip_address
        self._volumes = []
        self._security_groups = []

    @property
    def ami(self):
        return self._ami

    @property
    def security_groups(self):
        return self._security_groups

    @property
    def key_pair_name(self):
        return self._key_pair_name

    @property
    def cluster_name(self):
        return self._cluster_name

    @property
    def instance_type(self):
        return self._instance_type

    @property
    def instances_count(self):
        return self._instances_count

    @property
    def allocate_ip_address(self):
        return self._allocate_ip_address

    @property
    def block_device_mappings(self):
        return [dict(
            DeviceName = v['name'],
            Ebs = dict(
                VolumeSize = v['size'],
                VolumeType = v['volume_type'],
                DeleteOnTermination = v['delete_on_termination']
            )
        ) for v in self._volumes]

    @property
    def props(self):
        return dict(
            ImageId = self._ami, 
            UserData = self._user_data,
            MinCount = 1, 
            MaxCount = self.instances_count,
            KeyName = self.key_pair_name,
            InstanceType = self.instance_type,
            Monitoring = dict(
                Enabled = True
            ),

            BlockDeviceMappings = self.block_device_mappings
        )

    #def volume(name = '/dev/sdb', size = 100, volume_type = 'gp2', delete_on_termination = True):
    def volume(self, **kwargs):
        # name, size, volume_type required
        self._volumes.append(kwargs)

        return self

    def security_group(self, **kwargs):
        self._security_groups.append(kwargs)

        return self
