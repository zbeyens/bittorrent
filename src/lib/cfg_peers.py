import os
import configparser

root_path = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), '..', '..')
config_path = os.path.join(root_path, 'config')
peers_path = os.path.join(config_path, 'peers.ini')

# for Alice/Bob and Charlie 1


class CfgPeers:

    def read_config_peers(self, user):
        config = configparser.ConfigParser()
        config.read(peers_path)
        ip_address = config.get(user, 'ip_address')
        port_number = config.getint(user, 'port_number')
        return ip_address, port_number


if __name__ == '__main__':
    CfgPeers()
