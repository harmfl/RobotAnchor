# from Custom_Widgets.Widgets import *
from PyQt5.QtCore import pyqtSignal
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtGui import QIcon
from PyQt5 import QtGui, QtCore
import Voice_model
from PyQt5.QtCore import Qt

class Voice_select_window(QWidget):
    select_voice = pyqtSignal(list)

    def __init__(self):
        super().__init__(parent=None)
        self.cwd = os.path.dirname(__file__)
        self.initUI()
        self.button_color = None

    def initUI(self):
        self.setWindowTitle('选择声音')
        self.move(800, 220)
        layout = QVBoxLayout(self)
        self.resize(300, 200)
        self.setWindowIcon(QIcon(f'{self.cwd}\\arc5.ico'))  # 替换 'icon.png' 为你的图标文件路径

        for i in Voice_model.voice_list:
            voice_name = i['Chinese']
            button = QPushButton(f'{voice_name}', self)
            button.setStyleSheet("QPushButton:hover {\n"
                     "background-color: #E0EEF9;\n"
                     "}")
            button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            button.clicked.connect(self.buttonClicked)
            layout.addWidget(button)

    def buttonClicked(self):
        voice_b = self.sender()
        for voice in Voice_model.voice_list:
            if voice.get("Chinese") == voice_b.text():
                transfer = [voice['Name'], voice['Chinese']]
                self.select_voice.emit(transfer)
                self.close()
                break


# if __name__ == '__main__':
#     app = QApplication([])
#     window = Voice_select_window()
#     window.show()
#     app.exec_()
