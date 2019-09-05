from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import re
from configparser import ConfigParser

#===== config =====#
ini = ConfigParser()
ini.read('config.ini')
config=ini['config']
username = config['username']
password = config['password']

#===== prepare data =====#
driver = webdriver.Chrome('./chromedriver')
driver.get('https://www2.adst.keio.ac.jp/rcs/login')

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
trs = table.find_elements_by_tag_name("tr")

seiseki = []

for i in trs:
    seiseki.append(i.text)

#===== prepare variables =====#
### 変数を用意 ###
sum = 0
credits = []
graduate = True

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
            sannen+=int(float(hoge[-6]))
        elif not ((hoge[-7].startswith("Ｄ") or hoge[-7].startswith("Ｆ")) or hoge[-7].startswith("？")):
            yonen+=int(float(hoge[-6]))





#===== 取得単位の分類 =====#
### 分類の用意 ###
#- 総合教育科目 -#
pankyo1=0
pankyo2=0
pankyo3=0
#- 基礎教育科目 -#
kiso=0
#- 外国語科目 -#
gogaku=0
#- 専門教育科目 -#
senmon=0
senmon_kiso=0
sentaku=0
kihon=0
bunya={"A":0,"B":0,"C":0,"D":0,"E":0,"F":0,"G":0,"H":0,"I":0,"J":0}
kanren=0
#- 卒業認定単位 -#
nintei=0
#- 自主選択科目 -#
jishu3=0#体育の3単位までの枠と2単位までの枠
jishu2=0#合計で4単位まで
#- 自由科目 -#
free=0
#- 必修科目 -#
hisshu={"macro1":False,"macro2":False,"toukei1":False,"toukei2":False,
        "bisekiORgairon":False,"senkeiORshiten":False,
        "micro1":False,"micro2":False,"zaishi1":False,"zaishi2":False,}

for i in credits:
    ### 般教 ###
    if i[0].startswith('10-21-'):#般教1系
        pankyo1+=i[1]
    elif i[0].startswith('10-22-'):#般教2系
        pankyo2+=i[1]
    elif i[0].startswith('10-23-'):#般教3系
        pankyo3+=i[1]

    ### 基礎教育科目 ###
    elif i[0].startswith('20-10-01'):#統計1
        if i[1]==0:
            print('統計1未取得卒業不可')
            graduate=False
        else:
            hisshu['toukei1']=True
            kiso+=i[1]
    elif i[0].startswith('20-10-02'):#統計2
        if i[1]==0:
            print('統計2未取得卒業不可')
            graduate=False
        else:
            hisshu['toukei2']=True
            kiso+=i[1]
    elif i[0].startswith('20-11-01'):#微積
            hisshu['bisekiORgairon']=True
            kiso+=i[1]
    elif i[0].startswith('20-11-02'):#線形
            hisshu['senkeiORshiten']=True
            kiso+=i[1]
    elif i[0].startswith('20-12-01'):#日本経済概論
            hisshu['bisekiORgairon']=True
            kiso+=i[1]
    elif i[0].startswith('20-12-02'):#歴史的経済分析の視点
            hisshu['senkeiORshiten']=True
            kiso+=i[1]
    elif i[0].startswith('20-3'):#その他の基礎教育科目 ex.)情報処理,微積入門etc
        kiso+=i[1]

    ### 外国語科目 ###
    elif i[0].startswith('30-10-01'):#study skills
        if i[1]==0:
            print('study skill未取得卒業不可')
            graduate=False
        gogaku+=i[1]
    elif i[0].startswith('30-10-'):#第二外国語1年
        gogaku+=i[1]
    elif i[0].startswith('30-20-01'):#英語2年
        if i[1]==0:
            print('英語(2年)未取得卒業不可')
            graduate=False
        gogaku+=i[1]
    elif i[0].startswith('30-2'):#第二or第三外国語2年
        gogaku+=i[1]
    elif i[0].startswith('30-30-'):#選択A
        gogaku+=i[1]

    ### 専門教育科目 ###
    #- 基礎科目 -#
    elif i[0].startswith('40-11-03'):#マクロ1
        if i[1]==0:
            print('マクロ1未取得卒業不可')
            graduate=False
        else:
            hisshu['macro1']=True
        senmon+=i[1]
    elif i[0].startswith('40-11-04'):#マクロ2
        if i[1]==0:
            print('マクロ2未取得卒業不可')
            graduate=False
        else:
            hisshu['macro2']=True
        senmon+=i[1]
    elif i[0].startswith('40-12-01'):#ミクロ1
        if i[1]==0:
            print('ミクロ1未取得卒業不可')
            graduate=False
        else:
            hisshu['micro1']=True
        senmon+=i[1]
    elif i[0].startswith('40-12-02'):#ミクロ2
        if i[1]==0:
            print('ミクロ2未取得卒業不可')
            graduate=False
        else:
            hisshu['micro2']=True
        senmon+=i[1]
    elif i[0].startswith('40-12-03'):#経済史1
        if i[1]==0:
            print('経済史1未取得卒業不可')
            graduate=False
        else:
            hisshu['zaishi1']=True
        senmon+=i[1]
    elif i[0].startswith('40-12-04'):#経済史2
        if i[1]==0:
            print('経済史2未取得卒業不可')
            graduate=False
        else:
            hisshu['zaishi2']=True
        senmon+=i[1]

    #- 選択必修 -#
    elif i[0].startswith('40-20-01'):#選択必修
        sentaku+=i[1]
        senmon+=i[1]
    elif i[0].startswith('40-21-01'):#選択必修
        sentaku+=i[1]
        senmon+=i[1]

    #- 基本科目 -#
    elif i[0].startswith('40-22-01'):
        kihon+=i[1]
        bunya["A"]+=i[1]
    elif i[0].startswith('40-22-02'):
        kihon+=i[1]
        bunya["B"]+=i[1]
    elif i[0].startswith('40-22-03'):
        kihon+=i[1]
        bunya["C"]+=i[1]
    elif i[0].startswith('40-22-04'):
        kihon+=i[1]
        bunya["D"]+=i[1]
    elif i[0].startswith('40-22-05'):
        kihon+=i[1]
        bunya["E"]+=i[1]
    elif i[0].startswith('40-22-06'):
        kihon+=i[1]
        bunya["F"]+=i[1]
    elif i[0].startswith('40-22-07'):
        kihon+=i[1]
        bunya["G"]+=i[1]
    elif i[0].startswith('40-22-08'):
        kihon+=i[1]
        bunya["H"]+=i[1]
    elif i[0].startswith('40-22-09'):
        kihon+=i[1]
        bunya["I"]+=i[1]
    elif i[0].startswith('40-22-10'):
        kihon+=i[1]
        bunya["J"]+=i[1]

    #- 関連科目 -#
    elif i[0].startswith('40-39-'):
        kanren+=i[1]

    #- 特殊科目 -#
    elif i[0].startswith('40-3'):
        senmon+=i[1]

    ### 自主選択科目 ###
    elif i[0].startswith('50-30-01'):#体育学講義
        jishu3+=i[1]
    elif i[0].startswith('50-31-01'):#体育学演習
        jishu3+=i[1]
    elif i[0].startswith('50-32-'):#体育実技
        jishu2+=i[1]
    elif i[0].startswith('50-50-'):#others
        nintei+=i[1]

    ### 自由科目 ###
    elif i[0].startswith('60-'):# 卒業の単位にはカウントされない
        sum-=i[1]
"""
print("般教 ",pankyo1+pankyo2+pankyo3)
print("基礎教育科目 ",kiso)
print("外国語科目 ",gogaku)
print("専門教育科目 ",senmon)
if kanren!=0:
    print("関連科目 ",kanren)
"""
#===== 必要単位分析 =====#
### 般教分析 ###
print("\n### 総合教育科目 ###")
print("般教取得単位数",pankyo1+pankyo2+pankyo3,"(必要単位1系6, 2系10, その他4)")
if pankyo1 > 6:
    print("般教1系ok")
else:
    print("般教1系不足")
    graduate=False

if pankyo2 > 10:
    print("般教2系ok")
else:
    print("般教2系不足")
    graduate=False

if pankyo1+pankyo2+pankyo3 > 4:
    print("般教1or2or3系ok")
    if pankyo1+pankyo2+pankyo3>20:
        print("般教から卒業認定単位に",pankyo1+pankyo2+pankyo3-20,"単位分が使われます。")
        nintei+=pankyo1+pankyo2+pankyo3-20#溢れた単位は卒業認定単位に回る
else:
    print("般教1or2or3系不足")
    graduate=False

### 必修 ###
for i in hisshu:
    if not hisshu[i]:
        print(i,"未取得卒業不可")
        graduate=False

### 基礎教育科目 ###
print("\n### 基礎教育科目 ###")
print("基礎教育科目取得単位数",kiso,"(必要単位8)")
if kiso<8:
    print("基礎教育科目不足(8単位中",kiso,"単位取得)")
    graduate=False
else:
    print("基礎教育科目ok")
    print("基礎教育科目から卒業認定単位に",kiso-8,"単位分が使われます。")
    nintei+=kiso-8

### 外国語科目 ###
print("\n### 外国語科目 ###")
print("外国語科目取得単位数",gogaku,"(必要単位14)")
if gogaku<8:
    print("外国語科目不足(14単位中",gogaku,"単位取得)")
    graduate=False
else:
    print("外国語科目ok")
    print("外国語科目から卒業認定単位に",gogaku-14,"単位分が使われます。")
    nintei+=gogaku-14

### 専門教育科目 ###
print("\n### 専門教育科目 ###")
#- 選択必修 -#
print("選択必修取得単位数",sentaku)
if sentaku<4:
    print("選択必修不足(4単位中",sentaku,"単位取得)")
    graduate=False
else:
    print("選択必修ok")
#- 関連科目 -#
if kanren>12:
    print("関連科目から卒業認定単位に",kanren-12,"単位分が使われます。(関連科目の上限は12単位)")
    senmon+=12
    nintei+=(kanren-12)
elif kanren!=0:
    print("関連科目は全て専門教育科目としてカウントされます。(関連科目の上限は12単位)")
    senmon+=kanren
#- 基本科目 -#
count=""#4単位以上の分野数
for i in bunya:
    if bunya[i]>=4:
        count+=i
print("基本科目4単位以上取得した分野数",len(count),"合計",kihon,"単位\n(4単位以上取得した分野が3つ以上必要)")
senmon+=kihon
if len(count)<3 or senmon<68:
    graduate=False
print("専門教育科目取得単位数",senmon,"(必要単位68)")

### 自主選択科目 ###
print("\n### 自主選択科目 ###")
print("自主選択科目取得単位数 ",jishu3+jishu2,"(必要単位0)")
jishu=0
if jishu3>3:
    free+=jishu3-3
    jishu3=3
if jishu2>2:
    free+=jishu2-2
    jishu2=2
jishu=jishu3+jishu2
if jishu>5:
    jishu=4
elif jishu!=0:
    print("自主選択科目(体育系)から卒業認定単位に",jishu,"単位が使われます。")
    nintei+=jishu

### 自由科目 ###
if free>0:
    print("\n### 自由科目 ###")
    print("自由科目扱いの単位が",free,"単位あります。\nこれらは卒業単位には含まれません。")

### 卒業認定単位 ###
print("\n### 卒業認定単位 ###")
print("卒業認定単位数",nintei,"(必要単位16)")


#===== 判定 =====#
print("\n### 判定 ###")
if sum<126:
    graduate=False
print('取得単位合計', sum, '単位')

### 進級判定 ###
#MEMO 自由科目は卒業単位にならないだけで進級要件の単位には数えられる

#- 2年生への進級 -#
if sum+free>24:#2年への進級は取得単位24以上のみ
    print("2年生に進級できます。")
else:
    print("2年生に進級できません。")

#- 3年性への進級 -#
kisokyouiku=(hisshu["toukei1"]+hisshu["toukei2"]+hisshu["bisekiORgairon"]+hisshu["senkeiORshiten"])*2#基礎教育科目から4単位以上
senmonkiso=(hisshu["macro1"]+hisshu["macro2"]+hisshu["micro1"]+hisshu["micro2"]+hisshu["zaishi1"]+hisshu["zaishi2"])*2#専門基礎科目から8単位以上
# 取得単位60・選択必修4・必修の基礎教育4・必修の専門教育基礎8・外国語科目8以上
if sum+free>60 and sentaku>=4 and kisokyouiku>=4 and senmonkiso>=8 and gogaku >=8:
    print("3年生に進級できます。")
else:
    print("3年生に進級できません。")

#- 4年生への進級 -#
print('3年次取得単位数 ',sannen)
if kiso>=8 and senmonkiso+sentaku>=16 and sannen>=28:
    print("4年生に進級できます。")
else:
    print("4年生に進級できません。")

#- 4年生の条件 -#
print('4年次取得単位数', yonen)
if yonen<12:
    graduate=False

### 卒業判定 ###
if graduate:
    print("卒業OKです、おめでとうございます。")
else:
    print("卒業不可です。")
