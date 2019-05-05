# coding:utf-8


'''
    heima: 黑马交易系统
    按照黑马交易系统构建程序化回归程序
    author:卢超
    使用python2.7

'''


import tushare as ts
import datetime
import time
import sqlite3
import talib
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import smtplib,os,sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email import encoders
from email.mime.base import MIMEBase
from email.utils import parseaddr, formataddr



# 格式化邮件地址
def formatAddr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))

# 发送邮件
def sendMail(body):
    host = 'smtp.163.com'
    # 设置发件服务器地址
    port = 994
    # 设置发件服务器端口号。注意，这里有SSL和非SSL两种形式，现在一般是SSL方式
    sender = 'cafield2008@163.com'
    # 设置发件邮箱，一定要自己注册的邮箱
    pwd = 'keesofT&65@'
    # 设置发件邮箱的授权码密码，根据163邮箱提示，登录第三方邮件客户端需要授权码
    receiver = 'cafield2008@163.com'
    # 设置邮件接收人，可以是QQ邮箱
    body = '<h1>你已成功打卡</h1><p>zhongfs</p>'
    # 设置邮件正文，这里是支持HTML的
    msg = MIMEText(body, 'html')
    # 设置正文为符合邮件格式的HTML内容
    msg['subject'] = body
    # 设置邮件标题
    msg['from'] = sender
    # 设置发送人
    msg['to'] = receiver
    # 设置接收人
    try:
        s = smtplib.SMTP_SSL(host, port)
        # 注意！如果是使用SSL端口，这里就要改为SMTP_SSL
        s.login(sender, pwd)
        # 登陆邮箱
        s.sendmail(sender, receiver, msg.as_string())
        # 发送邮件！
        print ('Done.sent email success')
    except smtplib.SMTPException:
        print ('Error.sent email fail')


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
    pd.set_option('display.max_rows', None)
    # 使用get_k_data 可以得到前复权
    df = ts.get_k_data(stockname,start=sdate)

    df.index = df.date
    # 收市股价
    close = df.close
    # 开盘股价
    open = df.open
    # MA10价格
    ma10=  talib.MA(close,timeperiod=10)

    # 调用talib计算MACD指标
    # 晕死这个DIFF好像不对，所以还是直接输出其他几个判断条件后，列出来再人肉
    #df['DIFF'], df['DEA'], df['MACD'] = talib.MACD(np.array(close),fastperiod=12, slowperiod=26, signalperiod=9)

    df['DIFF'], df['DEA'], df['MACD']= talib.MACDEXT(close, fastperiod=12, fastmatype=1, slowperiod=26, slowmatype=1,signalperiod=9, signalmatype=1)
    diff = df.DIFF
    dea = df.DEA

    # 处理信号
    macdSignal = pd.Series(0, index=close.index)
    #为什么这里34开头，因为上面的macd计算的化前面34个都是 NAN 出来
    for i in range(34, len(close)):

        if diff[i]>0 and ma10[i] > ma10[i-1] and close[i] > open [i] and close[i] > ma10[i]:
            macdSignal[i] = 1

        elif ma10[i] <= ma10[i-1] and close[i] < open [i] and close[i] < ma10[i]:
            macdSignal[i]=-1
    print macdSignal[-130:]

    return macdSignal

'''
    realtimeheima: 
            得到当前时间之实时股票价格，并加入到均线/macd计算中，得到实时的买卖信号
    返回值：1 买入，-1 卖出，0 维持
'''
def realtimeheima(stockname):

    # 使用get_k_data 可以得到前复权
    df = ts.get_k_data(stockname,start='2018-12-12')
    df.index = df.date
    # 收市股价
    close = df.close
    dreal = ts.get_realtime_quotes(stockname)
    mdate = dreal['date'][0]
    #这里有坑，dreal出来的price,open这些都是字符串，需要手动转float
    mclose = float(dreal['price'][0])
    mopen = float(dreal['open'][0])
    newclose = pd.Series({mdate : mclose})
    all_close = close.append(newclose)

    print all_close
    # MA10价格
    ma10=  talib.MA(all_close,timeperiod=10)

    # 调用talib计算MACD指标
    # 晕死这个DIFF好像不对，所以还是直接输出其他几个判断条件后，列出来再人肉
    #df['DIFF'], df['DEA'], df['MACD'] = talib.MACD(np.array(close),fastperiod=12, slowperiod=26, signalperiod=9)

    diff, dea, macd= talib.MACDEXT(all_close, fastperiod=12, fastmatype=1, slowperiod=26, slowmatype=1,signalperiod=9, signalmatype=1)

    i= len(all_close)-1



    manow =0
    manow = ma10.values[i]
    maold = 0
    maold = ma10.values[i-1]
    diffnow = 0.0
    diffnow = diff.values[i]

    print 'diff :',diffnow,' ma10 :',manow ,'ma old :',maold
    print 'real close :',mclose,' real open: ',mopen


    sign = 0
    if diffnow>0 and manow > maold and mclose> mopen and mclose > manow:
        sign = 1

    if mclose<mopen and manow<=maold and mclose<manow:
    #if mclose < mopen and manow <= maold and mclose < manow:
    #elif mclose < mopen :
        sign=-1

    return sign



'''
    recalheima 
            参数 heimaSignal:买卖时间点信号
    返回值：null
'''

def recalheima(sname,begindata,heimaSignal):

    sig = heimaSignal
    # print sig
    # 最简单的处理，定义一个字符串数组，数组中为 一个买入时间，一个卖出时间，计算时候定义一个状态0空仓，1满仓
    stat = 0
    trade = []
    for j in range(0, len(sig)):
        # print sig.index[j],'+++',sig.values[j]
        if sig.values[j] == 1 and stat == 0:
            stat = 1
            trade.append(sig.index[j])
        elif sig.values[j] == -1 and stat == 1:
            stat = 0
            trade.append(sig.index[j])
    # 接下来计算每一次买入，卖出的回报，盈亏比例，及总盈亏比
    #print trade
    df = ts.get_k_data(sname, start=begindata)
    df.index = df.date
    df1 = df.shift(-1)

    # 在这里可以加点好玩的，如果是用发出信号后的第2天的价格入手 open or close？
    #c = df1.open
    c=df.close


    strbuy = ''
    vbuy = 0
    strsell = ''
    vsell = 0
    sigprofit = 0
    totalprofit = 0
    win = 0
    all = 0
    for m in range(0, len(trade)):
        if m % 2 == 0:
            strbuy = trade[m]
            vbuy = c[strbuy]
        elif m % 2 == 1:
            strsell = trade[m]
            vsell = c[strsell]
            all = all + 1
            sigprofit = (vsell - vbuy) / vbuy * 100
            print '买入时间： ', strbuy, '买入价：', vbuy, '卖出时间： ', strsell, '卖出价：', vsell, ' 单笔盈亏： ', sigprofit
            if sigprofit > 0:
                win = win + 1
            totalprofit = totalprofit + sigprofit

    print '过交易次数： ', all, '盈利交易次数： ', win, '盈利比例： ', win / all * 100
    print '总盈亏： ', totalprofit




'''
    主入口
'''

if __name__ == '__main__':
    print 'stock!'


    #kv = realtimeheima('502050')
    #print 'hhhh: ',kv


    #stocklist =['000859','150252','150201','150153','150197','150206','150131','502050','150195','150270','000858']
    stocklist = ['150195']
    for k in range(0,len(stocklist)):
        print '股票代码：' , stocklist[k]
        sig= heima(stocklist[k],'2016-12-01')
        recalheima(stocklist[k],'2016-12-01',sig)


