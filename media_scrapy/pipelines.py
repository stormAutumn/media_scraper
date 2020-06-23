from scrapy.exporters import CsvItemExporter
from datetime import datetime


class CsvPipeline(object):
    def __init__(self):
        now_str = datetime.now().strftime("%Y-%m-%d--%H-%M")
        path = f'./result/{now_str}.csv'
        self.file = open(path, 'wb')
        self.exporter = CsvItemExporter(self.file, encoding='utf-8')
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

