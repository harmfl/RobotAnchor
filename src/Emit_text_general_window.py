import Emit_text_general_window_style
# from Custom_Widgets.Widgets import *
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QIcon
import os


class Emit_general_window(Emit_text_general_window_style.Ui_Dialog, QMainWindow):
    transfer_text = pyqtSignal(str)

    def __init__(self,title='通用文本编辑窗口',label_text='请输入:'):
        super(Emit_general_window, self).__init__()
        self.cwd = os.path.dirname(__file__)
        self.title = title
        self.label_text = label_text
        self.setupUi(self)
        self.initUI()

        self.Y_b.clicked.connect(self.Y_b_clicked)
        self.N_b.clicked.connect(self.N_b_clicked)

    def initUI(self):
        self.setWindowTitle(self.title)
        _translate = QtCore.QCoreApplication.translate
        self.label.setText(_translate("Dialog", self.label_text))
        self.setWindowIcon(QIcon(f'{self.cwd}\\arc5.ico'))  # 替换 'icon.png' 为你的图标文件路径

    def Y_b_clicked(self):
        input_text = self.textEdit.toPlainText()
        if input_text == '' or input_text == '不可为空！':
            self.textEdit.append('不可为空！')
        else:
            input_text = input_text.replace('\n','')
            self.transfer_text.emit(input_text)
            self.close()

    def N_b_clicked(self):
        self.close()
