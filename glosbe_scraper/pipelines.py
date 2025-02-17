# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


import pandas as pd

class GlosbeScraperPipeline:
    def open_spider(self, spider):
        self.data = []

    def process_item(self, item, spider):
        self.data.append(item)
        return item

    def close_spider(self, spider):
        df = pd.DataFrame(self.data)
        df.to_excel("translations_data.xlsx", index=False)
