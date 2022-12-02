import threading
import socket
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
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

        # starting service
        self.run_service()

    def __broadcast(self, msg: bytes) -> None:
        pass
        for client in self.clients.keys():
            client.send(msg)

    def __handle(self, client: socket.socket) -> None:
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

    def run_service(self) -> None:
        print('server is running on {}:{}!'.format(self.host, self.port))
        while True:
            client, address = self.server.accept()
            # storing this client and its IP address into dictionary 'clients'
            self.clients[client] = address
            print('{0} has connected.'.format(str(address)))

            # receiving RSC pubkey and sending back AES key
            pubKeyPM = bytes(client.recv(1024))
            encrypted_AESkey = self.encrypt_AESkey(pubKeyPM)
            client.send(bytes(encrypted_AESkey))

            # starting thread for broadcasting msg
            self.work_thread = threading.Thread(target=self.__handle, args=(client,))
            self.work_thread.start()

    def encrypt_AESkey(self, pubKeyPEM: bytes) -> bytes:
        pubKey = RSA.import_key(pubKeyPEM)
        encryptor = PKCS1_OAEP.new(pubKey)
        return encryptor.encrypt(self.AESkey)


def main():
    # host = '192.168.31.66'
    host = '127.0.0.1'
    port = 8000
    server = Server(host, port)


if __name__ == '__main__':
    main()
