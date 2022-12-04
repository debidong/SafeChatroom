import json
import socket
import sys
import time

from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QDialog

from lib.chatroom import Ui_SafeChatroom
from lib.cipher import AESCipher, RSCCipher


class ClientWindow(QDialog, Ui_SafeChatroom):
    # msg_recv is an archive which stores messages that client used to receive
    msg_recv: str = ''
    # nickname identifies messages sent from this client
    nickname = 'unknown'
    # host and port are used to create socket for connection with chat server
    host: str
    port: int

    def __init__(self):
        """initializing GUI, socket, key pairs and working threads for the client"""
        super().__init__()
        self.setupUi(self)

        # initializing socket
        with open('./lib/ipconfig.json', 'r') as fp:
            ipconfig: dict = json.load(fp)
            self.host = ipconfig['IP']
            self.port = int(ipconfig['port'])
        print('Trying to connect server at {}:{}.'.format(self.host, self.port))
        try:
            self.connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connect.connect((self.host, self.port))
        except:
            print('ERROR: The server according to IP address and port number is not running!')
            print('Check the setting or rerun the server.')
            sys.exit(-1)

        # generating RSC keypair
        print('Server found. Generating RSC keypair and exchanging keys...')
        rsc = RSCCipher()
        try:
            # sending RSC pubkey to server
            self.connect.send(rsc.pubKeyPEM)
            # receiving and decrypt AESkey
            encrypted_AESkey = bytes(self.connect.recv(1024))
            self.AESkey = rsc.decrypt(encrypted_AESkey)
            print('AESkey received: {}.'.format(self.AESkey))
        except:
            print('Server is dead. Try to rerun the server.')
            sys.exit(-1)

        # initializing thread
        print('Starting threads...')
        self.recv_thread = RecvThread(self.connect, self.AESkey)
        self.recv_thread.trigger.connect(self.print_msg)
        self.recv_thread.start()

        # binding buttons
        self.send.clicked.connect(self.send_msg)
        self.nickname_changer.clicked.connect(self.change_nickname)
        self.historySaver.clicked.connect(self.save_history)
        print('All preparations are done. Have fun in SafeChatroom.')

    def send_msg(self) -> None:
        """function for 'send' button, implementation of sending messages"""
        cipher = AESCipher(self.AESkey)
        msg = '<{}> {}'.format(self.nickname, self.send_window.text())
        # print('Sent {}', msg)
        self.connect.send(cipher.encrypt(msg))
        self.send_window.clear()

    def print_msg(self, msg: str) -> None:
        """functon for threading of receiving messages"""
        # robust
        if msg:
            # adding new received msg to archive
            self.msg_recv += msg + '\n'
            # refresh message browser
            self.recv_window.setText(self.msg_recv)

    def change_nickname(self) -> None:
        """changing nickname for current client"""
        self.nickname = self.send_window.text()
        hint = '<System> Your nickname has been successfully changed to '
        self.print_msg(hint + self.nickname + '.')

    def save_history(self) -> None:
        """saving chat history to ./lib/history with .hs file"""
        # creating file name with current time and CPU timestamp
        t = time.localtime()
        tick = time.time()
        year, mon, day = t.tm_year, t.tm_mon, t.tm_mday
        fName = './history/' + str(year) + '.' + str(mon) + '.' + str(day) + '.' + str(tick) + '.hs'
        # saving chat history
        with open(fName, 'w') as fp:
            fp.write(self.msg_recv)
        hint = '<System> Current chat history has been successfully stored into ' + fName
        self.print_msg(hint)


class RecvThread(QThread):
    """thread for receiving msg from the server"""
    # signal
    trigger = pyqtSignal(str)
    msg_recv: str

    def __init__(self, connect: socket.socket, AES_key):
        super(RecvThread, self).__init__()
        self.connect = connect
        self.cipher = AESCipher(AES_key)

    # overriding run() for thread
    def run(self):
        while True:
            # decrypting received msg and sending it to slot function
            msg = self.cipher.decrypt(self.connect.recv(1024))
            if msg:
                self.trigger.emit(msg)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    client = ClientWindow()
    client.show()
    sys.exit(app.exec())
