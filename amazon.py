import bs4
from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException,WebDriverException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from get_proxies import proxies
from random_user_agent.params import SoftwareName,OperatingSystem
from random_user_agent.user_agent import UserAgent
import random
import asyncio
import aiohttp
import requests


prox = proxies()
this = prox.get_()
# print(this)

class amaze():

    def __init__(self,url:str,**kwargs) -> None:
        self.url = url
        self.pages = kwargs.get('pages','1')
        self.description = kwargs.get('description','yes')
        self.proxies_this = this
        self.ua = ''
        self.data = ''

    def parse_page(self):
        software_names = [SoftwareName.CHROME.value]
        operatingSys = [OperatingSystem.LINUX.value,OperatingSystem.WINDOWS.value]
        ua_rotator = UserAgent(software_names=software_names,
                               operating_systems=operatingSys,
                               limit=100)
        user_agent = ua_rotator.get_random_user_agent()
        self.ua = user_agent
        proxy_this = random.choice(self.proxies_this)
        print(self.ua,proxy_this)

        headers = {
            "User-Agent": self.ua,
            "Accept-Encoding": "gzip, deflate",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "DNT": "1",
            "Connection": "close",
            "Upgrade-Insecure-Requests": "1"
        }

        resp = requests.get(url=self.url,timeout=100,headers=headers)
        with open("file.html", 'w+',encoding='utf-8') as data:
            data.write(f"{resp.text}")
        self.data = resp.text

    async def scrape_others(self):
        pass

    def read_product_link(self):
        with open('file.html','r') as fp:
            data = fp.read()
        # data = self.data
        soup = bs4.BeautifulSoup(data,'html.parser')
        all_links = soup.findAll('div',attrs={'data-cy':'title-recipe'})
        h2 = [x.find('h2') for x in all_links]
        links = [x.find('a')['href'] for x in h2 if x.find('a') and 'href' in x.find('a').attrs]
        print(links)
        with open("links.html",'w') as fp:
            fp.write(str(links))
        self.product_links = links
    
    def pages(self):
        pass
    
a = amaze("https://www.amazon.com/s?k=books+best+sellers&crid=2XGYE984X8E7E&sprefix=books+best%2Caps%2C275&ref=nb_sb_ss_ts-doa-p_2_10")
# a.parse_page()
a.read_product_link()