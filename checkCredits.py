# -*- coding: utf-8 -*-
#===== modules =====#
import csv, re
from analyze import analyze
### not depending on external libraries ###

#===== はじまるよ！ =====#
print("\n#===== 卒業・進級判定プログラム =====#")

#===== データ読み込み =====#
### ファイルを開く ###
filename='seiseki.csv'# このcsvはkeio.jpで表示される成績をExcelにコピペしてUTF8で保存したもの
file = open(filename,'r')
seiseki = csv.reader(file)
### 変数を用意 ###
sum = 0
credits = []

for i in seiseki:
    if len(i)>1:
        direct = True
        break
    else:
        direct = False
        break

### 分野コードと取得単位を取得 ###
if direct:# 直接Excelにコピペした場合
    for i in seiseki:
        if i[0].startswith('分野'):
            if i[1].startswith('取得合計'):
                num = int(int(re.sub("\\D", "", str(i[1])))/10)# 正規表現を用いて数字だけ取り出す
                sum += num
                credits.append([i[0][3:11], num])
                #print('分野', i[0][3:11], 'を', num, '単位')#for debug

else:# ワンクッション挟んでコピペした場合
    for j in seiseki:
        if len(j)==0:
            pass
        elif len(j)>1:
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
file.close()
file = open(filename,'r')# ポインタの関係からか、なぜか開き直さないとうまくいかない
seiseki = csv.reader(file)#TODO 上の並行して3,4年の取得単位も取るようにする

### 3,4年生の進級条件 ###
sannen=0# 3年次取得単位
yonen=0# 4年次取得単位
# これらは留年してn回目の3,4年生でもn年分合計される
if direct:
    seiseki=[x for x in seiseki]
    for i in seiseki:
        if len(i)==0:
            pass
        elif i[-1].startswith("3年") and not (i[2].startswith("Ｄ") or i[2].startswith("Ｆ") or i[2].startswith("？")):
            sannen+=int(i[3])
        elif i[-1].startswith("4年") and not (i[2].startswith("Ｄ") or i[2].startswith("Ｆ") or i[2].startswith("？")):
            yonen+=int(i[3])
else:
    for j in seiseki:
        #print(j)
        if len(j)==0:
            pass
        elif j[0][-2:]=="3年":
            hoge=j[0].split(" ")
            if not (hoge[-7].startswith("Ｄ") or hoge[-7].startswith("Ｆ") or hoge[-7].startswith("？")):
                sannen+=int(float(hoge[-6]))
        elif j[0][-2:]=="4年":
            hoge=j[0].split(" ")
            if not (hoge[-7].startswith("Ｄ") or hoge[-7].startswith("Ｆ") or hoge[-7].startswith("？")):
                yonen+=int(float(hoge[-6]))
file.close()# 開けたら閉める

analyze(credits,sum, sannen, yonen)
