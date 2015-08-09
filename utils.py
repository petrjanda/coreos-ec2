def confirm(message):
  choice = input(message + " Are you sure? y/n ").lower()
  if choice == 'y':
    return True
  else:
    sys.exit(0)
