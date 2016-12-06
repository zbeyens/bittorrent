from lib.server import Server


class Alice:

    def __init__(self):
        Server('alice')


if __name__ == '__main__':
    Alice()
