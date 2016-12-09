from lib.peer import Peer


class Alice(Peer):

    def __init__(self):
        Peer.__init__(self, 'alice')


if __name__ == '__main__':
    Alice()
