import psycopg2
from datetime import datetime, timedelta
from scrapy.exceptions import NotConfigured
from media_config import media_config


class DatabasePipeline(object):

    def __init__(self, db, user, passwd, host, table):
        self.db = db
        self.user = user
        self.passwd = passwd
        self.host = host
        self.table = table

    @classmethod
    def from_crawler(cls, crawler):
        db_settings = crawler.settings.getdict("DB_SETTINGS")
        if not db_settings:
            raise NotConfigured
        db = db_settings['db']
        user = db_settings['user']
        passwd = db_settings['passwd']
        host = db_settings['host']
        table = db_settings['table']
        return cls(db, user, passwd, host, table)

    def open_spider(self, spider):
        self.conn = psycopg2.connect(dbname=self.db,
                                     user=self.user,
                                     password=self.passwd,
                                     host=self.host)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        sql = ''.join(['INSERT INTO {} '.format(self.table),
                       '(title, domain, link, datetime, subtitle, text, views, category) ',
                       'VALUES ( %s, %s, %s, %s, %s, %s, %s, %s)'])

        title = item.get("title")[0]
        domain = item.get("domain")[0]
        link = item.get("link")[0]
        date = item.get("date")[0]
        if "time" in item.keys():
            time = item.get("time")[0]
            if domain == media_config['hromadske']['domain']:
                # Громадське повертає дані з часом на 3 години менше ніж насправді
                # При перегляді в браузері це можно помітити як splash невірних даних
                # які коригуються в ту саму секунду
                # Але це відбувається javascript'ом а скрапі його не виконує
                date_time = datetime.combine(date, time) + timedelta(hours=3)
            else:
                date_time = datetime.combine(date, time)
        else:
            time = None
            date_time = date
        if "subtitle" in item.keys():
            subtitle = item.get("subtitle")[0]
        else:
            subtitle = None
        if "text" in item.keys():
            text = item.get("text")[0]
        else:
            text = None
        if "views" in item.keys():
            views = item.get("views")[0]
        else:
            views = None
        if "category" in item.keys():
            category = item.get("category")[0]
        else:
            category = None

        self.cursor.execute(sql,
                            (
                                title,
                                domain,
                                link,
                                date_time,
                                subtitle,
                                text,
                                views,
                                category
                            )
                            )
        self.conn.commit()
        return item

    def close_spider(self, spider):
        self.conn.close()
