from lib.peer import Peer


class Bob(Peer):

    def __init__(self):
        self.user = 'bob'
        Peer.__init__(self)


if __name__ == '__main__':
    Bob()
