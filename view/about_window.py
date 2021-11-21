from PySide2 import QtCore, QtWidgets
from PySide2.QtGui import QDesktopServices


class AboutWindow(QtWidgets.QWidget):
    def __init__(self):
        super(AboutWindow,  self).__init__()

        self._main_layout = QtWidgets.QVBoxLayout()
        self._contibutors_layout = QtWidgets.QGridLayout()
        self.setFixedSize(500, 250)
        self.setWindowTitle("About")

        self._initWindow()

    def _initWindow(self):
        self._main_layout.addWidget(QtWidgets.QLabel("LumberBOTS"))
        self._main_layout.addWidget(QtWidgets.QLabel("Contributors:"))

        self._contibutors_layout.addWidget(QtWidgets.QLabel("\tMateusz Adamczky"), 0, 0)
        self._contibutors_layout.addWidget(QtWidgets.QLabel("241567@student.pwr.edu.pl"), 0, 1)
        self._contibutors_layout.addWidget(QtWidgets.QLabel("\tDaniel Śliwowski"), 1, 0)
        self._contibutors_layout.addWidget(QtWidgets.QLabel("241166@student.pwr.edu.pl"), 1, 1)
        self._contibutors_layout.addWidget(QtWidgets.QLabel("\tJakub Tomaszweski"), 2, 0)
        self._contibutors_layout.addWidget(QtWidgets.QLabel("241576@student.pwr.edu.pl"), 2, 1)
        self._contibutors_layout.addWidget(QtWidgets.QLabel("\tMateusz Urbaniak"), 3, 0)
        self._contibutors_layout.addWidget(QtWidgets.QLabel("241614@student.pwr.edu.pl"), 3, 1)

        self._main_layout.addLayout(self._contibutors_layout)

        self._robot_label = QtWidgets.QLabel("<a target=\"_blank\" href=\"https://icons8.com/icon/O5duduyEee1i/robot\">Robot</a> icon by <a target=\"_blank\" href=\"https://icons8.com\">Icons8</a>")
        self._robot_label.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        self._robot_label.linkActivated.connect(self._open_link)

        self._tree_label = QtWidgets.QLabel("<a target=\"_blank\" href=\"https://icons8.com/icon/6xmAFCGEcVns/tree\">Tree</a> icon by <a target=\"_blank\" href=\"https://icons8.com\">Icons8</a>")        
        self._tree_label.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        self._tree_label.linkActivated.connect(self._open_link)

        self._main_layout.addWidget(QtWidgets.QLabel("Icons:"))
        self._main_layout.addWidget(self._robot_label)
        self._main_layout.addWidget(self._tree_label)

        self.setLayout(self._main_layout)

    @QtCore.Slot()
    def _open_link(self, link):
        QDesktopServices.openUrl(link)
