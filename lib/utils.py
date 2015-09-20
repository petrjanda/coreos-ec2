import json, urllib.request

def confirm(message):
  choice = input(message + " Are you sure? y/n ").lower()
  if choice == 'y':
    return True
  else:
    sys.exit(0)


def download_file(url, file_path):
  with urllib.request.urlopen(url) as response, open(file_path, 'wb') as out_file:
    data = response.read()
    out_file.write(data)


def file_to_json(file_path):
    with open(file_path) as json_file:
        return json.load(json_file)
