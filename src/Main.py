from PyQt5.QtCore import QThread, pyqtSignal, QMutex, Qt
from PyQt5.QtGui import QTextCursor, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextBrowser, QPushButton
# from Custom_Widgets.Widgets import QPushButton
import sys
import time
import os
import copy
import threading
import edge_tts
import uuid
import subprocess
import random
import re
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"  # 隐藏欢迎信息
import pygame
import pygame._sdl2.audio as sdl2_audio

import QuestionManager
import BarrageCatcher
import Emit_text_general_window
import List_general_window
import Main_sty
import AutoResponse
import Voice_select
import VoiceControlManager
import ThankGiftManager
from GiftBook import gift_list

# warnings.filterwarnings("ignore", category=DeprecationWarning)

cwd = os.path.dirname(__file__)

pygame.mixer.init()

class MakingMp3Thread(QThread):
    update_welcome_list = pyqtSignal(str,str)
    add_gift_thank_list = pyqtSignal(str,str)

    def __init__(self, comment,voice_model,mtype='welcome'):
        super(MakingMp3Thread, self).__init__(parent=None)
        self.comment = comment
        self.voice_model = voice_model
        self.running = True
        self.cwd = os.path.dirname(__file__)
        self.mtype = mtype

    def run(self):
        try:
            unique_id = uuid.uuid4()
            if self.mtype == 'welcome':
                text = f'欢迎{self.comment}!'
                unique_name = os.path.join(self.cwd, "WelcomeMedia", f"tts_{unique_id}.mp3")  # 拼接路径
            elif self.mtype == 'gift':
                # print(self.comment)
                A = re.match(r'^(.*?)(：)', self.comment)
                B = re.findall(r'送出(.*?)×', self.comment)
                C = self.comment.split('×', 1)[-1]
                combind = '感谢' + A.group(1) + '送出的' + C + '个' + B[0]
                text = combind
                # print(text)
                unique_name = os.path.join(self.cwd, "ThankGiftMedia", f"tts_{unique_id}.mp3")  # 拼接路径
            else:
                unique_name = os.path.join(self.cwd, "WelcomeMedia", f"tts_{unique_id}.mp3")  # 拼接路径
                text = self.comment
            communicate = edge_tts.Communicate(text, self.voice_model)

            with open(unique_name, 'wb') as file:
                for chunk in communicate.stream_sync():
                    if chunk["type"] == "audio":
                        file.write(chunk["data"])

            # print(f"音频已生成: {unique_name}")
            if self.mtype == "welcome":
                self.update_welcome_list.emit(unique_name, self.comment)
            elif self.mtype == "gift":
                self.add_gift_thank_list.emit(unique_name, self.comment)
            self.running = False
        except Exception as e:
            print(f"生成音频失败: {e}")
            self.running = False

class BarrageThread(QThread):
    # 定义信号，传递抓取到的弹幕内容到主线程
    update_browser_signal = pyqtSignal(str)
    speices_update_browser_signal = pyqtSignal(str, str)
    started_signal = pyqtSignal()

    def __init__(self, barrage_catcher, R_type):
        super(BarrageThread, self).__init__(parent=None)
        self.barrage_catcher = barrage_catcher
        self.running = True  # 控制线程运行
        self.R_type = R_type

    def run(self):
        if not self.barrage_catcher.WorkFlag:
            self.barrage_catcher.WorkFlag = True
        # self.barrage_catcher.get_room()
        print(f'barrage_catcher_{self.R_type}!')
        time.sleep(4)
        self.started_signal.emit()  # 发出启动信号
        if self.R_type == 'A':
            while self.running:
                # A = time.time()
                comments = self.barrage_catcher.print_name()
                if comments:
                    for index, comment in enumerate(comments):
                        # 格式化为字符串
                        formatted_comment = f"{comment[0]} {comment[1]}"
                        if not index == 0:
                            self.speices_update_browser_signal.emit(formatted_comment,'A')
                            # print('1：', formatted_comment)
                        else:
                            self.speices_update_browser_signal.emit(formatted_comment, 'A')
                            # print('1A:',formatted_comment)
                time.sleep(1)

        elif self.R_type == 'B':
            while self.running:
                last_comment = self.barrage_catcher.print_last_name()
                if last_comment:
                    formatted_comment = f"{last_comment[0]} {last_comment[1]}"
                    self.speices_update_browser_signal.emit(formatted_comment, 'B')
                time.sleep(0.3)
            # B = time.time()
            # C = B-A
            # print(f'运行时间:{C:.6f}')

    def stop(self):
        if self.barrage_catcher.WorkFlag:
            self.barrage_catcher.WorkFlag = False
        self.running = False
        self.wait()

class RobotAnchor(Main_sty.Ui_RobtoAnchor, QMainWindow):
    def __init__(self):
        super(RobotAnchor, self).__init__()
        self.setupUi(self)
        self.initUI()

        self.Screen_button.clicked.connect(self.chang_screen_window)
        self.Start_button.clicked.connect(self.start_catch_comment)
        # self.Stop_button.clicked.connect(self.stop_thread)
        self.InitAnchor_button.clicked.connect(self.init_anchor)
        self.QuestionResponseSetting_button.clicked.connect(self.question_response_setting_window)
        self.QuestionResponseStart_button.clicked.connect(self.question_response_start)
        self.SoundCardSelect_button.clicked.connect(self.sound_card_select_window)
        self.VoiceSelect_button.clicked.connect(self.voice_select_window)
        self.VoiceWelcomeStart_button.clicked.connect(self.voice_welcome_start)
        self.ThankGiftSetting_button.clicked.connect(self.thank_gift_setting_window)
        self.ThankGiftStart_button.clicked.connect(self.thank_gift_start)
        self.VoiceControlSetting_button.clicked.connect(self.voice_control_setting_window)
        self.VoiceControlStart_button.clicked.connect(self.voice_control_start)

        self.screen_x = 1920
        self.screen_y = 1080
        self.barrage_working = False
        self.barrage_thread_A = None  # 用于存储线程对象
        self.barrage_thread_B = None
        self.cwd = os.path.dirname(__file__)
        self.browser_mutex = QMutex()
        self.question_list = []
        self.last_spe_comment = []
        self.is_compare = True
        self.Anchor = None
        self.response_question_working = False
        self.voice_model = [None] * 2
        self.voice_welcome_working = False
        self.welcome_list = []                  # 存储欢迎
        self.welcome_wait_list = []             # 存储等待生成mp3的元素
        self.welcome_wait_max = 3
        self.speak_lock = threading.Lock()
        self.program_mp3 = f'{self.cwd}\\运行文件,请勿删除.mp3'
        self.max_make_mp3_thread = 3
        self.welcome_make_mp3_thread_pool = []          # 管理欢迎的mp3生成的线程池

        self.thank_gift_working = False
        self.thank_gift_list = []  # 第一个list存储当前感谢的人
        self.thank_gift_list2 = [] # 第二个list存储随机抽选的感谢语
        self.thank_gift_make_mp3_thread_pool = []
        self.max_gift_make_mp3_thread = 5

        self.voice_control_working = False
        self.voice_control_list = []            # 存储场控
        self.voice_control_index = 0
        self.interval_time = []
        self.voice_control_send = True
        self.play_mp3_manager_thread = None  # 当任何跟语音有关的任务启动时，启动这个线程

    def initUI(self):
        self.setWindowTitle("RobotAnchor")
        self.setWindowIcon(QIcon(cwd + "/arc5.ico"))

    def chang_screen_window(self):
        self.ChangeScreen = Emit_text_general_window.Emit_general_window(title='设置当前屏幕的尺寸',
                                                                         label_text='以","(英文)号分割')
        self.ChangeScreen.setWindowModality(Qt.ApplicationModal)
        self.ChangeScreen.transfer_text.connect(self.change_screen)
        self.ChangeScreen.show()

    def change_screen(self, ScreenSize):
        S = ScreenSize.split(',')
        self.screen_x = int(S[0])
        self.screen_y = int(S[1])
        self.print_in_browser(f"屏幕尺寸已设置为{self.screen_x}x{self.screen_y}", 1)

    def start_catch_comment(self):
        A = time.time()
        self.room_id = self.Room_edit.toPlainText()
        if not self.room_id:
            self.print_in_browser("请先输入正确的房间号", 1)
        elif not self.barrage_working:
            self.barrage_catcher = BarrageCatcher.BarrageCatcher(self.screen_x, self.screen_y, self.room_id)
            self.print_in_browser(f"正在启动弹幕抓取，目标房间号为{self.room_id}", 1)
            barrage_start_thread = threading.Thread(target=self.barrage_catcher.get_room)
            barrage_start_thread.start()

            # 如果线程已经存在并运行中，先停止
            if self.barrage_thread_A:
                if self.barrage_thread_A.running:
                    self.barrage_thread_A.stop()
            if self.barrage_thread_B:
                if self.barrage_thread_B.running:
                    self.barrage_thread_B.stop()

            # 初始化主弹幕抓取线程
            self.barrage_thread_A = BarrageThread(self.barrage_catcher, 'A')
            self.barrage_thread_A.update_browser_signal.connect(self.barrage_screening)
            self.barrage_thread_A.started_signal.connect(self.on_barrage_started_A)
            self.barrage_thread_A.speices_update_browser_signal.connect(self.barrage_screening)

            self.barrage_thread_B = BarrageThread(self.barrage_catcher, 'B')
            self.barrage_thread_B.update_browser_signal.connect(self.barrage_screening)
            self.barrage_thread_B.started_signal.connect(self.on_barrage_started_B)
            self.barrage_thread_B.speices_update_browser_signal.connect(self.barrage_screening)

            self.barrage_thread_A.start()  # 启动前端更新线程
            self.barrage_thread_B.start()

            self.Start_button.setStyleSheet("background-color:#35D861")
            self.Start_button.setText('关闭弹幕抓取')
            self.Start_button.setEnabled(False)
            thread = threading.Timer(3, self.set_start_disable)
            thread.start()
            B = time.time()
            print(f'启动耗时：{B - A:.6f}')
            self.barrage_working = True
        elif self.barrage_working:
            self.stop_thread()

    def set_start_disable(self):
        time.sleep(3)
        self.Start_button.setEnabled(True)

    def stop_thread(self):
        A = time.time()
        if self.barrage_thread_A and self.barrage_thread_A.isRunning():
            self.barrage_thread_A.stop()
            self.barrage_thread_B.stop()
            self.barrage_thread_A.wait()  # 等待线程安全退出
            self.barrage_thread_B.wait()  # 等待线程安全退出
            self.Start_button.setStyleSheet("")
            self.Start_button.setText('开始抓取弹幕')
            self.print_in_browser('已安全关闭弹幕抓取', 1)
            self.barrage_working = False
        else:
            self.print_in_browser('并没有开启弹幕抓取',1)
        B = time.time()
        print(f'停止耗时:{B - A:.6f}')

    def barrage_screening(self, comment, ctype=None): # 用于筛选，防止发送重复弹幕，并给每个弹幕分配应对
        # 在主线程中更新 Work_browser
        cursor = self.Work_browser.textCursor()  # 获取当前光标
        at_bottom = cursor.atEnd()  # 检查光标是否在最底部

        # 使用锁来确保线程安全
        # lock = QMutexLocker(self.browser_mutex)
        if ctype == 'B':
            print(f'{comment}进入B通道')
            self.speices_comment = comment
            self.comment_classify(comment)
            self.last_spe_comment.append(comment)
            # if self.is_compare:  # 是否比较了上一次B和A，如果未比较则保留上一次B
            #     self.last_spe_comment = comment
            #     print('last更新为：',comment)
            #     self.is_compare = False
        elif ctype == 'A':  # 如果和B发的相同就不发送
            print(f'{comment}进入A通道,将与{self.last_spe_comment}比较')
            if self.last_spe_comment[0] == comment:
                print(f'{comment}判定完成')
                self.last_spe_comment.pop(0)
                return
            else:
                print('通过')
                self.comment_classify(comment)
        else:
            print(f'{comment}进入常规通道')
            self.comment_classify(comment)  # 添加新内容

        if at_bottom:
            # 如果光标在最底部，才将光标移动到新内容的末尾
            self.Work_browser.moveCursor(QTextCursor.End)
            self.Work_browser.ensureCursorVisible()

    def comment_classify(self, comment):
        # 处理礼物感谢通道
        if self.thank_gift_working:
            # print('进入',comment)
            # 查找是否有礼物
            for i in gift_list:
                if i[1] in comment:
                    comment = re.sub(r'了.*(?=×)', i[0], comment)
                    self.Work_browser.append(comment)
                    self.thank_gift(comment)
                    # print('感谢',{comment})
                    return

            # 如果没有礼物信息，检查是否满足欢迎条件
            if comment.endswith('来了') and self.voice_welcome_working and len(
                    self.welcome_wait_list) < self.welcome_wait_max:
                self.Work_browser.append(comment)
                self.welcome_wait_list.append(comment[:-2])
                self.voice_welcome(comment[:-2])
                # print('欢迎',{comment})

            # 如果是问题回答通道
            elif self.response_question_working:
                self.handle_question(comment)
                # print('回答',comment)

            else:  # 常规弹幕通道
                self.handle_gift_in_comment(comment)
                # print('常规',comment)

        # 如果没有开启礼物感谢通道
        elif comment.endswith('来了') and self.voice_welcome_working and len(
                self.welcome_wait_list) < self.welcome_wait_max:
            self.Work_browser.append(comment)
            self.welcome_wait_list.append(comment[:-2])
            self.voice_welcome(comment[:-2])

        # 问题回答通道
        elif self.response_question_working:
            self.handle_question(comment)

        # 常规弹幕通道
        else:
            self.handle_gift_in_comment(comment)

    def handle_question(self, comment):   # comment_classify子函数，用于处理问题
        for index, i in enumerate(self.question_list):
            if i[0] in comment:
                self.Work_browser.append(comment)
                self.question_response(index, comment)
                break

    def handle_gift_in_comment(self, comment):  # comment_classify子函数，用于翻译礼物
        for i in gift_list:
            if i[1] in comment:
                comment = re.sub(r'了.*(?=×)', i[0], comment)
                self.Work_browser.append(comment)
                return
        self.Work_browser.append(comment)

    def on_barrage_started_A(self):
        self.print_in_browser("弹幕抓取α启动成功", 1)

    def on_barrage_started_B(self):
        self.print_in_browser("弹幕抓取β启动成功", 1)

    def init_anchor(self):
        self.Anchor = AutoResponse.AutoResponse(self.screen_x, self.screen_y)
        login_thread = threading.Thread(target=self.anchor_login_thread)
        login_thread.start()

    def anchor_login_thread(self):
        self.print_in_browser('请尽快在此网页登录', 2)
        self.Anchor.login()
        while not self.Anchor.login_success:
            time.sleep(0.5)
        self.print_in_browser('登录成功,正在进入无头模式...',2)
        while not self.Anchor.name_text:
            time.sleep(0.5)
        self.print_in_browser(f'主播账号配置完成：{self.Anchor.name_text}，已切换到无头模式', 2)

    def print_in_browser(self, text, btype):
        if btype == 1:
            cursor = self.Work_browser.textCursor()  # 获取当前光标
            at_bottom = cursor.atEnd()  # 检查光标是否在最底部

            timestamp = time.strftime("%H:%M:%S")
            self.Work_browser.append(f"[{timestamp}]{text}")

            if at_bottom:
                self.Work_browser.moveCursor(QTextCursor.End)
                self.Work_browser.ensureCursorVisible()
        elif btype == 2:
            cursor = self.Work_browser2.textCursor()  # 获取当前光标
            at_bottom = cursor.atEnd()  # 检查光标是否在最底部

            timestamp = time.strftime("%H:%M:%S")
            self.Work_browser2.append(f"[{timestamp}]{text}")

            if at_bottom:
                self.Work_browser2.moveCursor(QTextCursor.End)
                self.Work_browser2.ensureCursorVisible()

    def question_response_setting_window(self):
        self.question_setting_window = QuestionManager.QuestionManager(self.question_list)
        self.question_setting_window.setWindowModality(Qt.ApplicationModal)
        self.question_setting_window.questionListSignal.connect(self.question_response_setting)
        self.question_setting_window.show()

    def question_response_setting(self, question_list):
        self.question_list = question_list
        self.print_in_browser(f'已将共{len(self.question_list)}个问题存储完毕', 2)

    def question_response_start(self):
        if not self.question_list:
            self.print_in_browser('请先配置弹幕回复', 2)
        elif not self.Anchor.headless_working:
            self.print_in_browser('请先登录',2)
        elif not self.response_question_working:
            self.response_question_working = True
            self.print_in_browser('已成功开启弹幕回复',2)
            self.QuestionResponseStart_button.setStyleSheet("background-color:#35D861")
            self.QuestionResponseStart_button.setText("关闭弹幕回复")
        elif self.response_question_working:
            self.response_question_working = False
            self.print_in_browser('已关闭弹幕回复',2)
            self.QuestionResponseStart_button.setStyleSheet("")

    def question_response(self, index, comment):
        if self.response_question_working:
            lock = QMutexLocker(self.browser_mutex)
            Answer = self.question_list[index][1]
            self.Anchor.send_bulletin(Answer)
            self.print_in_browser(f'已回复弹幕"{comment}"',2)
            self.print_in_browser(comment,1)

    def sound_card_select_window(self):
        init_by_me = not pygame.mixer.get_init()
        if init_by_me:
            pygame.mixer.init()
        devices = tuple(sdl2_audio.get_audio_device_names(False)) # 获取可用的所有音频输出设备
        self.sound_card_select_w = List_general_window.List_window(list_it=devices,title='选择输出设备',option_display_length=40)
        self.sound_card_select_w.setWindowModality(Qt.ApplicationModal)
        self.sound_card_select_w.select_choice.connect(self.sound_card_select)
        self.sound_card_select_w.show()

    def sound_card_select(self, device):
        try:
            init_by_me = pygame.mixer.get_init()
            if init_by_me:
                pygame.mixer.quit()
            pygame.mixer.init(devicename=device)
            # self.play_mp3(mp3_path=self.program_mp3,ptype=2)
            self.print_in_browser(f'声卡切换成功:"{device}"',2)
        except Exception as e:
            init_by_me = not pygame.mixer.get_init()
            if init_by_me:
                pygame.mixer.init()
            self.print_in_browser('声卡切换出错，已切换回默认',2)
            print(e)

    def voice_select_window(self):
        self.select_window = Voice_select.Voice_select_window()
        self.select_window.setWindowModality(Qt.ApplicationModal)
        self.select_window.select_voice.connect(self.voice_select)
        self.select_window.show()

    def voice_select(self,value):
        self.voice_model[0] = value[0]
        self.voice_model[1] = value[1]
        self.print_in_browser(f'已选择配音模型{self.voice_model[1]}',2)

    def voice_welcome_start(self):
        if self.voice_model[1] is None:
            self.print_in_browser('请先选择声音模型',2)
        elif not self.voice_welcome_working:
            self.voice_welcome_working = True
            if self.play_mp3_manager_thread is None or not self.play_mp3_manager_thread.is_alive():
                self.play_mp3_manager_thread = threading.Thread(target=self.play_mp3_manager)
                self.play_mp3_manager_thread.start()
            self.welcome_list = []
            self.VoiceWelcomeStart_button.setStyleSheet("background-color:#35D861")
            self.VoiceWelcomeStart_button.setText("关闭语音欢迎")
            self.print_in_browser('已成功开启语音欢迎',2)
        elif self.voice_welcome_working:
            self.voice_welcome_working = False
            pygame.mixer.music.load(self.program_mp3)
            while len(self.welcome_make_mp3_thread_pool) != 0: # 因为欢迎要欢迎当前的，所以停止后要删除掉那些滞后的
                time.sleep(0.3)
                self.welcome_make_mp3_thread_pool = [
                    thread for thread in self.welcome_make_mp3_thread_pool if thread.running is True
                ]
            dir_d = os.path.join(self.cwd, 'WelcomeMedia')
            mp3_files = []
            for root, dirs, files in os.walk(dir_d):
                for file in files:
                    if file.endswith(".mp3"):
                        mp3_files.append(file)
            for file_name in mp3_files:
                os.remove(f'{dir_d}\\{file_name}')
            print(f'{dir_d}的音频文件已清理完毕')
            self.VoiceWelcomeStart_button.setStyleSheet("")
            self.VoiceWelcomeStart_button.setText("开启语音欢迎")
            self.print_in_browser('已关闭语音欢迎', 2)

    def voice_welcome(self,comment):
        if self.voice_welcome_working:
            while len(self.welcome_make_mp3_thread_pool) >= self.max_make_mp3_thread:
                time.sleep(0.3)
                self.welcome_make_mp3_thread_pool = [
                    thread for thread in self.welcome_make_mp3_thread_pool if thread.running is True
                ]
                print('等待中')
            # t = threading.Thread(target=self.make_mp3, args=(comment,))
            t = MakingMp3Thread(comment,self.voice_model[0])
            t.update_welcome_list.connect(self.update_welcome_list)
            self.welcome_make_mp3_thread_pool.append(t)
            t.start()

    def update_welcome_list(self,uname,comment):
        self.welcome_list.append([uname,comment])

    def thank_gift_setting_window(self):
        self.thank_gift_set_window = ThankGiftManager.ThankGiftManager(self.thank_gift_list2)
        self.thank_gift_set_window.setWindowModality(Qt.ApplicationModal)
        self.thank_gift_set_window.thank_gift_list.connect(self.thank_gift_setting)
        self.thank_gift_set_window.show()

    def thank_gift_setting(self,thank_gift_list2):
        if len(self.thank_gift_list2) != 0:
            self.thank_gift_list2 = thank_gift_list2
            self.print_in_browser(f'感谢语已设置完成：\n共{len(self.thank_gift_list2)}条语音',2)
        else:
            self.thank_gift_list = []
            self.thank_gift_list2 = []
            pygame.mixer.music.load(self.program_mp3)
            dir_d = os.path.join(self.cwd, 'ThankGiftMedia')
            mp3_files = []
            for root, dirs, files in os.walk(dir_d):
                for file in files:
                    if file.endswith(".mp3"):
                        mp3_files.append(file)
            for file_name in mp3_files:
                os.remove(f'{dir_d}\\{file_name}')
            print(f'{dir_d}的音频文件已清理完毕')
            self.print_in_browser(f'礼物感谢配置失败，请检查操作', 2)

    def thank_gift_start(self):
        if self.voice_model[1] is None:
            self.print_in_browser('请先选择声音模型', 2)
        elif len(self.thank_gift_list2) == 0:
            self.print_in_browser('请先配置礼物感谢',2)
        elif not self.thank_gift_working:
            self.thank_gift_working = True
            if self.play_mp3_manager_thread is None or not self.play_mp3_manager_thread.is_alive():
                self.play_mp3_manager_thread = threading.Thread(target=self.play_mp3_manager)
                self.play_mp3_manager_thread.start()
            self.ThankGiftStart_button.setStyleSheet("background-color:#35D861")
            self.ThankGiftStart_button.setText("关闭礼物感谢")
            self.print_in_browser('已成功开启礼物感谢',2)
        elif self.thank_gift_working:
            self.thank_gift_working = False
            pygame.mixer.music.load(self.program_mp3)
            self.ThankGiftStart_button.setStyleSheet("")
            self.ThankGiftStart_button.setText("开启感谢礼物")
            self.print_in_browser('已关闭礼物感谢',2)

    def thank_gift(self,comment):
        if self.thank_gift_working:
            while len(self.thank_gift_make_mp3_thread_pool) >= self.max_gift_make_mp3_thread:
                time.sleep(0.3)
                self.thank_gift_make_mp3_thread_pool = [
                    thread for thread in self.thank_gift_make_mp3_thread_pool if thread.running is True
                ]
                print('等待中2 ')
            t = MakingMp3Thread(comment,self.voice_model[0],'gift')
            t.add_gift_thank_list.connect(self.add_gift_thank_list)
            self.thank_gift_make_mp3_thread_pool.append(t)
            t.start()

    def add_gift_thank_list(self,uname,comment):
        self.thank_gift_list.append([uname,comment])

    def voice_control_setting_window(self):
        self.voice_control_set_window = VoiceControlManager.VoiceControlManager(self.voice_control_list,self.interval_time)
        self.voice_control_set_window.setWindowModality(Qt.ApplicationModal)
        self.voice_control_set_window.FinalSignal.connect(self.voice_control_setting)
        self.voice_control_set_window.show()

    def voice_control_setting(self,voice_text_list,interval_time):
        if len(self.voice_control_list) != 0 and len(self.interval_time) != 0:
            self.voice_control_list = voice_text_list
            self.interval_time = interval_time
            self.voice_control_index = 0
            self.print_in_browser(f'场控已设置完成:\n共{len(self.voice_control_list)}条语音\n播放时间间隔：{self.interval_time}',2)
        else:
            self.voice_control_list = []
            self.interval_time = []
            pygame.mixer.music.load(self.program_mp3)
            dir_d =os.path.join(self.cwd, 'VoiceControlMedia')
            mp3_files = []
            for root, dirs, files in os.walk(dir_d):
                for file in files:
                    if file.endswith(".mp3"):
                        mp3_files.append(file)
            for file_name in mp3_files:
                os.remove(f'{dir_d}\\{file_name}')
            print(f'{dir_d}的音频文件已清理完毕')
            self.print_in_browser(f'语音场控配置失败，请检查操作',2)

    def voice_control_start(self):
        if len(self.voice_control_list) == 0:
            self.print_in_browser('请先配置场控',2)
        elif self.voice_control_working is False:
            self.voice_control_working = True
            if self.play_mp3_manager_thread is None or not self.play_mp3_manager_thread.is_alive():
                self.play_mp3_manager_thread = threading.Thread(target=self.play_mp3_manager)
                self.play_mp3_manager_thread.start()
            self.VoiceControlStart_button.setStyleSheet("background-color:#35D861")
            self.VoiceControlStart_button.setText("关闭语音场控")
            self.print_in_browser('已成功开启语音场控', 2)
        elif self.voice_control_working:
            self.voice_control_working = False
            pygame.mixer.music.load(self.program_mp3)
            self.VoiceControlStart_button.setStyleSheet("")
            self.VoiceControlStart_button.setText("开启语音场控")
            self.print_in_browser('已关闭语音场控',2)

    def voice_control_alarm_clock(self):
        if self.voice_control_index + 1 >= len(self.voice_control_list):
            self.voice_control_index = 0
        else:
            self.voice_control_index += 1
        self.voice_control_send = True

    def play_mp3_manager(self): # 在有复数播放任务时，管理哪个播放任务应该先进行
        while self.voice_welcome_working or self.thank_gift_working or self.voice_control_working:
            if self.thank_gift_working and len(self.thank_gift_list) != 0:
                thread = threading.Thread(target=self.play_mp3, args=(self.thank_gift_list[0],3)) # 在这里不直接调用而是用线程，以触发play_mp3的线程锁
                thread.start()
                # self.play_mp3(self.thank_gift_list[0],3)
                self.play_mp3(random.choice(self.thank_gift_list2),4)
                self.thank_gift_list.pop(0)
            elif self.voice_welcome_working and len(self.welcome_list) != 0:
                self.play_mp3(self.welcome_list[0],2)
                self.welcome_list.pop(0)
            elif self.voice_control_working and len(self.voice_control_list) != 0 and self.voice_control_send:
                self.play_mp3(self.voice_control_list[self.voice_control_index],1)
                self.voice_control_send = False
                alarm_clock = threading.Timer(random.choice(self.interval_time),self.voice_control_alarm_clock)
                alarm_clock.start()
            time.sleep(0.3)

    def play_mp3(self,pvalue,weight=1):
        with self.speak_lock:
            try:
                pygame.mixer.music.load(pvalue[0])
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                pygame.mixer.music.load(self.program_mp3)
                if weight == 4:
                    # self.print_in_browser(f'已感谢{pvalue[1]}',2)
                    pass
                elif weight == 3: # 3对应播放感谢的人，因为还要播放感谢语所以不用输出
                    os.remove(pvalue[0])
                    self.print_in_browser(f'已感谢"{pvalue[1]}"',2)
                elif weight == 2: # 2对应欢迎，这种情况要删除音频
                    os.remove(pvalue[0])
                    self.print_in_browser(f'已语音欢迎{pvalue[1]}',2)
                    self.welcome_wait_list.remove(pvalue[1])
                    # print(f'已删除欢迎音频{pvalue[1]}')
                elif weight == 1: # 对应场控，不用删除音频
                    self.print_in_browser(f'已播放场控{pvalue[1]}',2)
            except Exception as e:
                print(f"播放或删除音频文件失败: {e}")

    def closeEvent(self, a0, Any=None):
        self.print_in_browser('正在关闭后台进程和运行文件，请稍等',2)
        thread = threading.Thread(target=self.close_work)
        thread.start()

    def close_work(self):
        if self.barrage_thread_A:
            if self.barrage_thread_A.running:
                self.stop_thread()
        if self.Anchor:
            self.Anchor.browers.quit()
        if self.thank_gift_working or self.voice_control_working or self.voice_welcome_working:
            self.thank_gift_working = False
            self.voice_welcome_working = False
            self.voice_control_working = False
        pygame.mixer.music.load(self.program_mp3)
        del_dir = [os.path.join(self.cwd,'VoiceControlMedia'),os.path.join(self.cwd,'WelcomeMedia'),os.path.join(self.cwd,'ThankGiftMedia')]
        for dir_d in del_dir:
            mp3_files = []
            for root, dirs, files in os.walk(dir_d):
                for file in files:
                    if file.endswith(".mp3"):
                        mp3_files.append(file)
            for file_name in mp3_files:
                os.remove(f'{dir_d}\\{file_name}')
            print(f'{dir_d}的音频文件已清理完毕')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = RobotAnchor()
    MainWindow.show()
    sys.exit(app.exec_())
