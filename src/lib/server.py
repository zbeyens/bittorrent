import socket
import sys
import threading

# EXAMPLE OF MULTITHREADED SERVER

# to test a client connect:
# telnet localhost 8001

RECV_BUFFER = 1024  # Advisable to keep it as an exponent of 2
HOST = ''
PORT = 8001


class Server:

    def __init__(self):

        self.host = HOST
        self.port = PORT
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Include IP headers
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.listen()

    def listen(self):
        print('Listening on port', PORT)
        self.sock.listen(10)
        while True:
            client, address = self.sock.accept()
            print('Client connected with ' +
                  address[0] + ':' + str(address[1]))
            # timeout after 60 seconds of inactivity
            client.settimeout(60)
            threading.Thread(target=self.listenToClient,
                             args=(client, address)).start()

    def listenToClient(self, client, address):
        while True:
            data = client.recv(RECV_BUFFER).decode()
            if data:
                print(data, 'received by Client',
                      address[0] + ':' + str(address[1]))
                # Set the response to echo back the recieved data
                response = data
                client.send(response.encode())
            else:
                # if recv() returned NULL, that usually means the sender wants
                # to close the socket.
                print('Client disconnected with ' +
                      address[0] + ':' + str(address[1]))
                client.close()
                return False

if __name__ == '__main__':
    Server()
