# from Custom_Widgets.Widgets import *
from PyQt5.QtCore import pyqtSignal
import os
from PyQt5.QtGui import QIcon
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QPushButton


class List_window(QWidget):
    select_choice = pyqtSignal(str)

    def __init__(self,list_it,title='通用列表选择窗口',button_color='#FFF',option_display_length=15):
        super().__init__(parent=None)
        self.cwd = os.path.dirname(__file__)
        self.button_color = button_color
        self.title = title
        self.list_it = list_it
        self.option_display_length = option_display_length
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.move(800, 220)
        layout = QVBoxLayout(self)
        self.resize(400, 600)
        # self.setMaximumSize(300, 200)
        self.setWindowIcon(QIcon(f'{self.cwd}\\arc5.ico'))  # 替换 'icon.png' 为你的图标文件路径

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        scroll_layout = QVBoxLayout(scroll_content)

        for i in self.list_it:
            display_text = i[:self.option_display_length] + '...' if len(i) > self.option_display_length else i
            button = QPushButton(display_text, self)
            button.setToolTip(i)#设置按钮提示
            button.setStyleSheet("QPushButton:hover {\n"
                     f"background-color: {self.button_color};\n"
                     "}")
            button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))#设定光标
            button.clicked.connect(self.buttonClicked)
            layout.addWidget(button)
            scroll_layout.addWidget(button)

    def buttonClicked(self):
        choice_b = self.sender()
        for item in self.list_it:
            if item == choice_b.toolTip():
                self.select_choice.emit(item)
                self.close()
                break
