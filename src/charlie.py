import sys
from lib.client import *

if len(sys.argv) < 2:
    print('Error: missing step number')
    sys.exit(1)
step = int(sys.argv[1])

if step == 1:
    """
    Step 1
    Creation of client Charlie (downloads chunks of a file from 2 peers: Alice and Bob).
    """

    Charlie()


elif step == 2:
    """
    Step 2
    """
    ClientV2('tracker')
elif step == 3:
    """
    Step 3
    """
else:
    print('Error: invalid step number')
    sys.exit(1)


class Charlie(ClientV1):

    def __init__(self):
        ClientV1.__init__(self, 'charlie')
        print(self.ip_address)
        print(port_number)
