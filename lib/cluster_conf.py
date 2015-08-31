""" ClusterConf """

#TODO reduce properties
class ClusterConf:
    """ ClusterConf """

    #TODO reduce attributes
    def __init__(self, cluster_name, ami, key_pair_name,
                 user_data='', instance_type='m1.small',
                 instances_count=1, allocate_ip_address=False):
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
        """ Ami """

        return self._ami

    @property
    def security_groups(self):
        """ List of security groups """

        return self._security_groups

    @property
    def key_pair_name(self):
        """ Key pair name used to access the cluster """

        return self._key_pair_name

    @property
    def cluster_name(self):
        """ Name """

        return self._cluster_name

    @property
    def instance_type(self):
        """ EC2 Instance Type """

        return self._instance_type

    @property
    def instances_count(self):
        """ Instances count """

        return self._instances_count

    @property
    def allocate_ip_address(self):
        """ Allocate elastic IP address for the cluster nodes? """

        return self._allocate_ip_address

    @property
    def block_device_mappings(self):
        """ Block device mapping for EC2 instance creation """

        return self._volumes

    @property
    def props(self):
        """ Props for EC2 cluster creation """

        return dict(
            ImageId=self._ami,
            UserData=self._user_data,
            MinCount=1,
            MaxCount=self.instances_count,
            KeyName=self.key_pair_name,
            InstanceType=self.instance_type,
            Monitoring=dict(
                Enabled=True
            ),

            BlockDeviceMappings=self.block_device_mappings
        )

    def volume(self, **kwargs):
        """ Add volume """

        self._volumes.append(kwargs)

        return self

    def security_group(self, **kwargs):
        """ Add security group """

        self._security_groups.append(kwargs)

        return self
