import os
import configparser

root_path = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), '..', '..')
config_path = os.path.join(root_path, 'config')
peers_path = os.path.join(config_path, 'peers.ini')


class CfgPeers:
    # for Alice/Bob and Charlie 1

    def read_config_peers(self, user):
        config = configparser.ConfigParser()
        config.read(peers_path)
        ip_address = config.get(user, 'ip_address')
        port_number = config.getint(user, 'port_number')
        return ip_address, port_number

    # for Tracker 2
    def read_config_peers_all(self):
        config_p = configparser.ConfigParser()
        config_p.read(peers_path)
        peers_info = {}
        for peer in config_p.sections():
            p = config_p.getint(peer, 'port_number')
            i = config_p.get(peer, 'ip_address')
            peers_info[peer] = (i, p)
        return peers_info
