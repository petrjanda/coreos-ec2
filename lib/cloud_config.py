""" CoreOS Cloud Config """

import requests

def with_new_token(template, count):
    """ Return CloudConfig with new discovery token from ETCD discovery server """
    token = get_discovery_token(count)

    return template.replace('$coreos_discovery_token', token)

def get_discovery_token(count):
    """ Request new ETCD discovery token """
    return requests.get('https://discovery.etcd.io/new?size=' + str(count)).text
