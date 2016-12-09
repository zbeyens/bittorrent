from lib.peer import Peer


class Bob(Peer):

    def __init__(self):
        Peer.__init__(self, 'bob')


if __name__ == '__main__':
    Bob()
