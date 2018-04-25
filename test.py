#coding:utf-8
import tushare as ts
import datetime
import os
import time

'''
    testts: 测试tushare
    返回值：null
'''
def testts():
    hn=ts.get_k_data('300701',start='2018-04-01')
    sbegin = hn.iloc[0].values[2]
    send = hn.iloc[1].values[2]
    print(sbegin)
    print(send)
    print(hn)
    #测试获取股票实时报价
    #df = ts.get_realtime_quotes('150174')  # Single stock symbol
    #print(df[['code', 'name', 'price', 'bid', 'ask', 'volume', 'amount', 'time']])


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
                print(df[['name','price','time']])

            time.sleep(120)
        except:
            pass


'''
    stockprofit: 根据stockname 股票的买入信号时间begintime，得到止盈价格:静态止盈，盈利30%，动态止盈，在当前时间中，最高的价格回落5%
    返回值：止盈价格
'''
def stockprofit(stockname,begintime):
    profitprice =float(0)
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
        shigh=max(hn.iloc[:,2].values) #取收盘价格最高值

        profitprice = max(send *1.3,shigh*0.95)
    except:
        pass
    return profitprice


'''
    stockloss: 根据stockname 股票的买入信号时间begintime，得到止损价格：买入时间收盘价格跌7%
    返回值：止损价格
'''
def stockloss(stockname,begintime):
    lossprice =float(0)
    try:
        hn = ts.get_k_data(stockname, start=begintime)
        lossprice = hn.iloc[0].values[2]*0.93
    except:
        pass
    return lossprice




'''
    isrise: 比较指定股票sname在指定开始时间btime后span个工作日的涨跌情况
    返回值：1 涨，0 跌，-1 异常（span个工作日超过了当前交易日）
'''
def isrise(btime,sname,span):
    try:
        tmphn = ts.get_k_data(sname.strip(),start=btime.strip())
        tmpbegin = tmphn.iloc[0].values[2]
        tmpend = tmphn.iloc[span].values[2]
        if tmpend > tmpbegin:
            return 1
        else:
            return 0
    except:
        return -1



'''
    calrise: 计算指定股票sname在指定开始时间btime后span个工作日的涨跌比例
    这里修改买入规则，第2天最低价格大于第1天收盘价，则买入失败，涨幅为0
    返回值：涨幅/跌幅，-1 异常
'''
def calrise(btime,sname,span):
    try:
        tmphn = ts.get_k_data(sname.strip(),start=btime.strip())
        tmpbegin = tmphn.iloc[0].values[2]
        if (tmphn.iloc[1].values[4]>tmpbegin):
            ra =0
        else:
            tmpend = tmphn.iloc[span].values[2]
            ra = (tmpend-tmpbegin)*100/tmpbegin
        print(ra)
        return ra
    except:
        return 0


'''
    recalsinggletime: 打开指定股票列表文件sfile,回测最简单的交易策略，发出购买信号收盘价格买入，持有num
                      天后卖出
    返回值： 涨跌幅度之和，0异常
'''
def recalsingletime(sfile,nday):
    try:
        data = open(sfile)
        print('=======')
        ntotalrate = 0
        for each_line in data:
            (buytime,stockname) = each_line.split(' ',1)
            k= calrise(buytime,stockname,nday)
            ntotalrate = ntotalrate + k
    except:
        return 0
    
    return ntotalrate




'''
    calrate: 打开指定股票列表文件sfile,回测试文件中的每一个股票，在买入信号，后num天后的
             上涨百分比
    返回值： 上涨百分比，0异常
'''
def calrate(sfile,num):
    try:
        data = open(sfile)
        ntotal = 0
        nrise =0 
        for each_line in data:
            ntotal = ntotal +1
            (buytime,stockname) = each_line.split(' ',1)
            k= isrise(buytime,stockname,num)
            if k<0:
                ntotal = ntotal -1
            else:
                nrise = nrise +k
    except:
        return 0
    
    print (ntotal)
    print(nrise)
    return 100*nrise/ntotal
    
'''
    calmutirate:计算1，2，3，4，5，6，10天对应的胜率
    返回值：无
'''
def calmutirate():
    rate1 = calrate('stocklist.txt',1)
    print(rate1)
    rate2 = calrate('stocklist.txt',2)
    print(rate2)
    rate3 = calrate('stocklist.txt',3)
    print(rate3)
    rate4 = calrate('stocklist.txt',4)
    print(rate4)
    rate5 = calrate('stocklist.txt',5)
    print(rate5)
    rate6 = calrate('stocklist.txt',6)
    print(rate6)
    rate10 = calrate('stocklist.txt',10)
    print(rate10)

'''
    主函数
'''

def main():
    print ('main')
    watchstock()
    #testts()
    #pv=stockprofit('300404','2018-04-16')
    #print(pv)
    #crise1 =  recalsingletime('stocklist.txt',3)
    #print('=====total rise=====')
    #print(crise1)





'''
    主入口
'''

if __name__ == '__main__':
    print ('main')
    main()



