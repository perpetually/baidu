# -*- coding: utf-8 -*-
import json
import re

import scrapy
from copy import deepcopy
from ..items import BdacgItem

class BdSpider(scrapy.Spider):
    name = 'baidu'
    # allowed_domains = ['b2b.baidu.com']
    start_urls = ['https://b2b.baidu.com/']

    def parse(self, response):
        # 获取html
        html = response.body.decode('utf-8')
        # 匹配json
        ret = re.compile('window.data = (.*?);', re.S)
        rest = re.search(ret, html).group(1)
        print(rest)
        # 遍历获取jumpurl
        s = json.loads(rest)
        nav = s['nav']
        for detail in nav:
            list = detail['detail']

            for dict in list:
                data = dict['list']
                for jumpurl in data:
                    url = jumpurl['jumpUrl']
                    item = BdacgItem()
                    item['url_l'] = 'https://b2b.baidu.com/' + url
                    item['title'] = jumpurl['title']

                    print(item)
                    yield scrapy.Request(
                        item['url_l'],
                        callback=self.get_ajax,
                        meta={'item': deepcopy(item)}
                    )

    def get_ajax(self, response):
        item = response.meta['item']
        html = response.body.decode('utf-8')
        # 匹配json
        ret = re.compile('window.data = (.*?);', re.S)
        rest = re.search(ret, html).group(1)
        # 遍历获取jumpurl
        s = json.loads(rest)
        # data=s['data']
        item['dispNum'] = num = s['dispNum']
        for i in range(1, num // 38):
            # 翻页请求
            item[
                'url_m'] = 'https://b2b.baidu.com/s/a?ajax=1&csrf_token=f7d912c3dbdf033254b97df9879a10ca&o=0&q={}&p={}&sa=&mk=%E5%85%A8%E9%83%A8%E7%BB%93%E6%9E%9C&f=[]'.format(
                item['title'], i)
            # print(item)
            yield scrapy.Request(
                item['url_m'],
                callback=self.get_list,
                meta={'item': deepcopy(item)}
            )

    def get_list(self, response):
        # print('*' * 30)
        item = response.meta['item']
        # 获取html
        html = response.body.decode('utf-8')
        s = json.loads(html)
        data = s['data']
        item['pageNum'] = data['pageNum']
        productList = data['productList']
        # 获取详情页url,数据来源网站,公司名

        for list in productList:
            item['url_s'] = list['jumpUrl']
            item['from'] = list['from']
            item['company'] = list['fullProviderName']

            yield scrapy.Request(
                item['url_s'],
                callback=self.get_detail,
                meta={'item': deepcopy(item)}
            )

    def get_detail(self, response):
        # 获取不同公司名的电话　姓名
        item = response.meta['item']
        if item['from'] == '仟渔网':
            href = re.search(r'\d+.html', item['url_s']).group()
            item['url'] = 'http://www.qianyuwang.com/offer/' + href
            # print(item)
            yield scrapy.Request(
                item['url'],
                callback=self.get_qianyu,
                meta={'item': item}
            )

        elif item['from'] == '搜好货网':
            href = re.search(r'\d+.html', item['url_s']).group()
            item['url'] = 'http://www.912688.com/supply/' + href
            # print(item)
            yield scrapy.Request(
                item['url'],
                callback=self.get_souhao,
                meta={'item': item}
            )

        elif item['from'] == '找商网':
            href = re.match(r'\d+', re.search(r'\d+&query', item['url_s']).group()).group()
            item['url'] = 'https://www.zhaosw.com/product/detail/' + href
            yield scrapy.Request(
                item['url'],
                callback=self.get_zhaoshang,
                meta={'item': item}
            )

        elif item['from'] == '搜了网':
            href = re.search(r'\d+.htm', item['url_s']).group()
            item['url'] = 'http://www.51sole.com/tp/' + href
            # print(item)
            yield scrapy.Request(
                item['url'],
                callback=self.get_soule,
                meta={'item': item}
            )

        elif item['from'] == '全球塑胶网':
            href = item['url_s'].split('Info%2F')[1].split('&query')[0].replace('%2F', '/')
            item['url'] = 'https://www.51pla.com/html/sellinfo/' + href
            # print(item)
            yield scrapy.Request(
                item['url'],
                callback=self.get_sujiao,
                meta={'item': item}
            )

        elif item['from'] == '慧聪网':
            href = re.search(r'\d+.html', item['url_s']).group()
            item['url'] = 'https://b2b.hc360.com/supplyself/' + href
            yield scrapy.Request(
                item['url'],
                callback=self.get_huicong,
                meta={'item': item}
            )

        elif item['from'] == '微智服采购':
            href = re.search(r'\d+.htm', item['url_s']).group()
            item['url'] = 'https://www.bjweizhifu.com/sell/show-' + href
            # print(item)
            yield scrapy.Request(
                item['url'],
                callback=self.get_wzf,
                meta={'item': item}
            )

    def get_qianyu(self, response):
        item = response.meta['item']
        # print('*' * 40)
        item['phone'] = response.xpath('//div[@class="score-infor"]/ul/li[2]/text()').extract_first()
        item['name'] = response.xpath('//span[@style="vertical-align:top"]/text()').extract_first()
        # print(item)
        yield item

    def get_souhao(self, response):
        item = response.meta['item']
        item['phone'] = response.xpath('//span[@class="val prod-phone"]/text()').extract_first()
        item['name'] = response.xpath('//a[@class="val concat-name"]/@title').extract_first()
        # print(item)
        yield item

    def get_zhaoshang(self, response):
        item = response.meta['item']
        item['phone'] = response.xpath('normalize-space(//span[@class="phone-num"]/text())').extract_first()
        item['name'] = response.xpath('//p[@class="p2"]/span[2]/text()').extract_first()
        # print(item)
        yield item

    def get_soule(self, response):
        item = response.meta['item']
        item['phone'] = response.xpath('//span[@id="lblMobilePhone"]/text()').extract_first()
        item['name'] = response.xpath('//span[@id="lblPersonName"]/text()').extract_first()
        yield item
        # print(item)

    def get_sujiao(self, response):
        # print('*' * 50)
        item = response.meta['item']
        item['phone'] = response.xpath('//div[@class="two"]/p[@class="p3"][2]/span[2]/text()').extract_first()

        item['name'] = response.xpath('//div[@class="two"]/p[@class="p1"]/span[2]/text()').extract_first()
        yield item
        # print(item)

    def get_huicong(self, response):
        # print('*' * 100)

        item = response.meta['item']
        item['phone'] = response.xpath('//em[@class="c-red"]/text()').extract_first()
        item['name'] = response.xpath('//div[@class="p name"]/em/text()').extract_first().split('\xa0')[0]
        yield item
        # print(item)

    def get_wzf(self, response):
        item = response.meta['item']
        item['phone'] = response.xpath('//div[@class="personal_bottom"]/span/text()').extract_first()
        item['name'] = response.xpath('//div[@class="personal_top"]/div/span/text()').extract_first()
        yield item
        print(item)
