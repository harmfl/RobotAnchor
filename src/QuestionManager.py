import sys
from PyQt5.QtCore import pyqtSignal, QThread
import os
import time
from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow, QPushButton
from PyQt5.QtGui import QIcon
# from Custom_Widgets.Widgets import *

import List_general_window
import QuestionManager_sty


def read_file_in_chunks(file_path, chunk_size=3):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            while True:
                # 读取三行并去除空白字符，组成一个列表
                lines = [file.readline().strip() for _ in range(chunk_size)]
                # 去除空行，保留非空内容
                lines = [line for line in lines if line]
                if not lines:  # 如果没有更多内容，退出循环
                    break
                yield lines  # 将三行的内容组合成一个列表返回
    except Exception as e:
        print(f"读取文件出错: {e}")

def is_positive_integer(value):
    try:
        number = int(value)
        return number > 0
    except ValueError:
        return False


class QuestionManager(QuestionManager_sty.Ui_MainWindow,QMainWindow):
    questionListSignal = pyqtSignal(list)

    def __init__(self,question_list):
        super(QuestionManager, self).__init__()
        self.cwd = os.path.dirname(__file__)
        self.title = '问题管理'
        self.setupUi(self)
        self.initUI()

        self.Add_button.clicked.connect(self.add_question)
        self.Del_button.clicked.connect(self.delete_question_window)
        self.Show_button.clicked.connect(self.show_question)
        self.Txt_button.clicked.connect(self.txt_question)
        self.Affirm_button.clicked.connect(self.affirm_question)

        self.questionList = question_list

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(os.path.join(self.cwd,'arc5.ico')))

    def add_question(self):
        question_key = self.QuestionKey_edit.toPlainText().strip()
        answer = self.Answer_edit.toPlainText().strip()
        weight = self.Weight_edit.toPlainText().strip()

        inputs = [question_key, answer, weight]
        edits = [self.QuestionKey_edit, self.Answer_edit, self.Weight_edit]

        # 检查输入是否为空
        for value, edit in zip(inputs, edits):
            if value == '' or value == '不可为空！':
                edit.setPlainText('不可为空！')  # 提示信息
                timestamp = time.strftime("%H:%M:%S")
                self.Work_browser.append(f'[{timestamp}]输入不可为空')
                return False

        if not is_positive_integer(weight):
            timestamp = time.strftime("%H:%M:%S")
            self.Work_browser.append(f'[{timestamp}]权重只可输入正整数')
            return False

        # 检查 question_key 是否重复
        for question in self.questionList:
            if question[0] == question_key:
                self.Work_browser.append(
                    f'[{time.strftime("%H:%M:%S")}] 题目 "{question_key}" 已存在，无法重复添加！')
                return False

        # 添加新问题到列表
        self.questionList.append([question_key, answer, weight])
        timestamp = time.strftime("%H:%M:%S")
        self.Work_browser.append(f'[{timestamp}] "{question_key}" 已成功添加到列表')
        return True

    def delete_question_window(self):
        translate_list = [question[0] for question in self.questionList]
        self.Question_del_window = List_general_window.List_window(list_it=translate_list,title='选择要删除的问题')
        self.Question_del_window.setWindowModality(Qt.ApplicationModal)
        self.Question_del_window.select_choice.connect(self.delete_question)
        self.Question_del_window.show()

    def delete_question(self,del_question_key):
        for sublist in self.questionList:
            if sublist[0] == del_question_key:  # target_value 是您要匹配的 question[0]
                self.questionList.remove(sublist)
                timestamp = time.strftime("%H:%M:%S")
                self.Work_browser.append(f'[{timestamp}]已删除"{sublist[0]}"')
                return  # 删除后退出循环（假设 question[0] 唯一）
        timestamp = time.strftime("%H:%M:%S")
        self.Work_browser(f'[{timestamp}]删除失败')

    def show_question(self):
        self.Work_browser.clear()
        if not self.questionList == []:
            self.Work_browser.append(f'共{len(self.questionList)}个问题')
            for i in self.questionList:
                timestamp = time.strftime("%H:%M:%S")
                self.Work_browser.append(f'[{timestamp}]问题关键词：{i[0]}')
                self.Work_browser.append(f'答案：{i[1]}')
                self.Work_browser.append(f'权重：{i[2]}')
        else:
            timestamp = time.strftime("%H:%M:%S")
            self.Work_browser.append(f'[{timestamp}]当前没有存储任何问题')

    def txt_question(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            None,
            "选择文件",  # 窗口标题
            "",  # 起始目录（空字符串表示当前目录）
            "文本文件 (*.txt);;所有文件 (*)"  # 过滤器，支持多种文件类型
        )

        if file_path:  # 如果用户选择了文件
            for index,chunk in enumerate(read_file_in_chunks(file_path)):
                if len(chunk) == 3 and is_positive_integer(chunk[2]):
                    self.questionList.append(chunk)
                    timestamp = time.strftime("%H:%M:%S")
                    self.Work_browser.append(f'[{timestamp}]已添加"{chunk[0]}"')
                else:
                    timestamp = time.strftime("%H:%M:%S")
                    self.Work_browser.append(f'[{timestamp}]第{index+1}组问题存储时发生错误，请检查txt文件内容')
                    break

    def affirm_question(self):
        self.questionListSignal.emit(self.questionList)
        self.Work_browser.append('das')
        self.close()


# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     window = QuestionManager()
#     window.show()
#     sys.exit(app.exec_())
