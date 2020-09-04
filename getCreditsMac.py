from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import re
from analyze import analyze
from configparser import ConfigParser
#https://www.k-hitorigoto.online/entry/2017/03/09/223538

#===== config =====#
ini = ConfigParser()
ini.read('config.ini')
config=ini['config']
username = config['username']
password = config['password']

#===== prepare data =====#
driver = webdriver.Chrome('./chromedriver')
driver.get('https://www2.adst.keio.ac.jp/rcs/login')

from time import sleep
sleep(1)

usr = driver.find_element_by_id('username')
pwd = driver.find_element_by_id('password')

usr.send_keys(username)
pwd.send_keys(password)
pwd.send_keys(Keys.RETURN)

elem = driver.find_element_by_id('RCS101EfId')
elem.send_keys(username)
elem = driver.find_element_by_id('RCS101EfPwd')
elem.send_keys(password)
elem.send_keys(Keys.RETURN)

table = driver.find_element_by_class_name('main')
trs = table.find_elements_by_tag_name('tr')

seiseki = []

for i in trs:
    seiseki.append(i.text)

#===== prepare variables =====#
### 変数を用意 ###
sum = 0
credits = []

### 3,4年生の進級条件 ###
sannen=0# 3年次取得単位
yonen=0# 4年次取得単位

for j in seiseki:
    if len(j)>1:
        if j.startswith('分野'):
            index = j.find('取得合計')
            if index>0:
                num = int(int(re.sub("\\D", "", str(j[index:])))/10)
                sum += num
                credits.append([j[3:11], num])
                #print('分野', j[3:11], 'を', num, '単位')#for debug

    else:
        if j[0].startswith('分野'):
            index = j[0].find('取得合計')
            if index>0:
                num = int(int(re.sub("\\D", "", str(j[0][index:])))/10)
                sum += num
                credits.append([j[0][3:11], num])
                #print('分野', j[0][3:11], 'を', num, '単位')#for debug

for j in seiseki:
    if j[-2:]=="3年":
        hoge=j.split(" ")# 最初からこれやった方がいいな？
        if not ((hoge[-7].startswith("Ｄ") or hoge[-7].startswith("Ｆ")) or hoge[-7].startswith("？")):# DとFが落単
            sannen+=int(float(hoge[-6]))
        elif not ((hoge[-7].startswith("Ｄ") or hoge[-7].startswith("Ｆ")) or hoge[-7].startswith("？")):
            yonen+=int(float(hoge[-6]))
    elif j[-2:]=="4年":
        hoge=j.split(" ")
        if not ((hoge[-7].startswith("Ｄ") or hoge[-7].startswith("Ｆ")) or hoge[-7].startswith("？")):
            yonen+=int(float(hoge[-6]))
        elif not ((hoge[-7].startswith("Ｄ") or hoge[-7].startswith("Ｆ")) or hoge[-7].startswith("？")):
            sannen+=int(float(hoge[-6]))


analyze(credits,sum, sannen, yonen)
