import undetected_chromedriver as uc
import time
from get_proxies import proxies
import random
import requests
import os
import json
import datetime
from selenium import webdriver
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException,WebDriverException
from selenium.webdriver.remote.webelement import WebElement
# from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import Proxy,ProxyType
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

# from fake_useragent import UserAgent


def generate_proxy():
    check = os.path.exists('proxies.json')
    print(check)
    if check:
        ts = os.path.getmtime('proxies.json')
        last_modified = datetime.datetime.fromtimestamp(ts)
        print(last_modified)
        # last_modified = datetime.datetime.strptime(last_modified,'%d-%b-%Y %H:%M:%S')
        now = datetime.datetime.now()
        print(now)
        if now-last_modified >= datetime.timedelta(hours=1):
            print('in if now-last_modified')
            proxy_list = proxies()
            fetch_proxies = proxy_list.genocode()
            if fetch_proxies:
                # alive_proxies = proxy_list.check_proxy_alive()
                alive_proxies = fetch_proxies
                print(alive_proxies)
                prox_file = {
                    'proxies':
                        alive_proxies
                }
                with open('proxies.json','w') as file:
                    json.dump(prox_file,file)
                    return alive_proxies
            else:
                return False
        else:
            with open('proxies.json','r') as file:
                proxy_list = json.load(file)
                return proxy_list['proxies']
    else:
        proxy_list = proxies()
        fetch_proxies = proxy_list.genocode()
        if fetch_proxies:
            # alive_proxies = proxy_list.check_proxy_alive()
            alive_proxies = fetch_proxies
            print(alive_proxies)
            prox_file = {
                'proxies':
                    alive_proxies
            }
            with open('proxies.json','w') as file:
                json.dump(prox_file,file)
                return alive_proxies
        else:
            return False
    
def random_sleep():
    rand = random.randrange(1,30)
    print(f"sleeping for {rand} secs")
    time.sleep(rand)

def random_long_sleep():
    rand = random.randrange(30,100)
    print(f"sleeping for {rand} secs")
    time.sleep(rand)

def random_short_sleep():
    rand = random.randrange(1,5)
    print(f"sleeping for {rand} secs")
    time.sleep(rand)

def random_reverse_scroller(*args):
    rand = random.randrange(150,700)



# proxy = random.choice(proxy)
generated_proxies = generate_proxy()
print(generated_proxies)

class Req():
    
    def __init__(self,url) -> None:
        self.url = url
        self.retries = 0
        self.driver = ''
        self.sc_down = 0
        self.sc_up = 0

    def overlay_proxy(self):
        software_names = [SoftwareName.CHROME.value]
        operatingSys = [OperatingSystem.LINUX.value,OperatingSystem.WINDOWS.value]
        ua_rotator = UserAgent(software_names=software_names,
                               operating_systems=operatingSys,
                               limit=100)
        user_agent = ua_rotator.get_random_user_agent()
        chrome_opts = uc.ChromeOptions()
        # chrome_opts.add_argument('--headless')
        PROXY = random.choice(generated_proxies)
        print(PROXY)
        chrome_opts.add_argument('--no-sandbox')
        chrome_opts.add_argument('--window-size=1420,1080')
        chrome_opts.add_argument('--disable-features=WebRTC')
        chrome_opts.add_argument('--disable-gpu')
        chrome_opts.add_argument(f'user-agent={user_agent}')
        chrome_opts.add_argument(f'--proxy-server={PROXY}')
        # prox = Proxy()
        # prox.proxy_type = ProxyType.MANUAL
        # prox.auto_detect = False
        # capalilities = webdriver.DesiredCapabilities.CHROME
        # prox.http_proxy = PROXY
        # prox.add_to_capabilities(capalilities)
        self.driver = uc.Chrome(options=chrome_opts)
        self.driver.get(self.url)
        # time.sleep(100)
        WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.TAG_NAME,'pre')))
        element = self.driver.find_element(By.TAG_NAME,'pre')
        element_text = element.text.split()
        print(element_text)
        if element.text.find('country') > 0:
            self.driver.delete_all_cookies()
            self.driver.quit()
            return True,self.retries
        else:
            self.driver.delete_all_cookies()
            self.driver.quit()
            return False,self.retries
        
    def type_like_human(self,element:WebElement,text,delay=0.1):
        try:
            for i in text:
                element.send_keys(i)
                time.sleep(random.uniform(delay, delay + 0.2))
            return True
        except Exception as err:
            print(err)
            return False

    def pause_before_click(self,element:WebElement):
        try:

            random_sleep()
            WebDriverWait(self.driver,100).until(EC.element_to_be_clickable((element)))
            element.click()
            return True
        
        except Exception as err:
            print(err)
            return False

    def scroll_down_random(self):
        """Scrolls down by a random number of pixels."""
        try:
            scroll_amount = random.randint(200, 600)  # Choose a random amount to scroll down
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            print(f"Scrolled down {scroll_amount} pixels")
            random_short_sleep()
            return True

        except Exception as err:
            print(f"Error scrolling down: {err}")
            return False
        
    def scroll_up_random(self):
        """Scrolls up by a random number of pixels, but only if scrolled down already."""
        try:
            scroll_amount = random.randint(100, 600)  # Choose a random amount to scroll up
            current_scroll = self.driver.execute_script("return window.pageYOffset;")
            scroll_up_amount = min(scroll_amount, current_scroll)  # Ensure not scrolling past the top

            if current_scroll > 0:
                self.driver.execute_script(f"window.scrollBy(0, -{scroll_up_amount});")
                random_short_sleep()
                print(f"Scrolled up {scroll_up_amount} pixels")
                return True
            else:
                print("Already at the top of the page or unable to scroll up")
                return True
        
        except Exception as err:
            print(f"Error scrolling up: {err}")
            return False
        
    def scroll_to_bottom(self):
        """
        Scrolls to the bottom of the page to ensure all content is loaded.
        """
        try:
            last_height = self.driver.execute_script("return document.body.scrollHeight")

            while True:
        
                # Scroll down to the bottom of the page
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                
                # Wait for new content to load
                random_short_sleep()

                # Calculate new scroll height and compare with last scroll height
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                random_short_sleep()

            print("Scrolled to the bottom of the page")
            return True

        except Exception as err:
            print(f"Error scrolling to bottom: {err}")
            return False
        
    def no_proxy(self):
        self.driver = uc.Chrome()
        self.driver.get(self.url)
        random_sleep()

    def login(self):

        email = 'xxxx@email.com'
        passw = 'xxxxxxx'
        WebDriverWait(self.driver,100).until(EC.visibility_of_element_located((By.ID,'email')))
        email_element= self.driver.find_element(By.ID,'email')
        self.type_like_human(email_element,email)
        random_sleep()

        WebDriverWait(self.driver,100).until(EC.visibility_of_element_located((By.ID,'pass')))
        passw_element = self.driver.find_element(By.ID,'pass')
        self.type_like_human(passw_element,passw)

        login_btn = self.driver.find_element(By.XPATH,'//*[@name="login"]')
        self.pause_before_click(login_btn)
        random_long_sleep()

        alert = WebDriverWait(self.driver, 10).until(EC.alert_is_present())
        alert.dismiss()

        self.scroll_down_random()
        
        random_sleep()

        self.scroll_down_random()
        random_sleep()
        self.scroll_down_random()

        random_sleep()

        self.scroll_up_random()

        # driver.delete_all_cookies()
    
    def scroll_element_into_view(self,element):
        """Scrolls the given element into view."""
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)

        return True


    def go_to_groups(self,group_name,text):
        # to click on the element Group found
        random_sleep()
        WebDriverWait(self.driver,100).until(EC.visibility_of_element_located((By.XPATH,"//a[@aria-label='Groups']")))
        goto_groups = self.driver.find_element(By.XPATH,"//a[@aria-label='Groups']")
        self.pause_before_click(goto_groups)

        self.scroll_down_random()
        random_short_sleep()

        self.scroll_down_random()
        random_short_sleep()
        self.scroll_down_random()
        random_short_sleep()
        self.scroll_down_random()

        # to click on the element(See all) found
        random_long_sleep()
        WebDriverWait(self.driver,100).until(EC.visibility_of_element_located((By.XPATH,"//a[@aria-label='See all']")))
        self.scroll_down_random()
        self.scroll_up_random()
        random_sleep()
        see_all = self.driver.find_element(By.XPATH,"//a[@aria-label='See all']")
        self.pause_before_click(see_all)

        # to click on the element(View group) found
        WebDriverWait(self.driver,100).until(EC.visibility_of_element_located((By.XPATH,"//a[@aria-label='See all']")))
        self.scroll_to_bottom()
        random_sleep()
        self.scroll_up_random()
        self.scroll_to_bottom()
        random_sleep()
        find_all_groups = self.driver.find_elements(By.XPATH,"/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[2]/div/div/div/div/div/div/div/div/div/div[3]/div")
        
        for element in find_all_groups:
        # Find the inner text of the group
            group_name_element = element.find_element(By.CSS_SELECTOR, "a[role='link']")
            group_name = group_name_element.text
        # Check if the text matches the specific group name
            if group_name == group_name:
                random_sleep()
                # Find and click the "View group" button within the current element
                view_group_button = element.find_element(By.CSS_SELECTOR, "a[aria-label='View group']")
                self.scroll_element_into_view(view_group_button)
                random_short_sleep()
                WebDriverWait(self.driver,100).until(EC.element_to_be_clickable,((view_group_button)))
                self.pause_before_click(view_group_button)
                print(f"Clicked on the group: {group_name}")
                break  # Exit loop once the desired group is found
    
                # view_group = self.driver.find_element(By.XPATH,"//a[@aria-label='View group']")


        # to click on the element(Create a post) found
        WebDriverWait(self.driver,100).until(EC.visibility_of_element_located((By.XPATH,"//div[@role='button']//span[contains(text(), 'Write something')]")))
        element = self.driver.find_element(By.XPATH, "//div[@role='button']//span[contains(text(), 'Write something')]")
        self.scroll_down_random()
        self.scroll_down_random()
        self.scroll_up_random()
        self.scroll_down_random()

        random_sleep()

        self.scroll_element_into_view(element)
        WebDriverWait(self.driver,100).until(EC.element_to_be_clickable((By.XPATH,"//div[@role='button']//span[contains(text(), 'Write something')]")))
        self.pause_before_click(element)


        # to type content in input field
        WebDriverWait(self.driver,100).until(EC.visibility_of_element_located((By.XPATH,"//div[@role='presentation']//div[contains(text(), 'Create a')]")))
        WebDriverWait(self.driver,100).until(EC.element_to_be_clickable((By.XPATH,"//div[@role='presentation']//div[contains(text(), 'Create a')]")))
        input_field = self.driver.find_element(By.XPATH,"//div[@role='presentation']//div[contains(text(), 'Create a')]")
        random_short_sleep()
        self.pause_before_click(input_field)
        self.type_like_human(input_field,text)
        random_long_sleep()


        # to click on the back button element found
        WebDriverWait(self.driver,100).until(EC.visibility_of_element_located((By.XPATH,"//div[@aria-label='Submit']")))
        random_sleep()
        WebDriverWait(self.driver,100).until(EC.element_to_be_clickable((By.XPATH,"//div[@aria-label='Submit']")))
        submit_btn = self.driver.find_element(By.XPATH,"//div[@aria-label='Submit']")
        self.pause_before_click(submit_btn)
        random_sleep()
        self.scroll_down_random()
        self.scroll_down_random()
        self.scroll_up_random()
        random_sleep()
        self.driver.quit()
        self.driver.delete_all_cookies()
        return True
    

facebook = Req('https://www.facebook.com')
facebook.no_proxy()
facebook.login()
facebook.go_to_groups("testgroup","Hi! this is my first post in a long long time!!!")

# this = Req('http://lumtest.com/myip.json')
# status = this.overlay_proxy()
# print(status)
# retries = 1
# while not status:
#     status = this.overlay_proxy(retries)
#     retries+=status[1]
#     if status[0]:
#         print('DOne')
#         break
#     else:
#         continue



# ua = UserAgent()
# custom_agent = ua.chrome
# options = uc.ChromeOptions()
# options.add_argument('--headless')  # Use headless mode
# options.add_argument('--disable-gpu')  # Disable GPU hardware acceleration
# options.add_argument(f'user-agent={custom_agent}')
# options.add_argument('--window-size=1024,768')
# if proxy:
#     print(proxy)
#     options.add_argument(f'--proxy-server={proxy}')
# else:
#     pass

# driver = uc.Chrome(options=options)


