def create_security_group(**kwargs):
    """ Create new EC2 security group given the description """

    group = self.ec2.create_security_group(
        GroupName = kwargs['name'],
        Description = kwargs['name'] + ' security'
    )

    if(kwargs['allow_all_own_traffic'] is True):
        group.authorize_ingress(
            SourceSecurityGroupName = cluster_name
        )

    for inbound in kwargs['allow_inbound']:
        group.authorize_ingress(
            IpProtocol = inbound['protocol'],
            FromPort = inbound['from_port'],
            ToPort = inbound['to_port'],
            CidrIp = inbound['ip']
        )

    return group

def find_security_group(name):
    """ Find existing EC2 security group """

    return self.ec2.security_group(
        Name = kwargs['name']
    )

