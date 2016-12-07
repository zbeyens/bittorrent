import os
import configparser
import binascii
root_path = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), '..', '..')
config_path = os.path.join(root_path, 'config')
chunks_path = os.path.join(config_path, 'file.ini')

# fot tracker (part2)


class CfgChunks:

    def read_config_chunks(self):
        chunks = {}
        chunks_peers = {}
        config = configparser.ConfigParser()
        config.read(chunks_path)
        filename = config.get('description', 'filename')
        chunks_count = config.getint('Description','chunks_count')
        for (id_chunk, chunk_hash) in config.items('chunks'):
            id_chunk = int(id_chunk)
            chunks[id_chunk] = binascii.a2b_hex(chunk_hash)
        for (id_chunk_peer, peers) in config.items('chunks_peer'):
            id_chunk_peer = int(id_chunk_peer)
            list_peers = peers.split(',')
            chunks_peers[id_chunk_peer] = list_peers
        return (chunks,chunks_peers,chunks_count,filename)

if __name__ == '__main__':
    CfgChunks()