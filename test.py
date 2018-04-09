#coding:utf-8
import tushare as ts
import datetime

hn=ts.get_k_data('300584',start='2018-04-03')

#print (hn)
#判断n天后是涨 y=1，是跌 y=0
y=0
n=4
sbegin = hn.iloc[0].values[2]
send = hn.iloc[1].values[2]

if send>sbegin:
    y=1

#print(sbegin)
#print(send)
#print(y)

'''
   
'''
def isrise(btime,sname,span):
    try:
        tmphn = ts.get_k_data(stockname.strip(),start=buytime.strip())
        tmpbegin = tmphn.iloc[0].values[2]
        tmpend = tmphn.iloc[n].values[2]
        if tmpend > tmpbegin:
            return 1
        else:
            return 0
    except:
        return -1



print ('=============')

data = open('stocklist.txt')
ntotal = 0
nrise =0 
for each_line in data:
    ntotal = ntotal +1
    (buytime,stockname) = each_line.split(' ',1)
    k= isrise(buytime,stockname,n)
    if k<0:
        ntotal = ntotal -1
    else:
        nrise = nrise +k

print ('==home====')
print (ntotal)
print(nrise)
print(100*nrise/ntotal)


