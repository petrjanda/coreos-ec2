import requests

class CloudConfig:
  """ CoreOS cloud-config utils """

  def __init__(self, template):
    self.config = template

  def with_new_token(self, count):
    token = self.get_discovery_token(count)

    return self.config.replace('$coreos_discovery_token', token)

  def get_discovery_token(self, count):
    return requests.get('https://discovery.etcd.io/new?size=' + str(count)).text
