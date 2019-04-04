# coding:utf-8

'''
    heima: 黑马交易系统
    按照黑马交易系统构建程序化回归程序
    author:卢超

'''


import tushare as ts
import datetime
import os
import time
import sqlite3

'''
    testts: 测试tushare
    返回值：null
'''


def testts():
    hn = ts.get_k_data('300701', start='2018-04-01')
    sbegin = hn.iloc[0].values[2]
    send = hn.iloc[1].values[2]
    print(sbegin)
    print(send)
    print(hn)
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
                print(df[['name', 'price', 'time']])

            time.sleep(1200)
        except:
            pass


'''
    stockprofit: 根据stockname 股票的买入信号时间begintime，得到止盈价格:静态止盈，盈利30%，动态止盈，在当前时间中，最高的价格回落5%
    返回值：止盈价格
'''


def stockprofit(stockname, begintime):
    profitprice = float(0)
    today = datetime.date.today()
    oneday = datetime.timedelta(days=1)
    yesterday = today - oneday

    yday = yesterday.strftime("%Y-%m-%d")
    print(yday)
    print(begintime)
    try:
        hn = ts.get_k_data(stockname, start=begintime, end=yday)
        print(hn)
        send = hn.iloc[1].values[2]
        shigh = max(hn.iloc[:, 2].values)  # 取收盘价格最高值

        profitprice = max(send * 1.3, shigh * 0.95)
    except:
        pass
    return profitprice


'''
    stockloss: 根据stockname 股票的买入信号时间begintime，得到止损价格：买入时间收盘价格跌7%
    返回值：止损价格
'''


def stockloss(stockname, begintime):
    lossprice = float(0)
    try:
        hn = ts.get_k_data(stockname, start=begintime)
        lossprice = hn.iloc[0].values[2] * 0.93
    except:
        pass
    return lossprice


'''
    isrise: 比较指定股票sname在指定开始时间btime后span个工作日的涨跌情况
    返回值：1 涨，0 跌，-1 异常（span个工作日超过了当前交易日）
'''


def isrise(btime, sname, span):
    try:
        print('isrise')
        tmphn = ts.get_k_data(sname.strip(), start=btime.strip())
        # tmpbegin = tmphn.iloc[0].values[2]
        tmpbegin = tmphn.iloc[1].value[1]  # 修改下以第2天的开盘价格更真实
        print(tmpbegin)
        tmpend = tmphn.iloc[span].values[2]
        print(tmpend)
        if tmpend > tmpbegin:
            return 1
        else:
            return 0
    except:
        return -1


'''
    stocktradeinfo: 打印指定股票sname在指定开始时间btime后span个工作日里的信息
    返回值：0正常，-1 异常
'''


def stocktradeinfo(btime, sname, span):
    try:
        tmphn = ts.get_k_data(sname.strip(), start=btime.strip())
        t1 = tmphn.iloc[0].values[2]  # 买入信号当天的收盘价格
        t2 = tmphn.iloc[1].values[1]  # 买入信号第2天的开盘价格
        tn = tmphn.iloc[1].values[2]  # 买入span天后的收盘价格
        print('股票名：', sname, ' 买入时间：', btime, ' 买入当天收盘: ', t1, ' 买入第2天开盘: ', t2, ' 买入第', span, '天收盘: ', tn)
        return 0
    except:
        return -1


'''
    calrise: 计算指定股票sname在指定开始时间btime后span个工作日的涨跌比例
    这里修改买入规则，第2天最低价格大于第1天收盘价，则买入失败，涨幅为0
    返回值：涨幅/跌幅，-1 异常
'''


def calrise(btime, sname, span):
    try:
        tmphn = ts.get_k_data(sname.strip(), start=btime.strip())
        tmpbegin = tmphn.iloc[0].values[2]
        if (tmphn.iloc[1].values[4] > tmpbegin):
            ra = 0
        else:
            tmpend = tmphn.iloc[span].values[2]
            ra = (tmpend - tmpbegin) * 100 / tmpbegin
        print(ra)
        return ra
    except:
        return 0


'''
    recalsinggletime: 打开指定股票列表文件sfile,回测最简单的交易策略，发出购买信号收盘价格买入，持有num
                      天后卖出
    返回值： 涨跌幅度之和，0异常
'''


def recalsingletime(sfile, nday):
    try:
        data = open(sfile)
        print('=======')
        ntotalrate = 0
        for each_line in data:
            (buytime, stockname) = each_line.split(' ', 1)
            k = calrise(buytime, stockname, nday)
            ntotalrate = ntotalrate + k
    except:
        return 0

    return ntotalrate


'''
    calrate: 打开指定股票列表文件sfile,回测试文件中的每一个股票，在买入信号，后num天后的
             上涨百分比
    返回值： 上涨百分比，0异常
'''


def calrate(sfile, num):
    try:
        data = open(sfile)
        ntotal = 0
        nrise = 0
        for each_line in data:
            ntotal = ntotal + 1
            (buytime, stockname) = each_line.split(' ', 1)
            k = isrise(buytime, stockname, num)
            if k > 1:
                nrise = nrise + 1

    except:
        return 0

    print('全部信号： ', ntotal)
    print('有效上涨信号: ', nrise)
    # return 100*nrise/ntotal
    return 0


'''
    stbinsert: 打开指定股票列表文件sfile, 将股票编号，和买入时间点插入
    返回值： 0正常，1异常
'''


def stbinsert(sfile):
    try:
        print('insert')
        data = open(sfile)
        conn = sqlite3.connect('test.db')
        print("Open database successfully")
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
                print(stockname, buytime, 'no 3 days')
            print(ncount)
            ncount = ncount + 1
        conn.commit()
        conn.close()


    except:
        print('error')
        pass


'''
    calmutirate:计算1，2，3，4，5，6，10天对应的胜率
    返回值：无
'''


def calmutirate():
    rate1 = calrate('stocklist.txt', 1)
    print(rate1)
    rate2 = calrate('stocklist.txt', 2)
    print(rate2)
    rate3 = calrate('stocklist.txt', 3)
    print(rate3)
    rate4 = calrate('stocklist.txt', 4)
    print(rate4)
    rate5 = calrate('stocklist.txt', 5)
    print(rate5)
    rate6 = calrate('stocklist.txt', 6)
    print(rate6)
    rate10 = calrate('stocklist.txt', 10)
    print(rate10)


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
        print('error')
        pass


'''
    主函数
'''


def main():
    print('main')
    # stbupdate(1)
    # stbinsert('stocklist.txt')
    # calmutirate()
    # isrise('2018-04-03','300584',5)
    # calrate('stocklist.txt', 3)
    watchstock()
    # testts()
    # pv=stockprofit('300404','2018-04-16')
    # m= stocktradeinfo('2018-04-16','300404',5)
    # print(pv)
    # crise1 =  recalsingletime('stocklist.txt',3)
    # print('=====total rise=====')
    # print(crise1)


'''
    主入口
'''

if __name__ == '__main__':
    main()



