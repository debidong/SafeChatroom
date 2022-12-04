import json
import threading
import socket
from lib.cipher import encrypt_AESkey
from Crypto.Random import get_random_bytes


class Server:
    def __init__(self, host: str, port: int):
        # initializing dictionary for client - IP address
        self.clients = {}
        self.work_thread = None

        # initializing socket
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen()

        # generating AESkey
        self.AESkey = get_random_bytes(16)
        print('AESkey: {}'.format(self.AESkey))

    def __handle(self, client: socket.socket) -> None:
        """implementation of child thread for each client"""
        while True:
            try:
                msg: bytes = client.recv(1024)
                self.__broadcast(msg)
            except:
                # removing client from client-nickname dictionary
                print('{} has disconnected.'.format(self.clients[client]))
                del self.clients[client]
                client.close()
                return

    def __broadcast(self, msg: bytes) -> None:
        """implementation of broadcasting msg"""
        # no records for msg from clients, ensuring end-to-end communication
        for client in self.clients.keys():
            client.send(msg)

    def run_service(self) -> None:
        """implementation of creating child thread for each client and running broadcast service for them"""
        print('server is running on {}:{}!'.format(self.host, self.port))
        while True:
            client, address = self.server.accept()
            # storing this client and its IP address into dictionary 'clients'
            self.clients[client] = address
            print('{0} has connected.'.format(str(address)))

            # receiving RSC pubkey and sending back AES key
            pubKeyPEM = bytes(client.recv(1024))
            encrypted_AESkey = encrypt_AESkey(self.AESkey, pubKeyPEM)
            client.send(bytes(encrypted_AESkey))

            # starting thread for broadcasting msg
            self.work_thread = threading.Thread(target=self.__handle, args=(client,))
            self.work_thread.start()


def main():
    with open('./lib/ipconfig.json', 'r') as fp:
        ipconfig: dict = json.load(fp)
    server = Server(ipconfig['IP'], ipconfig['port'])
    server.run_service()


if __name__ == '__main__':
    main()
