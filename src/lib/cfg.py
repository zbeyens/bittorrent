import os

root_path = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), '..', '..')
config_path = os.path.join(root_path, 'config')
peers_path = os.path.join(config_path, 'peers.ini')
