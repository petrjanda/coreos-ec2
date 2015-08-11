class ClusterConf:
    def __init__(self, cluster_name, ami, key_pair_name, user_data = '', instance_type = 'm1.small', instances_count = 1):
        self._cluster_name = cluster_name
        self._ami = ami
        self._user_data = user_data
        self._key_pair_name = key_pair_name
        self._instance_type = instance_type 
        self._instances_count = instances_count
        self._volumes = []

    @property
    def ami(self):
        return self._ami

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
    def block_device_mappings(self):
        return [{
            'DeviceName': v['name'],
            'Ebs': {
                'VolumeSize': v['size'],
                'VolumeType': v['volume_type'],
                'DeleteOnTermination': v['delete_on_termination']
            }
        } for v in self._volumes]

    @property
    def props(self):
        return {
            'ImageId': self._ami, 
            'UserData': self._user_data,
            'MinCount':1, 
            'MaxCount':self.instances_count,
            'KeyName':self.key_pair_name,
            'InstanceType':self.instance_type,
            'Monitoring':{
                'Enabled': True
            },

            'BlockDeviceMappings':self.block_device_mappings
        }



    #def volume(name = '/dev/sdb', size = 100, volume_type = 'gp2', delete_on_termination = True):
    def volume(self, **kwargs):
        self._volumes.append(kwargs)

        return self
