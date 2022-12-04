import sys
import threading
import socket
import json

from Crypto.Random import get_random_bytes
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog

from lib.server import Ui_server
from lib.cipher import encrypt_AESkey


class ServerGUI(QDialog, Ui_server):
    host: str
    pNumber: int
    server = None
    AESkey: bytes
    work_thread = None
    condition = None

    def __init__(self):
        # initializing GUI
        super().__init__()
        self.child = None
        self.setupUi(self)
        with open('./lib/ipconfig.json', 'r') as fp:
            ipconfig: dict = json.load(fp)
            self.IPAddress.setText(ipconfig['IP'])
            self.port.setText(str(ipconfig['port']))

        # binding buttons
        self.start.clicked.connect(self.start_server)
        self.terminate.clicked.connect(self.terminate_server)

    def start_server(self):
        """setting IP address and port to start the server"""
        self.host = self.IPAddress.text()
        self.pNumber = int(self.port.text())
        with open('./lib/ipconfig.json', 'w') as fp:
            ipconfig = {'IP': self.host, 'port': self.pNumber}
            json.dump(ipconfig, fp)
        self.child = Server(self.host, self.pNumber)
        self.child.run_service()
        # # initializing socket

        # try:
        #     self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #     self.server.bind((self.host, self.pNumber))
        #     self.server.listen()
        # except:
        #     self.hint.setText('ERROR: Can not start server. Check the availability of IP address and port.')
        #
        # # generating AESkey
        # self.AESkey = get_random_bytes(16)
        # self.hint.setText('AESkey generated: {}'.format(self.AESkey))
        #
        # # starting service
        # hint = self.hint.toPlainText()
        # self.hint.setText(hint + '\nserver is running on {}:{}!'.format(self.host, self.pNumber))

        # self.condition = True
    #     while self.condition:
    #         client, address = self.server.accept()
    #         # storing this client and its IP address into dictionary 'clients'
    #         self.clients[client] = address
    #         hint = self.hint.toPlainText()
    #         self.hint.setText(hint + '{0} has connected.'.format(str(address)))
    #
    #         # receiving RSC pubkey and sending back AES key
    #         pubKeyPEM = bytes(client.recv(1024))
    #         encrypted_AESkey = encrypt_AESkey(self.AESkey, pubKeyPEM)
    #         client.send(bytes(encrypted_AESkey))
    #
    #         # starting thread for broadcasting msg
    #         self.work_thread = threading.Thread(target=self.__handle, args=(client,))
    #         self.work_thread.start()
    #
    # def __broadcast(self, msg: bytes) -> None:
    #     pass
    #     for client in self.clients.keys():
    #         client.send(msg)
    #
    # def __handle(self, client: socket.socket) -> None:
    #     while True:
    #         try:
    #             msg: bytes = client.recv(1024)
    #             self.__broadcast(msg)
    #         except:
    #             # removing client from client-nickname dictionary
    #             hint = self.hint.toPlaintext()
    #             self.hint.setText(hint + '{} has disconnected.'.format(self.clients[client]))
    #             del self.clients[client]
    #             client.close()
    #             return

    def terminate_server(self):
        """terminating the server"""
        self.close()


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
            encrypted_AESkey = encrypt_AESkey(pubKeyPM)
            client.send(bytes(encrypted_AESkey))

            # starting thread for broadcasting msg
            self.work_thread = threading.Thread(target=self.__handle, args=(client,))
            self.work_thread.start()


# class WorkThread(QThread):
#     # trigger = pyqtSignal(str)
#
#     def __init__(self, server):
#         super(WorkThread, self).__init__()
#         self.server = server
#         self.clients = {}
#
#     def run(self):
#         while True:
#             client, address = self.server.accept()
#             # storing this client and its IP address into dictionary 'clients'
#             self.clients[client] = address
#             hint = self.hint.toPlainText()
#             self.hint.setText(hint + '{0} has connected.'.format(str(address)))
#
#             # receiving RSC pubkey and sending back AES key
#             pubKeyPEM = bytes(client.recv(1024))
#             encrypted_AESkey = encrypt_AESkey(self.AESkey, pubKeyPEM)
#             client.send(bytes(encrypted_AESkey))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    server = ServerGUI()
    server.show()
    sys.exit(app.exec())
