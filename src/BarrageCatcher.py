from bs4 import BeautifulSoup
import sys
import threading
import time
import os
import encodings.idna
import warnings
from selenium import webdriver  # # 驱动浏览器
from selenium.webdriver.common.by import By  #选择器
from selenium.webdriver.support.wait import WebDriverWait  #等待页面加载完毕，寻找某些元素
from selenium.webdriver.support import expected_conditions as EC  ##等待指定标签加载完毕
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.remote.remote_connection import LOGGER

# LOGGER.setLevel(logging.WARNING)
# 设置日志格式和编码
# logging.basicConfig(
#     level=logging.DEBUG,
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.StreamHandler(stream=sys.stdout),  # 将日志输出到标准输出
#     ]
# )
# logging.getLogger().handlers[0].stream.reconfigure(encoding='utf-8')
class BarrageCatcher:
    def __init__(self, screen_x, screen_y, room):
        self.url_login ='https://live.douyin.com/'
        # self.screen_x = 1920
        # self.screen_y = 1080
        self.screen_x = screen_x
        self.screen_y = screen_y
        self.room = room

        self.options=webdriver.EdgeOptions()

        self.options.add_experimental_option("excludeSwitches", ['enable-automation', 'enable-logging'])
        self.options.add_argument('--mute-audio')
        self.options.add_argument("--disable-gpu")
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--ignore-ssl-errors')
        # self.options.add_argument('--headless')
        # self.options.add_argument(f"--window-size={self.screen_x},{self.screen_y}") # 特殊情况需要调整
        # self.options.add_argument("user-agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'")
        self.browers=webdriver.Edge(options=self.options)
        self.wait=WebDriverWait(self.browers,0.5)

        self.WorkFlag = False
        self.all_comments = []
        self.last_comments = []
        self.speice_comments = None
        self.last_speice_comments = None
        self.max_num = 30
        self.A = time.time()

    def get_room(self):
        # self.room=input('请输入房间号:') 20183400634"
        # self.room = "456066026839"
        url = self.url_login+self.room
        self.browers.get(url)

    def print_name(self):
        # print("弹幕爬虫启动成功")
        if self.WorkFlag:
            try:
                # 获取所有类名为 'TNg5meqw' 的元素
                elements = self.browers.find_elements(By.CLASS_NAME, 'TNg5meqw')
                if elements:
                    # 保护措施：如果元素少于 10 个，则只检查现有元素
                    check_elements = elements[-1 * self.max_num:] if len(elements) >= self.max_num else elements
                    self.all_comments = []
                    for last_element in check_elements[:-1]:
                        try:
                            name_element = last_element.find_element(By.CLASS_NAME, 'u2QdU6ht')
                            comment_element = last_element.find_element(By.CLASS_NAME, 'WsJsvMP9')

                            # 获取 comment_element 的完整 HTML 内容
                            comment_html = comment_element.get_attribute("innerHTML")

                            # 使用 BeautifulSoup 解析 HTML
                            soup = BeautifulSoup(comment_html, 'html.parser')

                            # 提取各部分内容
                            text1 = soup.find(class_='hH0pxiDh')  # 第一段文字
                            img_tag = soup.find(class_='DyNQfBip')  # 图片
                            text2 = soup.find(class_='tbZ6dkVE')  # 第二段文字

                            # 拼接评论内容
                            comment_text = ""
                            if text1 and img_tag and text2:
                                comment_text += '送出了 '  # 拼接第一段文字
                                image_url = f"{img_tag.get('src')}"
                                # for sublist in gift_list:
                                #     if sublist[1] in image_url:
                                #         comment_text += sublist[0]
                                #         break
                                comment_text += image_url
                                comment_text += text2.get_text(strip=True)  # 拼接第二段文字
                                # print('A:',comment_text)

                            # 如果没有图片，直接从 comment_element 获取文本
                            if not img_tag:
                                comment_text = comment_element.text.strip()

                            # 保存到 all_comments 中
                            self.all_comments.append((name_element.text.strip(), comment_text))

                        # 获取子元素的文本
                            # name_text = name_element.text.strip()
                            # comment_text = comment_element.text.strip()
                            #
                            # self.all_comments.append((name_text, comment_text))

                        except StaleElementReferenceException:
                            # 元素失效时跳过
                            print('A索引失败，情况一')
                            continue

                    result = self.check_new_barrage()
                    self.last_comments = self.all_comments
                    return result
            except Exception as e:
                print(f"A无法找到子元素: {e}")
                # print('抓取失败，情况二')
                pass
        # else:
        #     print('退出1')
        #     self.browers.quit()

    def check_new_barrage(self): # 新旧弹幕筛选算法
        if self.all_comments == self.last_comments:
            # print(0)
            return []
        elif len(self.all_comments) < self.max_num - 1 and len(self.last_comments) < self.max_num:
            # print(3)
            # print(self.last_comments)
            # print(self.all_comments)
            # print(self.all_comments[len(self.last_comments):],len(self.last_comments))
            return self.all_comments[len(self.last_comments):]
        else:
            for i in range(1, len(self.all_comments)):
                old_sublist = self.last_comments[i:]
                new_sublist = self.all_comments[:len(old_sublist)]

                if old_sublist == new_sublist and len(self.last_comments)!=0:
                    # print(1)
                    # print(self.last_comments)
                    # print(self.all_comments,i)
                    # print(self.all_comments[len(self.last_comments) - i:])
                    return self.all_comments[len(self.last_comments) - i:]
            # print(2)
            # print(self.last_comments)
            # print(self.all_comments)
            return self.all_comments

    def print_last_name(self):
        if self.WorkFlag:
            try:
                self.B = time.time()
                if self.B - self.A > 300:
                    self.browers.refresh()
                    self.A = time.time()
                    # print('已刷新')

                elements = self.browers.find_elements(By.CLASS_NAME, 'TNg5meqw')
                if elements:
                    # 只抓取最后一个元素
                    speice = elements[-1]

                    try:
                        name_element = speice.find_element(By.CLASS_NAME, 'u2QdU6ht')
                        comment_element = speice.find_element(By.CLASS_NAME, 'WsJsvMP9')

                        # 获取 comment_element 的完整 HTML 内容
                        comment_html = comment_element.get_attribute("innerHTML")

                        # 使用 BeautifulSoup 解析 HTML
                        soup = BeautifulSoup(comment_html, 'html.parser')

                        # 提取各部分内容
                        text1 = soup.find(class_='hH0pxiDh')  # 第一段文字
                        img_tag = soup.find(class_='DyNQfBip')  # 图片
                        text2 = soup.find(class_='tbZ6dkVE')  # 第二段文字

                        # 拼接评论内容
                        comment_text = ""
                        if text1 and img_tag and text2:
                            comment_text += '送出了 '  # 拼接第一段文字
                            image_url = f"{img_tag.get('src')}"
                            # for sublist in gift_list:
                            #     if sublist[1] in image_url:
                            #         comment_text += sublist[0]
                            #         break
                            comment_text += image_url
                            comment_text += text2.get_text(strip=True)  # 拼接第二段文字
                            # print(comment_text)

                        # 如果没有图片，直接从 comment_element 获取文本
                        if not img_tag:
                            comment_text = comment_element.text.strip()

                        # 查找子元素
                        # name_element = speice.find_element(By.CLASS_NAME, 'u2QdU6ht')
                        # comment_element = speice.find_element(By.CLASS_NAME, 'WsJsvMP9')
                        #
                        # # 获取子元素的文本
                        # name_text = name_element.text.strip()
                        # comment_text = comment_element.text.strip()

                        # # 将抓取到的评论添加到列表中
                        self.speice_comments = (name_element.text.strip(), comment_text)

                        # print(self.speice_comments)

                    except StaleElementReferenceException:
                        # 元素失效时跳过
                        print('B索引失败，情况一')
                        return False  # 如果抓取失败，则返回 None

                    if self.speice_comments != self.last_speice_comments:
                        # print(4)
                        # print('last:',self.last_speice_comments)
                        # print('now:',self.speice_comments)
                        self.last_speice_comments = self.speice_comments
                        return self.last_speice_comments
                    else:
                        return False

            except Exception as e:
                print(f"B无法找到子元素: {e}")
                # print('抓取失败，情况二')
                return False

        else:
            try:
                if len(self.browers.window_handles):
                    # print('退出成功')
                    self.browers.quit()
            except Exception as e:
                print('退出错误：',e)


# if __name__=='__main__':
#     bc = BarrageCatcher()
#     bc.get_room()
#     bc.print_name()
