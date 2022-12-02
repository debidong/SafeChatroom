import json
import socket
import sys
import time

from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog

from lib.chatroom import Ui_SafeChatroom
from lib.cipher import AESCipher, RSCCipher


class ClientWindow(QDialog, Ui_SafeChatroom):
    msg_recv = ''
    nickname = 'unknown'
    host = ''
    port = ''

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # initializing socket
        with open('./lib/ipconfig.json', 'r') as fp:
            ipconfig: dict = json.load(fp)
            self.host = ipconfig['IP']
            self.port = int(ipconfig['port'])
        print('Trying to connect server at {}:{}.'.format(self.host, self.port))
        self.connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect.connect((self.host, self.port))
        # try:
        #     self.connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #     self.connect.connect((self.host, self.port))
        # except:
        #     print('ERROR: The server according to IP address and port number is not running!')
        #     print('Check the setting or rerun the server.')
        #     sys.exit(-1)

        print('Server found. Generating RSC keypair and exchanging keys...')
        # generating RSC keypair
        rsc = RSCCipher()
        # sending RSC pubkey to server
        self.connect.send(rsc.pubKeyPEM)

        # receiving AESkey
        encrypted_AESkey = bytes(self.connect.recv(1024))
        self.AESkey = rsc.decrypt(encrypted_AESkey)
        print('AESkey received: {}.'.format(self.AESkey))

        # initializing thread
        print('Starting threads...')
        self.recv_thread = RecvThread(self.connect, self.AESkey)
        self.recv_thread.trigger.connect(self.print_msg)
        self.recv_thread.start()

        # initializing buttons
        self.send.clicked.connect(self.send_msg)
        self.nickname_changer.clicked.connect(self.change_nickname)
        self.historySaver.clicked.connect(self.save_history)
        print('All preparations are done. Have fun in SafeChatroom.')

    def send_msg(self):
        """function for 'send' button, implementation of sending messages"""
        cipher = AESCipher(self.AESkey)
        msg = '<{}> {}'.format(self.nickname, self.send_window.text())
        # print('Sent {}', msg)
        self.connect.send(cipher.encrypt(msg))
        self.send_window.clear()

    def print_msg(self, msg: str):
        """functon for threading of receiving messages"""
        if msg:
            self.msg_recv += msg + '\n'
            self.recv_window.setText(self.msg_recv)

    def change_nickname(self):
        self.nickname = self.send_window.text()
        hint = '<System> Your nickname has been successfully changed to '
        self.print_msg(hint + self.nickname + '.')

    def save_history(self):
        t = time.localtime()
        tick = time.time()
        year, mon, day = t.tm_year, t.tm_mon, t.tm_mday
        fName = './history/' + str(year) + '.' + str(mon) + '.' + str(day) + '.' + str(tick) + '.hs'
        fo = open(fName, 'w')
        fo.write(self.msg_recv)
        fo.close()
        hint = '<System> Current chat history has been successfully stored into ' + fName
        self.print_msg(hint)


class RecvThread(QThread):
    trigger = pyqtSignal(str)

    def __init__(self, connect: socket.socket, AES_key):
        super(RecvThread, self).__init__()
        self.connect = connect
        self.msg_recv = ''
        self.cipher = AESCipher(AES_key)

    def run(self):
        while True:
            msg = self.cipher.decrypt(self.connect.recv(1024))
            if msg:
                self.trigger.emit(msg)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    client = ClientWindow()
    client.show()
    sys.exit(app.exec())
