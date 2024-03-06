# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
import psycopg2
import logging

#class MediamarktscraperPipeline:
#    def __init__(self):
#        self.names_seen = set()
#
#    def process_item(self, item, spider):
#        adapter = ItemAdapter(item)
#        if adapter['brand'] in self.names_seen:
#            raise DropItem(f"Duplicate item found: {item!r}")
#        else:
#            self.names_seen.add(adapter['brand'])
#            return item
        
class SavingToPostgresPipeline(object):

    def __init__(self):
        self.create_connection()


    def create_connection(self):
        self.connection = psycopg2.connect(
            host="localhost",
            database="laptops",
            user="postgres",
            password="0000",
            port="5433"
            )
        
        self.curr = self.connection.cursor()


    def process_item(self, item, spider):
        self.store_db(item)
        #we need to return the item below as scrapy expects us to!
        return item

    def store_db(self, item):
        try:
            self.curr.execute("""INSERT INTO laptops (brand, model, price, rated, stars, url) VALUES (%s, %s, %s, %s, %s, %s)""",
            (item['brand'], item['model'], item['price'], item['rated'], item['stars'], item['url'])
            )
            self.connection.commit()
            logging.info(f"Data stored in PostgreSQL database: {item}")

        except psycopg2.IntegrityError as e:
            print(e)
            self.connection.rollback()
        except BaseException as e:
            print(e)
            self.connection.rollback()