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
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


'''
    简单的策略——移动均线策略。这个策略是由下向上超过均线就买入，相反就卖出
    simple: 测试tushare
    返回值：null
'''

def simple():

    df=ts.get_hist_data('600848',start='2017-01-01',end='2017-09-15')
    df=df.sort_index()
    df.index=pd.to_datetime(df.index,format='%Y-%m-%d')
    #收市股价
    close= df.close
    #每天的股价变动百分率
    ret=df.p_change/100
    # 10日的移动均线为目标
    df['SMA_10'] = talib.MA(np.array(close), timeperiod=10)
    close10=df.SMA_10

    #处理信号
    SmaSignal=pd.Series(0,index=close.index)

    for i in range(10,len(close)):
        if all([close[i]>close10[i],close[i-1]<close10[i-1]]):
            SmaSignal[i]=1
        elif all([close[i]<close10[i],close[i-1]>close10[i-1]]):
            SmaSignal[i]=-1

    SmaTrade=SmaSignal.shift(1).dropna()

    SmaBuy=SmaTrade[SmaTrade==1]

    SmaSell=SmaTrade[SmaTrade==-1]

    SmaRet=ret*SmaTrade.dropna()

    #累积收益表现
    #股票累积收益率
    cumStock=np.cumprod(1+ret[SmaRet.index[0]:])-1
    #策略累积收益率
    cumTrade=np.cumprod(1+SmaRet)-1


'''
     doubleline: 双均线策略,即5日短线移动平均超过30日长线移动平均即买入，其余时候空仓
    返回值：null
'''

def doubleline():
    df = ts.get_hist_data('600848', start='2015-01-01', end='2015-12-31')
    df = df.sort_index()
    df.index = pd.to_datetime(df.index, format='%Y-%m-%d')
    # 收市股价
    close = df.close
    # 每天的股价变动百分率
    ret = df.p_change / 100
    # 5\30日的移动均线为目标
    df['SMA_5'] = talib.MA(np.array(close), timeperiod=5)
    df['SMA_30'] = talib.MA(np.array(close), timeperiod=30)
    close5 = df.SMA_5
    close30 = df.SMA_30

    # 处理信号
    SmaSignal = pd.Series(0, index=close.index)

    for i in range(10, len(close)):
        if all([close5[i] > close30[i]]):
            SmaSignal[i] = 1

    SmaTrade = SmaSignal.shift(1).dropna()

    SmaRet = ret * SmaTrade.dropna()

    # 累积收益表现
    # 股票累积收益率
    cumStock = np.cumprod(1 + ret[SmaRet.index[0]:]) - 1
    # 策略累积收益率
    cumTrade = np.cumprod(1 + SmaRet) - 1


'''
    simplemacd: 即DIFF大于DEA的时候买入，其他时候卖出
    返回值：null
'''


def simplemacd():

    df = ts.get_hist_data('600848', start='2017-01-01', end='2017-12-31')
    df = df.sort_index()
    df.index = pd.to_datetime(df.index, format='%Y-%m-%d')
    # 收市股价
    close = df.close
    # 每天的股价变动百分率
    ret = df.p_change / 100
    # 调用talib计算MACD指标
    df['DIFF'], df['DEA'], df['MACD'] = talib.MACD(np.array(close),
                                                   fastperiod=12, slowperiod=26, signalperiod=9)

    diff = df.DIFF
    dea = df.DEA

    # 处理信号
    macdSignal = pd.Series(0, index=close.index)

    for i in range(10, len(close)):
        # if all([diff[i]>dea[i]>0,diff[i-1]<dea[i-1]]):
        if all([diff[i] > dea[i]]):
            macdSignal[i] = 1
        # elif all([diff[i]<dea[i]<0,diff[i-1]>dea[i-1]]):
        # macdSignal[i]=-1

    macdTrade = macdSignal.shift(1).dropna()
    macdRet = ret * macdTrade.dropna()

    # 累积收益表现
    # 股票累积收益率
    cumStock = np.cumprod(1 + ret[macdRet.index[0]:]) - 1
    # 策略累积收益率
    cumTrade = np.cumprod(1 + macdRet) - 1



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
    heima: 
           买入条件： 1）M10向上 2）收阳线 3）收盘价在MA10之上 4）DIF 在0之上
           卖出条件： 1）M10向下 2）收阴线 3）收盘价在MA10之下  or 低于买入价10%
    返回值：null
'''
def heima(stockname,sdate):

    df = ts.get_hist_data(stockname, start=sdate)
    df = df.sort_index()
    df.index = pd.to_datetime(df.index, format='%Y-%m-%d')
    # 收市股价
    close = df.close
    # 开盘股价
    open = df.open
    # MA10价格
    ma10=df.ma10
    # 每天的股价变动百分率
    ret = df.p_change / 100
    # 调用talib计算MACD指标
    df['DIFF'], df['DEA'], df['MACD'] = talib.MACD(np.array(close),fastperiod=12, slowperiod=26, signalperiod=9)

    diff = df.DIFF
    dea = df.DEA

    #晕死这个DIFF好像不对，所以还是直接输出其他几个判断条件后，列出来再人肉
    # 处理信号
    macdSignal = pd.Series(0, index=close.index)

    for i in range(1, len(close)):
        #if all([[diff[i]>0,ma10[i]>ma10[i-1]],close[i]>open[i],close[i]>ma10[i]]):
        if all([[ma10[i] > ma10[i - 1]], close[i] > open[i], close[i] > ma10[i]]):
            macdSignal[i] = 1
        elif all([ma10[i]<= ma10[i-1],close[i] < open[i],close[i] < ma10[i]]):
            macdSignal[i]=-1

    macdTrade = macdSignal.shift(1).dropna()
    macdRet = ret * macdTrade.dropna()

    # 累积收益表现
    # 股票累积收益率
    cumStock = np.cumprod(1 + ret[macdRet.index[0]:]) - 1
    # 策略累积收益率
    cumTrade = np.cumprod(1 + macdRet) - 1
    pd.set_option('display.max_rows', None)
    print macdSignal



'''
    主入口
'''

if __name__ == '__main__':
    print 'stock!'
    heima('600036','2019-01-01')



