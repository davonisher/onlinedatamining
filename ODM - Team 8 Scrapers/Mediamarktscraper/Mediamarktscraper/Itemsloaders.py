#make new python file and name it: itemloader.py
from itemloaders.processors import TakeFirst, MapCompose
from scrapy.loader import ItemLoader


class mediamarktProductLoader(ItemLoader):

    default_output_processor = TakeFirst()
    rated_in = MapCompose(lambda x: x.strip('()'))
    price_in = MapCompose(lambda x: f"€{x}")
    url_in = MapCompose(lambda x: 'https://www.mediamarkt.nl/' + x )