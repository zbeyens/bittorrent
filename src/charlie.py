import sys
from lib.client import *

if len(sys.argv) < 2:
    print('Error: missing step number')
    sys.exit(1)
step = int(sys.argv[1])


if step == 1:
    """
    Step 1
    Creation of the client Charlie that will download chunks of a file from 2 peers: Alice and Bob.
    """


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
