import sys
from lib.client import *


class Charlie(Client1):

    def __init__(self):
        #Client1.__init__(self)
        # print(self.ip_address)
        # print(port_number)
        if len(sys.argv) < 2:
            print('Error: missing step number')
            sys.exit(1)

        step = int(sys.argv[1])

        if step == 1:
            """
            Step 1
            Creation of client Charlie (downloads chunks of a file from 2 peers: Alice and Bob).
            """
            Client1()

        elif step == 2:
            """
            Step 2
            """
            Client2()
        elif step == 3:
            """
            Step 3
            """
        else:
            print('Error: invalid step number')
            sys.exit(1)


if __name__ == '__main__':
    Charlie()
