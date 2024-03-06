import scrapy
from coolbluescraper.items import CoolbluescraperItem
from coolbluescraper.itemloaders import CoolblueProductLoader

class CoolbluespiderSpider(scrapy.Spider):
    name = 'coolbluespider'
    allowed_domains = ['www.coolblue.nl']
    start_urls = ['https://www.coolblue.nl/laptops/gaming-laptops']

    def parse(self, response):
        products= response.css('div[class*="product-grid__card"]')
        #looping through products and extracting brand, model, price, number of custumers that rated it, number of stars, & url
        for product in products:
            if not product.css('a.link::attr(title)').get():
                continue
            laptop= CoolblueProductLoader(item=CoolbluescraperItem(), selector=product)
            stars = product.css('div.review-stars__icon svg[class*="green"]')
            if product.css('div.product-label.product-label--primary'):
                laptop.add_css('Coolblues_keuze', 'span[class*="dynamic-highlight__value"]::text')
            else:
                laptop.add_value('Coolblues_keuze', 'No')
            #get all values for each product
            laptop.add_css('name', 'a.link::attr(title)')
            laptop.add_css('gaming_videocard', 'span[data-component*="Gaming videokaart"]::text',re='  (.*)\n')
            laptop.add_css('processor', 'span[data-component*="Processor"]::text',re='  (.*)\n')
            laptop.add_css('screen_size', 'span[data-component*="Schermdiagonaal"]::text',re='  (.*)\n')
            laptop.add_css('price','strong[class*="sales-price__current"]::text')
            laptop.add_css('reviews', 'span.review-rating__reviews.text--truncate::text', re='\n  (.*)')
            laptop.add_value('stars',len(stars))
            laptop.add_css('url','a.link::attr(href)')

            yield laptop.load_item()
        #check if there are more pages and get the info of those products as well    
        next_page = response.css('[rel="next"] ::attr(href)').get()
        #if next_page has a url, it will use that url for the parse function 
        if next_page is not None:
            next_page_url = next_page
            yield response.follow(next_page_url, callback=self.parse)
