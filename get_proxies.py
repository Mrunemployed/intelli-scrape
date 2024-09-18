import requests
import json
from concurrent.futures import ThreadPoolExecutor
import bs4
import pandas as pd
import undetected_chromedriver as uc
import time
from selenium.webdriver.common.by import By
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName,OperatingSystem

class proxies():

    def __init__(self) -> None:
        # self.url = url
        self.proxies = []
        self.working_proxies = []

    def fetch(self):
        url = "https://api.proxyscrape.com/v3/free-proxy-list/get?request=getproxies&skip=0&proxy_format=protocolipport&format=json&limit=40"
        resp = requests.get(url=url)
        if resp.status_code == 200:
            proxy_list = resp.json()
            for i in proxy_list['proxies']:
                if i['alive'] and i['protocol'] in {'http','https'}:
                    self.proxies.append(i['proxy'])
            return self.proxies
        else:
            return False
        
    def fetch_nova(self):
        try:
            url = 'https://www.proxynova.com/proxy-server-list/'
            driver = uc.Chrome()
            driver.get(url)
            time.sleep(5)
            table = driver.find_element(By.TAG_NAME,'table')
            table_contents = table.get_attribute('outerHTML')
            print(table_contents)
            # driver.quit()
            soup = bs4.BeautifulSoup(table_contents,'html.parser')
            table = soup.find('table')
            df = pd.read_html(str(table))[0]
            # print(df)
            # df.to_csv('proxies.csv')
            df = df[['Proxy IP','Proxy Port','Anonymity']]
            df = df.dropna()
            drop_these = ['Transparent']
            df = df[~df.isin(drop_these).any(axis=1)]
            df['Proxy IP'] = df['Proxy IP'].apply(lambda row: str(row).split(')')[::-1][0].strip('"'))
            df['Proxy Port'] = df['Proxy Port'].apply(lambda row: int(row))
            # print(df.columns)
            df.loc[:,'proxy'] = df.apply(lambda row: f"http://{row['Proxy IP']}:{row['Proxy Port']}",axis=1)
            # print(df['proxy'])
            # return df['proxy'].to_list()
            self.proxies = df['proxy'].to_list()
            return self.proxies
        except Exception as err:
            print(err)
            return False
        finally:
            driver.quit()
            # self.

    def genocode(self):
        url = "https://proxylist.geonode.com/api/proxy-list?anonymityLevel=elite&protocols=http%2Chttps&limit=500&page=1&sort_by=speed&sort_type=asc"
        reqs = requests.get(url=url)
        if reqs.status_code == 200:
            resp = reqs.json()
            with open('proxies-metadata.json','w') as fp:
                json.dump(resp,fp,indent=4)
            data = resp
            proxy_list = []
            for i in data['data']:
                proxy = f"{i['protocols'][0]}://{i['ip']}:{i['port']}/"
                proxy_list.append(proxy)
            self.proxies = proxy_list
            return proxy_list
        else:
            return False




    def req_prox(self,prox):
        import random

        rsleep = random.randrange(1,3)
        time.sleep(rsleep)

        software_names = [SoftwareName.CHROME.value]
        operatingSys = [OperatingSystem.LINUX.value,OperatingSystem.WINDOWS.value]
        ua_rotator = UserAgent(software_names=software_names,
                               operating_systems=operatingSys,
                               limit=100)
        user_agent = ua_rotator.get_random_user_agent()
        url = 'http://lumtest.com/myip.json'
        proxy = {
            "http": prox
        }
        try:

            resp = requests.get(url,proxies=proxy,timeout=10)
            if resp.status_code == 200:
                print(resp)
                return prox,True
            else:
                return prox,False
        except TimeoutError:
           print("Timed out")
           return prox,False
        except Exception:
            print("failed to connect")
            return prox,False
    
    def refresh_list(self):
        import os
        import datetime

        check = os.path.exists('proxies.json')
        print(check)
        if not check:
            ts = os.path.getmtime('proxies.json')
            last_modified = datetime.datetime.fromtimestamp(ts)
            print(last_modified)
            # last_modified = datetime.datetime.strptime(last_modified,'%d-%b-%Y %H:%M:%S')
            now = datetime.datetime.now()
            print(now)
            if now-last_modified >= datetime.timedelta(hours=1):
                # print('in if now-last_modified')
                return True
            else:
                return False
        else:
            return True
        
    
    def read_cache_proxies(self,rw):
        if rw == 'read':
                
            with open('proxies.json','r') as fp:
                proxy_list = json.load(fp)
            return proxy_list
        
        elif rw == 'write':
            with open('proxies.json','w') as fp:
                prox_file = {
                        'proxies':
                            self.working_proxies
                }
                json.dump(prox_file,fp,indent=4)
            return prox_file
        else:
            print('incorrect kwargs')

    def check_proxy_alive(self):
        try:
            if self.refresh_list():

                return self.read_cache_proxies('read')
            else:
                    
                with ThreadPoolExecutor(max_workers=15) as threads:
                    fu = threads.map(self.req_prox,self.proxies)
                for prox,is_alive in fu:
                    print(prox,is_alive)
                    if is_alive:
                        self.working_proxies.append(prox)
                print(self.working_proxies)
                return self.read_cache_proxies('write')
        except Exception as err:
            return False
        
    def get_(self,**kwargs):
        host = kwargs.get('host','genocode')
        if host == 'genocode':
            proxy_list = self.genocode()
        else:
            pass
        if proxy_list:
            alive = self.check_proxy_alive()
            if alive:
                return proxy_list
            else:
                return False
        else:
            return False
