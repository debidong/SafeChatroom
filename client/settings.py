import json
import sys

from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog
from lib.popout import Ui_popout


class WelcomeWindow(QDialog, Ui_popout):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        with open('./lib/ipconfig.json', 'r') as fp:
            ipconfig: dict = json.load(fp)
            self.IPAddress.setText(ipconfig['IP'])
            self.port.setText(ipconfig['port'])
        self.setWindowIcon(QIcon("./img/icon.img"))
        self.submit.clicked.connect(self.get_address)

    def get_address(self):
        IPAddress = self.IPAddress.text()
        port = self.port.text()
        ipconfig = {'IP': IPAddress, 'port': port}
        with open('./lib/ipconfig.json', 'w') as fp:
            json.dump(ipconfig, fp)
        self.IPAddress.setText('Changes have been modified.')
        self.port.setText('Target server is: ' + IPAddress + ':' + port)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    welcome = WelcomeWindow()
    welcome.show()
    sys.exit(app.exec())
