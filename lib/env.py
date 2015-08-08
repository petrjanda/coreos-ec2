import os, sys, argparse

def check():
  # Check necessary configuration
  if os.getenv('AWS_ACCESS_KEY_ID') is None:
    print("ERROR: The environment variable AWS_ACCESS_KEY_ID must be set", file=sys.stderr)
    sys.exit(1)

  if os.getenv('AWS_SECRET_ACCESS_KEY') is None:
    print("ERROR: The environment variable AWS_SECRET_ACCESS_KEY must be set", file=sys.stderr)
    sys.exit(1)

  if os.getenv('AWS_DEFAULT_REGION') is None:
    print("ERROR: The environment variable AWS_DEFAULT_REGION must be set", file=sys.stderr)
    sys.exit(1)
