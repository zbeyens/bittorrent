from lib.peer import Peer


class Alice(Peer):

    def __init__(self):
        self.user = 'alice'
        Peer.__init__(self)


if __name__ == '__main__':
    Alice()
