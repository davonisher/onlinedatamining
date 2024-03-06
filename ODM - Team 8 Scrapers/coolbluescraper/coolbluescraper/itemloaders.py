from itemloaders.processors import TakeFirst, MapCompose
from scrapy.loader import ItemLoader


class CoolblueProductLoader(ItemLoader):

    default_output_processor = TakeFirst()
    Coolblues_keuze_in=MapCompose(lambda x: ' '.join(x.strip().split()))
    gaming_videocard_in=MapCompose(lambda x: ' '.join(x.strip().split()))
    processor_in=MapCompose(lambda x: ' '.join(x.strip().split()))
    screen_size_in=MapCompose(lambda x: ' '.join(x.strip().split()))
    reviews_in = MapCompose(lambda x: ' '.join(x.strip().split()))
    price_in = MapCompose(lambda x: f"€{x}")
    url_in = MapCompose(lambda x: 'https://www.coolblue.nl/' + x )
