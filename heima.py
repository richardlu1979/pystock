# coding:utf-8

'''
    heima: 黑马交易系统
    按照黑马交易系统构建程序化回归程序
    author:卢超
    使用python2.7

'''


import tushare as ts
import datetime
import os
import time
import sqlite3
import talib

'''
    testts: 测试tushare
    返回值：null
'''


def testts():
    hn = ts.get_k_data('300701', start='2018-04-01')
    sbegin = hn.iloc[0].values[2]
    send = hn.iloc[1].values[2]
    print sbegin
    print send
    print hn
    # 测试获取股票实时报价
    # df = ts.get_realtime_quotes('150174')  # Single stock symbol
    # print(df[['code', 'name', 'price', 'bid', 'ask', 'volume', 'amount', 'time']])


'''
    watchstock: 监控实时的股票价格
    返回值：null
'''


def watchstock():
    stocklist = ['150174']
    while 1:
        try:
            for stock in stocklist:
                df = ts.get_realtime_quotes(stock)  # Single stock symbol
                print df[['name', 'price', 'time']]

            time.sleep(1200)
        except:
            pass



'''
    stbinsert: 打开指定股票列表文件sfile, 将股票编号，和买入时间点插入
    返回值： 0正常，1异常
'''


def stbinsert(sfile):
    try:
        print 'insert'
        data = open(sfile)
        conn = sqlite3.connect('test.db')
        print "Open database successfully"
        c = conn.cursor()
        ncount = 0
        hs = ts.get_stock_basics()
        for each_line in data:
            (buytime, stockname) = each_line.split(' ', 1)
            tmphn = ts.get_k_data(stockname.strip(), start=buytime.strip())
            nsize = tmphn.iloc[:, 0].size
            sname = hs.loc[stockname.strip()].values[0]
            if nsize > 10:
                beginprice = tmphn.iloc[0].values[2]
                buyprice = tmphn.iloc[1].values[1]
                twop = tmphn.iloc[2].values[2]
                threep = tmphn.iloc[3].values[2]
                fivep = tmphn.iloc[5].values[2]
                tenp = tmphn.iloc[10].values[2]
                c.execute(
                    "INSERT INTO tbstock (sname,begintime,scode,beginprice,buyprice,twop,threep,fivep,tenp) VALUES (?,?,?,?,?,?,?,?,?)",
                    (sname, buytime.strip(), stockname.strip(), beginprice, buyprice, twop, threep, fivep, tenp))
            else:
                print stockname, buytime, 'no 3 days'
            print ncount
            ncount = ncount + 1
        conn.commit()
        conn.close()


    except:
        print 'error'
        pass


'''
    stbupdate: 查出所有buyprice,twop,threep,fivep,tenp为空的记录，进行相应的update动作
               stype : 1 更新 buyprice,3 更新threep,2更新 twop,5 更新fivep,10更新 tenp
    返回值： 0正常，1异常
'''


def stbupdate(stype):
    try:
        conn = sqlite3.connect('test.db')
        print("Open database successfully")
        c = conn.cursor()
        c.execute('SELECT * FROM tbstock WHERE buyprice IS NULL ')
        vs = c.fetchall()
        for row in vs:
            buytime = row[2]
            scode = row[1]
            tmphn = ts.get_k_data(scode.strip(), start=buytime.strip())
            nsize = tmphn.iloc[:, 0].size
            if nsize > 0:
                buyprice = tmphn.iloc[1].values[1]
                c.execute("UPDATE  tbstock SET buyprice= ? WHERE scode =? ", (buyprice, scode))

        c.close()
        conn.commit()
        conn.close()
    except:
        print 'error'
        pass


'''
    主入口
'''

if __name__ == '__main__':
    print 'stock!'



