import socket
import select
import sys

# EXAMPLE OF SERVER

# to test a client connect:
# telnet localhost 8001

# List to keep track of socket descriptors
SOCKETS = []
RECV_BUFFER = 4096  # Advisable to keep it as an exponent of 2
HOST = ''
PORT = 8001  # Arbitrary non-privileged port

socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_server.bind((HOST, PORT))
socket_server.listen(10)

# Add server socket to the list of readable connections
SOCKETS.append(socket_server)
print('Socket now listening')


while 1:
    # NOT USING ACCEPT BECAUSE IT'S A BLOCKING CALL:
    # conn, addr = s.accept()

    # Get the list sockets which are readable
    # select wait for I/O efficiently (non-blocking)
    read_sockets, write_sockets, error_sockets = select.select(
        SOCKETS, [], [])

    for sock in read_sockets:
        # New connection
        if sock == socket_server:
            # Handle the case in which there is a new connection recieved
            # through socket_server
            sockfd, addr = socket_server.accept()
            SOCKETS.append(sockfd)
            print('Client connected with ' + addr[0] + ':' + str(addr[1]))
        # Some incoming message from a client
        else:
            # Data recieved from client, process it
            data = sock.recv(RECV_BUFFER).decode()
            if data:
                print(data)
                sock.send('ACK'.encode())
            else:
                # if recv() returned NULL, that usually means the sender wants
                # to close the socket.
                print('Client disconnected with ' +
                      addr[0] + ':' + str(addr[1]))
                sock.close()
                SOCKETS.remove(sock)

s.close()
