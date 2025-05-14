import sys
import os
from PyQt5.QtCore import pyqtSignal, QThread, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtGui import QIcon
# from Custom_Widgets.Widgets import *
import time
import edge_tts
import threading
import uuid
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"  # 隐藏欢迎信息
import pygame

import ThankGiftManager_sty
import List_general_window
import Voice_select

class WorkThread(QThread):
    update_browser_signal = pyqtSignal(str)
    update_remove_list_signal = pyqtSignal(str)

    def __init__(self,unique_name, text, voice_control_list, voice):
        super(WorkThread, self).__init__(parent=None)
        self.ThankGiftList = voice_control_list
        self.unique_name = unique_name
        self.text = text
        self.voice = voice
        self.cwd = os.path.dirname(os.path.realpath(__file__))
        self.running = True

    def run(self):
        self.update_browser_signal.emit(f'“{self.text}”已进入队列')
        old_text_list = [d[1] for d in self.ThankGiftList]
        if old_text_list.count(self.text) >= 2: # 假如有两个才算重复，因为其提前添加了一个
            self.update_browser_signal.emit(f'不可添加重复文本“{self.text}”')
            self.update_remove_list_signal.emit(self.unique_name)
            self.running = False
            return
        else:
            try:
                communicate = edge_tts.Communicate(self.text, self.voice)

                with open(self.unique_name, 'wb') as file:
                    for chunk in communicate.stream_sync():
                        if chunk["type"] == "audio":
                            file.write(chunk["data"])

                self.update_browser_signal.emit(f'已成功添加“{self.text}”')
                self.running = False

                # print(f"音频已生成: {self.text}")
            except Exception as e:
                print(f"生成音频失败: {e}")
                self.update_remove_list_signal.emit(self.unique_name)
                self.running = False

class ThankGiftManager(ThankGiftManager_sty.Ui_MainWindow,QMainWindow):
    thank_gift_list = pyqtSignal(list)

    def __init__(self, thank_gift_list):
        super(ThankGiftManager, self).__init__()
        self.cwd = os.path.dirname(__file__)
        self.setupUi(self)
        self.initUI()

        self.SelectVoice_button.clicked.connect(self.voice_select_window)
        self.Add_button.clicked.connect(self.add_text)
        self.Txt_button.clicked.connect(self.txt_add_text)
        self.ListenTest_button.clicked.connect(self.listen_test_window)
        self.Del_button.clicked.connect(self.del_text_window)
        self.Show_button.clicked.connect(self.show_text)
        self.Affirm_button.clicked.connect(self.affirm)

        self.voice_model = [None] *2
        self.ThankGiftList = thank_gift_list
        self.max_make_mp3_thread = 5
        self.make_mp3_thread_pool = []
        self.program_mp3 = f'{self.cwd}\\运行文件,请勿删除.mp3'

    def initUI(self):
        self.setWindowTitle("礼物感谢配置")
        self.setWindowIcon(QIcon(os.path.join(self.cwd, 'arc5.ico')))

    def print_in_browser(self, text):
        timestamp = time.strftime("%H:%M:%S")
        self.Work_browser.append(f'[{timestamp}]{text}')
        
    def voice_select_window(self):
        self.select_window = Voice_select.Voice_select_window()
        self.select_window.setWindowModality(Qt.ApplicationModal)
        self.select_window.select_voice.connect(self.voice_select)
        self.select_window.show()

    def voice_select(self, value):
        self.voice_model[0] = value[0]
        self.voice_model[1] = value[1]
        self.print_in_browser(f'已选择配音模型"{self.voice_model[1]}"')

    def add_text(self):
        if self.voice_model[1] is None:
            self.print_in_browser('请先选择声音模型')
        elif self.Thank_edit.toPlainText().strip() == '':
            self.print_in_browser('输入不可为空')
        else:
            text = self.Thank_edit.toPlainText().strip()
            thread = threading.Thread(target=self.add_text_thread, args=(None, text, 1))
            thread.start()
            
    def txt_add_text(self):
        if self.voice_model[1] is None:
            self.print_in_browser('请先选择声音模型')
        else:
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getOpenFileName(
                None,
                "选择文件",  # 窗口标题
                "",  # 起始目录（空字符串表示当前目录）
                "文本文件 (*.txt);;所有文件 (*)"  # 过滤器，支持多种文件类型
            )
            if file_path:
                thread = threading.Thread(target=self.add_text_thread, args=(file_path,None,2))
                thread.start()
                
    def add_text_thread(self,file_path=None,ori_text=None,ttype=1):
        if ttype == 1:
            text_list = ori_text.split('\n')
            text_list_2 = [item for item in text_list if item != '']
            for text in text_list_2:
                unique_id = uuid.uuid4()
                unique_name = os.path.join(self.cwd, "ThankGiftMedia", f"{unique_id}.mp3")  # 拼接路径
                self.ThankGiftList.append([unique_name,text]) # 提前添加，方便进行重复性检查，如果出问题Qthread再删除添加的
                t = WorkThread(unique_name, text, self.ThankGiftList, self.voice_model[0])
                self.make_mp3_thread_pool.append(t)
                t.update_browser_signal.connect(self.print_in_browser)
                t.update_remove_list_signal.connect(self.update_remove_list)
                t.start()
        elif ttype == 2:
            if file_path:  # 如果用户选择了文件
                self.print_in_browser('开始txt批量作业')
                with open(file_path, 'r', encoding='utf-8') as file:
                    lines = file.read()
                    lines = lines.split('\n')
                    text_list = [item for item in lines if item != '']
                for text in text_list:
                    while len(self.make_mp3_thread_pool) >= self.max_make_mp3_thread:
                        time.sleep(0.3)
                        self.make_mp3_thread_pool = [
                            thread for thread in self.make_mp3_thread_pool if thread.running is True
                        ]
                        # print('等待中')
                    # print(text, '进入队列')
                    unique_id = uuid.uuid4()
                    unique_name = os.path.join(self.cwd, "ThankGiftMedia", f"{unique_id}.mp3")  # 拼接路径
                    self.ThankGiftList.append([unique_name, text])  # 提前添加，方便进行重复性检查，如果出问题Qthread再删除添加的
                    t = WorkThread(unique_name, text, self.ThankGiftList, self.voice_model[0])
                    self.make_mp3_thread_pool.append(t)
                    t.update_browser_signal.connect(self.print_in_browser)
                    t.update_remove_list_signal.connect(self.update_remove_list)
                    t.start()
                    # self.make_mp3_pool(t)
                    # self.print_in_browser(f'{t}已进入生成队列')

    def update_remove_list(self, u_name):
        for sublist in self.ThankGiftList:
            if sublist[0] == u_name:
                self.ThankGiftList.remove(sublist)

    def listen_test_window(self):
        translate_list = [i[1] for i in self.ThankGiftList]
        self.listen_window = List_general_window.List_window(list_it=translate_list,title='选择要试听的文本',option_display_length=20)
        self.listen_window.setWindowModality(Qt.ApplicationModal)
        self.listen_window.select_choice.connect(self.listen_test)
        self.listen_window.show()

    def listen_test(self, value):
        init_by_me = not pygame.mixer.get_init()
        if init_by_me:
            pygame.mixer.init()
        for sublist in self.ThankGiftList:
            if sublist[1] == value:
                pygame.mixer.music.load(sublist[0])
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                pygame.mixer.music.load(self.program_mp3)

    def del_text_window(self):
        translate_list = [i[1] for i in self.ThankGiftList]
        self.del_window = List_general_window.List_window(list_it=translate_list, title='选择要删除',
                                                             option_display_length=20)
        self.del_window.setWindowModality(Qt.ApplicationModal)
        self.del_window.select_choice.connect(self.del_text)
        self.del_window.show()

    def del_text(self, value):
        for sublist in self.ThankGiftList:
            if sublist[1] == value:
                os.remove(sublist[0])
                print(f'已删除{sublist[0]}')
                self.ThankGiftList.remove(sublist)
                self.print_in_browser(f'已将语句{value}从队列中删除')
                return

        self.print_in_browser('删除失败')

    def show_text(self):
        self.Work_browser.clear()
        if len(self.ThankGiftList) == 0:
            self.print_in_browser('当前并没有存储任何音频文本')
        else:
            self.print_in_browser(f'当前一共存储了{len(self.ThankGiftList)}条音频文本')
            for t in self.ThankGiftList:
                self.Work_browser.append(t[1])

    def affirm(self):
        # self.VoiceControlSignal.emit(self.voice_control_list)
        # self.TimerIntervalSignal.emit(self.interval_time)
        self.thank_gift_list.emit(self.ThankGiftList)
        self.close()


# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     window = ThankGiftManager()
#     window.show()
#     sys.exit(app.exec_())
