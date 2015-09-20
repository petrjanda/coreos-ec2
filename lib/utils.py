import urllib.request

def confirm(message):
  choice = input(message + " Are you sure? y/n ").lower()
  if choice == 'y':
    return True
  else:
    sys.exit(0)


def download_file_as_string(url):
  with urllib.request.urlopen(url) as response:
    return response.read().decode('utf-8')
