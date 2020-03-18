# -*- coding: utf-8 -*-

# Define your item pipelines here

import pymysql

class AicaigouPipeline(object):
    def __init__(self):
        self.connect = pymysql.connect(
            # localhost连接的是本地数据库
            host='rm-bp1s5d189x4h1wfh5.mysql.rds.aliyuncs.com',
            # host='127.0.0.1',
            # mysql数据库的端口号
            port=3306,
            # 数据库的用户名
            # user='root',
            user='crawl',
            # 本地数据库密码
            # passwd='mysql',
            passwd='crawl@123',
            # 数据库名
            # db='Alibb',
            db='crawl_ali',
            # 编码格式
            charset='utf8'
        )
        # 2. 创建一个游标cursor, 是用来操作表。
        self.cursor = self.connect.cursor()


    def process_item(self, item, spider):
        # 3. 将Item数据放入数据库，默认是同步写入。
        sql = 'insert into bdacg(name_s,url,phone,company,from_s) values (%s,%s,%s,%s,%s)'

        lis = (
            item['name'], item['url'], item['phone'], item['company'],item['from'])
        self.cursor.execute(sql, lis)

        # 4. 提交操作
        self.connect.commit()


    def close_spider(self, spider):
        self.cursor.close()
        self.connect.close()