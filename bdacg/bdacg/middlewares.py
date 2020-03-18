# -*- coding: utf-8 -*-
import random


def get_ua():
    first_num = random.randint(55, 62)
    third_num = random.randint(0, 3200)
    fourth_num = random.randint(0, 140)
    os_type = [
        '(Windows NT 6.1; WOW64)', '(Windows NT 10.0; WOW64)', '(X11; Linux x86_64)',
        '(Macintosh; Intel Mac OS X 10_12_6)'
    ]
    chrome_version = 'Chrome/{}.0.{}.{}'.format(first_num, third_num, fourth_num)

    ua = ' '.join(['Mozilla/5.0', random.choice(os_type), 'AppleWebKit/537.36',
                   '(KHTML, like Gecko)', chrome_version, 'Safari/537.36']
                  )
    return ua


# 使用随机ua
class RandomUserAgentMid:
    def process_request(self, request, spider):
        request.headers["User-Agent"] = get_ua()


import base64

#  阿布云ip代理配置，包括账号密码
proxyServer = "http-dyn.abuyun.com:9020"
proxyUser = "H93292AC09K83KZD"
proxyPass = "C5C07D82E30C86E7"

# for Python3
proxyAuth = "Basic " + base64.urlsafe_b64encode(bytes((proxyUser + ":" + proxyPass), "ascii")).decode("utf8")


class ABProxyMiddleware(object):
    """ 阿布云ip代理配置 """

    def process_request(self, request, spider):
        request.meta["proxy"] = proxyServer
        request.headers["Proxy-Authorization"] = proxyAuth
