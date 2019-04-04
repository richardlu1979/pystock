# coding: utf8
'''
    @Author: LCY
    @Contact: lchuanyong@126.com
    @blog: http://http://blog.csdn.net/lcyong_
    @Date: 2018-01-15
    @Time: 19:19
    说明： appid和secretKey为百度翻译文档中自带的，需要切换为自己的
           python2和python3部分库名称更改对应如下：
           httplib      ---->    http.client
           md5          ---->    hashlib.md5
           urllib.quote ---->    urllib.parse.quote
    官方链接：
           http://api.fanyi.baidu.com/api/trans/product/index

'''

import http.client
import hashlib
import json
import urllib
import random


def baidu_translate(content,toLang='en'):
    appid = '20180722000187847'
    secretKey = 'QmfvvQbj0Uc58CmQ63kx'
    httpClient = None
    myurl = '/api/trans/vip/translate'
    q = content.strip()
    fromLang = 'zh'  # 源语言
    salt = random.randint(32768, 65536)
    sign = appid + q + str(salt) + secretKey
    sign = hashlib.md5(sign.encode()).hexdigest()
    myurl = myurl + '?appid=' + appid + '&q=' + urllib.parse.quote(
        q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(
        salt) + '&sign=' + sign

    try:
        httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
        httpClient.request('GET', myurl)
        # response是HTTPResponse对象
        response = httpClient.getresponse()
        jsonResponse = response.read().decode("utf-8")  # 获得返回的结果，结果为json格式
        js = json.loads(jsonResponse)  # 将json格式的结果转换字典结构
        dst = str(js["trans_result"][0]["dst"])  # 取得翻译后的文本结果
        #print(dst)  # 打印结果
        return dst
    except Exception as e:
        return 'XXXXXXXX'
        print(e)
    finally:
        if httpClient:
            httpClient.close()

def testbaidu():
    while True:
        print("请输入要翻译的内容,如果退出输入q")
        content = input()
        if (content == 'q'):
            break
        print(baidu_translate(content))



def tansfile():
    try:
        target = open('a1.txt','w',encoding='UTF-8')
        with open('base.txt',encoding='UTF-8') as bf:
            for each_line in bf:
                print(each_line)
                target.write(each_line.strip()+','+baidu_translate(each_line)+'\r\n')

    except Exception as e:

        print(e)
    finally:
        target.close()


def tansmodel():
    try:
        i=0
        target = open('b1.txt','w',encoding='UTF-8')
        with open('base1.txt',encoding='UTF-8') as bf:
            for each_line in bf:
                print(i,each_line)
                i=i+1
                #根据不同的位置进行不同处理，没有\(var),在头，在尾，在中间
                tmp_line = each_line.strip()
                l = len (tmp_line)
                pos = tmp_line.find('\(var)')
                if pos== -1:
                    target.write(tmp_line + ',' + baidu_translate(tmp_line) + '\r\n')
                if pos== 0 :
                    target.write(tmp_line+','+'\(var)'+baidu_translate(tmp_line[6:]) + '\r\n')
                if pos== (l-6):
                    target.write(tmp_line + ',' +  baidu_translate(tmp_line[0:pos]) + '\(var)' + '\r\n')
                if (pos > 0) and (pos <l-6) :
                    target.write(tmp_line + ',' + baidu_translate(tmp_line[0:pos])+'\(var)'+baidu_translate(tmp_line[pos+6:])+'\r\n')

    except Exception as e:

        print(e)
    finally:
        target.close()

def test():
    a = '(第\(var)周)'
    k = a.find('\(var)')
    print(k)
    print(a[0:k])
    print(a[k + 6:])

    a1 = '查看地图'
    k1 = a1.find('\(var)')
    print(k1)

    a2 = '较上月增长\(var)'
    k2 = a2.find('\(var)')
    print(k2)
    print(a2[0:k2])
    print(len(a2))
    print(a2[k2 + 6:])

    a3 = '\(var)年'
    k3 = a3.find('\(var)')
    print(k3)



if __name__ == '__main__':
    #testbaidu()
    #tansfile()
    tansmodel()




