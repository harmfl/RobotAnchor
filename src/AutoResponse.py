from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys  # 按键
import time
import json

class AutoResponse:
    def __init__(self,screen_x, screen_y):
        # 初始化非无头模式浏览器
        self.options = webdriver.EdgeOptions()
        self.options.add_experimental_option("excludeSwitches", ['enable-automation', 'enable-logging'])
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--ignore-ssl-errors')
        self.browers = webdriver.Edge(options=self.options)
        self.wait = WebDriverWait(self.browers, 3600)
        self.url_login = 'https://anchor.douyin.com/anchor/dashboard?from=blcenter'

        self.login_success = False
        self.headless_working = False
        self.name_text = False

        self.screen_x = screen_x
        self.screen_y = screen_y

        self.cookies = [{"domain": ".douyin.com", "expiry": 1768124734, "httpOnly": True, "name": "xgplayer_user_id", "path": "/", "sameSite": "Lax", "secure": True, "value": "102642846555"}, {"domain": "anchor.douyin.com", "expiry": 1768124734, "httpOnly": False, "name": "xgplayer_device_id", "path": "/", "sameSite": "Lax", "secure": False, "value": "51112476798"}, {"domain": ".douyin.com", "expiry": 1741772732, "httpOnly": True, "name": "ssid_ucp_v1", "path": "/", "sameSite": "None", "secure": True, "value": "1.0.0-KDE3YzAwMDk0ODQxOTVhYWM4YmQzZjMzY2I3N2FlNjU4NWIxMGFlOTEKGAjagMmv5QIQu_uIvAYY0pMdIAw4BkD0BxoCbHEiIGQ2OGMwMzBhNzJjNDQ0OWI0NzkzOTg1ZjkzNDYxZDYx"}, {"domain": ".douyin.com", "expiry": 1741772732, "httpOnly": True, "name": "sid_ucp_v1", "path": "/", "sameSite": "Lax", "secure": True, "value": "1.0.0-KDE3YzAwMDk0ODQxOTVhYWM4YmQzZjMzY2I3N2FlNjU4NWIxMGFlOTEKGAjagMmv5QIQu_uIvAYY0pMdIAw4BkD0BxoCbHEiIGQ2OGMwMzBhNzJjNDQ0OWI0NzkzOTg1ZjkzNDYxZDYx"}, {"domain": ".douyin.com", "expiry": 1741772732, "httpOnly": True, "name": "sessionid", "path": "/", "sameSite": "Lax", "secure": True, "value": "d68c030a72c4449b4793985f93461d61"}, {"domain": ".douyin.com", "expiry": 1741772732, "httpOnly": True, "name": "is_staff_user", "path": "/", "sameSite": "Lax", "secure": True, "value": "False"}, {"domain": ".douyin.com", "expiry": 1741772732, "httpOnly": True, "name": "sid_tt", "path": "/", "sameSite": "Lax", "secure": True, "value": "d68c030a72c4449b4793985f93461d61"}, {"domain": ".douyin.com", "expiry": 1739180731, "httpOnly": True, "name": "passport_auth_status", "path": "/", "sameSite": "Lax", "secure": False, "value": "6682c1dcce0a2a82ada39d933603bca7%2C"}, {"domain": ".douyin.com", "expiry": 1741772731, "httpOnly": True, "name": "sid_ucp_sso_v1", "path": "/", "sameSite": "Lax", "secure": True, "value": "1.0.0-KDQwNDhhNzhlMTNkNmZlNDdkMjYyYmIxMzQxYWUwMjdhNTZkM2IwNzkKHgjagMmv5QIQuvuIvAYY0pMdIAww56rW1QU4BkD0BxoCbGYiIGQwNDkyODc0MmEwNTg5MjQ5ZGZlOGQwMGI3MmRmNzA1"}, {"domain": ".douyin.com", "expiry": 1739180731, "httpOnly": True, "name": "passport_auth_status_ss", "path": "/", "sameSite": "None", "secure": True, "value": "6682c1dcce0a2a82ada39d933603bca7%2C"}, {"domain": ".douyin.com", "expiry": 1741772732, "httpOnly": True, "name": "uid_tt", "path": "/", "sameSite": "Lax", "secure": True, "value": "08abe89e8203b4c1c1565f9b1505ac7c"}, {"domain": ".douyin.com", "expiry": 1768124731, "httpOnly": True, "name": "odin_tt", "path": "/", "sameSite": "Lax", "secure": False, "value": "7b5b4db3f84add1b15df516b342577d06ed3c577a876e3819c61e618de3c3db9cb0e72f6010c8221dbff52eb2f2b29f96efb51f93ee3ad8bf3b8936d9c5b8efa"}, {"domain": ".douyin.com", "expiry": 1741772731, "httpOnly": True, "name": "ssid_ucp_sso_v1", "path": "/", "sameSite": "None", "secure": True, "value": "1.0.0-KDQwNDhhNzhlMTNkNmZlNDdkMjYyYmIxMzQxYWUwMjdhNTZkM2IwNzkKHgjagMmv5QIQuvuIvAYY0pMdIAww56rW1QU4BkD0BxoCbGYiIGQwNDkyODc0MmEwNTg5MjQ5ZGZlOGQwMGI3MmRmNzA1"}, {"domain": "anchor.douyin.com", "httpOnly": False, "name": "x-web-secsdk-uid", "path": "/", "sameSite": "Lax", "secure": False, "value": "c4adee37-c3ca-4b29-8b81-86fbddf0c9bc"}, {"domain": ".douyin.com", "expiry": 1741772731, "httpOnly": True, "name": "sso_uid_tt_ss", "path": "/", "sameSite": "None", "secure": True, "value": "de1c0f1dba2b4c00bcecacb51e88923a"}, {"domain": ".douyin.com", "expiry": 1741772614, "httpOnly": False, "name": "passport_csrf_token", "path": "/", "sameSite": "None", "secure": True, "value": "ac6e3a03878d4bdac4a68c213f3309ca"}, {"domain": ".douyin.com", "expiry": 1767692731, "httpOnly": True, "name": "sid_guard", "path": "/", "sameSite": "Lax", "secure": True, "value": "d68c030a72c4449b4793985f93461d61%7C1736588731%7C5184001%7CWed%2C+12-Mar-2025+09%3A45%3A32+GMT"}, {"domain": ".douyin.com", "expiry": 1741772731, "httpOnly": True, "name": "sso_uid_tt", "path": "/", "sameSite": "Lax", "secure": True, "value": "de1c0f1dba2b4c00bcecacb51e88923a"}, {"domain": ".douyin.com", "expiry": 1768124730, "httpOnly": True, "name": "d_ticket", "path": "/", "sameSite": "Lax", "secure": False, "value": "0754c74216faafe40131b5dd540704bfe24e4"}, {"domain": ".douyin.com", "expiry": 1741772732, "httpOnly": True, "name": "uid_tt_ss", "path": "/", "sameSite": "None", "secure": True, "value": "08abe89e8203b4c1c1565f9b1505ac7c"}, {"domain": ".douyin.com", "expiry": 1771148731, "httpOnly": False, "name": "passport_assist_user", "path": "/", "sameSite": "Lax", "secure": True, "value": "Cjyp7Bj-fSqwg-hept-PNs1SyLbQm-rp_aJXILUgoZiXs4dMj_DnESoyyLKkCiN4r3TXNXvgHL_WBCRgEUMaSgo8RYt7VFp6i3rQlZzwpLOejTs36urKNKMpC2hSrVPiw6zscHxiJA7NEbwZZUf1yK8U3NFWyM3ZW-4xrqVxEJnG5g0Yia_WVCABIgEDcxVRWA%3D%3D"}, {"domain": ".douyin.com", "expiry": 1746956731, "httpOnly": True, "name": "n_mh", "path": "/", "sameSite": "Lax", "secure": False, "value": "9jvyGjMC4sjmzHvAtNW7AQlqAAPjbiWfbR7bH_90JOE"}, {"domain": ".douyin.com", "expiry": 1741772730, "httpOnly": True, "name": "passport_mfa_token", "path": "/", "sameSite": "Lax", "secure": True, "value": "CjVI7WTW53CM9Idyo0wPCO6v860S5263kR2ra9THGEmUD%2FoKt0p7py7Pe90pdrGQF2R9cH2hThpKCjwcIf3UVHsGKpSUZZRDXOh0B1H2IZSrux2P6wqUKZPZw%2BjbS7VUPseT7YKR0rSN1TeuQoI%2BpGQcbEseXxAQ8cXmDRj2sdFsIAIiAQPq7w50"}, {"domain": "anchor.douyin.com", "httpOnly": False, "name": "csrf_session_id", "path": "/", "sameSite": "None", "secure": True, "value": "ef75d1265bf94f163c3e5a691f1fb03f"}, {"domain": ".douyin.com", "expiry": 1767692733, "httpOnly": True, "name": "ttwid", "path": "/", "sameSite": "Lax", "secure": False, "value": "1%7CBDKxUTgR4e1ShF_E6_Y5kd2TiCpup6fS4-H2tsWLM2Y%7C1736588611%7C8a0345b73d9a05ea6ed05743d75b235d56266f6f40260e61d5461f58c8267c67"}, {"domain": "anchor.douyin.com", "expiry": 1736847811, "httpOnly": False, "name": "gfkadpd", "path": "/", "sameSite": "None", "secure": True, "value": "477650,32057"}, {"domain": ".douyin.com", "httpOnly": False, "name": "biz_trace_id", "path": "/", "sameSite": "Lax", "secure": False, "value": "d39eb19e"}, {"domain": ".douyin.com", "expiry": 1741772732, "httpOnly": True, "name": "sessionid_ss", "path": "/", "sameSite": "None", "secure": True, "value": "d68c030a72c4449b4793985f93461d61"}, {"domain": "anchor.douyin.com", "expiry": 1741772661, "httpOnly": False, "name": "s_v_web_id", "path": "/", "sameSite": "Lax", "secure": False, "value": "verify_m5s01v5g_rRxWwP5N_0XRN_4lVy_8r49_9DS8DrRSjZQ2"}, {"domain": ".douyin.com", "expiry": 1741772731, "httpOnly": True, "name": "toutiao_sso_user_ss", "path": "/", "sameSite": "None", "secure": True, "value": "d04928742a0589249dfe8d00b72df705"}, {"domain": ".douyin.com", "expiry": 1741772731, "httpOnly": True, "name": "toutiao_sso_user", "path": "/", "sameSite": "Lax", "secure": True, "value": "d04928742a0589249dfe8d00b72df705"}, {"domain": ".douyin.com", "expiry": 1741772614, "httpOnly": False, "name": "passport_csrf_token_default", "path": "/", "sameSite": "Lax", "secure": False, "value": "ac6e3a03878d4bdac4a68c213f3309ca"}]

    def wf_and_click(self, xpain):
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, xpain)))
            self.browers.find_element(By.XPATH, xpain).click()
        except Exception:
            print(
                '检测不到需要的页面元素，开始尝试刷新页面\n程序等待30秒后重新运行该函数，如果一直无法运行请联系开发人员')
            self.browers.get(self.url_login)
            time.sleep(30)
            self.wf_and_click(xpain)

    def login(self):
        self.browers.get(self.url_login)

        # for cookie in self.cookies:
        #     self.browers.add_cookie(cookie)
        # self.browers.refresh()

        # print("请手动完成登录并进行交互操作...")
        self.wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div[2]/div[2]/div')))
        print("正在切换到无头模式...")
        self.login_success = True
        self.switch_to_headless()
        # 继续自动化任务
        self.wf_and_click('/html/body/div[1]/div/div[1]/div[2]/div[2]/div')

    def switch_to_headless(self):
        # 获取当前浏览器的会话信息
        cookies = self.browers.get_cookies()
        print(cookies)
        current_url = self.browers.current_url

        # 关闭当前浏览器
        self.browers.quit()

        # 启动无头模式浏览器
        headless_options = webdriver.EdgeOptions()
        headless_options.add_experimental_option("excludeSwitches", ['enable-automation', 'enable-logging'])
        headless_options.add_argument('--disable-gpu')
        headless_options.add_argument('--ignore-certificate-errors')
        headless_options.add_argument('--ignore-ssl-errors')
        headless_options.add_argument('--headless')
        headless_options.add_argument(f"--window-size={self.screen_x},{self.screen_y}")  # 特殊情况需要调整
        headless_options.add_argument(
            "user-agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'")
        self.browers = webdriver.Edge(options=headless_options)
        self.wait = WebDriverWait(self.browers, 20)

        # 加载之前的会话状态
        self.browers.get(current_url)
        for cookie in cookies:
            self.browers.add_cookie(cookie)
        self.browers.refresh()
        print("成功切换到无头模式！")
        self.headless_working = True
        self.wait.until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div[3]/div/div[1]')))
        name = self.browers.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div[3]/div/div[1]')
        self.name_text = name.text.strip()
        # print(self.name_text)
        # while self.WorkFlag: # 维持浏览器
        #     time.sleep(1)
        # self.browers.quit()

    def send_bulletin(self,text):
        self.wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div[2]/div[2]/div/div[3]/div[2]/input')))
        text_input = self.browers.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/div[2]/div/div[3]/div[2]/input')
        text_input.send_keys(text)
        text_input.send_keys(Keys.ENTER)
        print(f'发送成功：{text}')


# if __name__ == "__main__":
#     automation = AutoResponse()
#     automation.login()
#     automation.send_bulletin('欢迎大家！')
