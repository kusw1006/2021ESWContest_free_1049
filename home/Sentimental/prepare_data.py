import pandas as pd


dataPath="./"
fname="ECorpus_Test"
fnameOut="_out"
txtFile="spoken.txt"

df = pd.read_excel("{0}{1}.xlsx".format(dataPath, fname), engine = "openpyxl")

from pandas import DataFrame
import csv
#df.to_excel('test_save.xlsx')


# 기쁨 불안 당황 슬픔 분노 상처
# 0: 평서문, 불안, 당황
# 1: 기쁨, 
# 2: 분노, 상처
# 3: 슬픔
lenOfRow = len(df)

with open('{0}{1}{2}.csv'.format(dataPath, fname, fnameOut), 'w', newline='', encoding='utf8') as f: 
    write = csv.writer(f)
    for x in range(2, lenOfRow - 2):
        df3 = [0, 0]
        for i in range(5):
            df2 = DataFrame(df.loc[x, ["사람문장{0}".format(i)]]).values.tolist()
            
            str_tmp = df2[0][0]
            if i == 0:
                str_tmp.replace(" ", "")
                if(str_tmp == '불안' or str_tmp == '당황'):
                    str_tmp = '0'
                elif(str_tmp == '기쁨'):
                    str_tmp = '1'
                elif(str_tmp == '분노' or str_tmp == '상처'):
                    str_tmp = '2'
                elif(str_tmp == '슬픔'):
                    str_tmp = '3'
                df3[0] = str_tmp
            else:
                if(pd.isna(df2)):
                    break

                df3[1] = str_tmp.replace("\"", "").replace("\'", "").replace(",", "")
                write.writerow(df3)

    # spoken에서 평서문 추가
    with open('{0}'.format(txtFile), 'r', encoding='utf8') as f2:
        # 테스트모드와 트레인모드, 읽어들이는 곳 변경 필요
        if fname[-1] == 't':
            for x in range(1000000):
                f2.readline()

        for x in range(lenOfRow * 2):
            df4 = list()
            line = f2.readline()
            df4.append('0')
            str_tmp = line[:-1]
            if not len(str_tmp):
                continue
            
            df4.append(str_tmp.replace("\"","").replace("\'","").replace(",", ""))
            write.writerow(df4)        



