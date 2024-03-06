import scrapy
import csv
import psycopg2
from Mediamarktscraper.items import mediamarktscaperItem
from Mediamarktscraper.Itemsloaders import mediamarktProductLoader

class mediamarktspiderSpider(scrapy.Spider):
    #name of spider
    name = 'mediamarktspider'
    #domain that will be scraped
    allowed_domains = ['mediamarkt.nl']
    #url of first page that will be scraped
    start_urls = ['https://www.mediamarkt.nl/nl/category/gaming-laptops-661.html']


    def parse(self, response):
        products= response.css('[data-test="mms-search-srp-productlist-item"]')
        #looping through products and extracting brand, model, price, number of custumers that rated it, number of stars, & url
        for product in products:
            laptop= mediamarktProductLoader(item=mediamarktscaperItem(), selector=product)
            stars = product.css('div.sc-gKPRtg.huMlOI')
            #get all values for each product
            laptop.add_css('brand', '[data-test="product-manufacturer"]::text')
            laptop.add_css('model', '[data-test="product-title"]::text')
            laptop.add_xpath('price','.//div[@class="sc-iveFHk fEflDt"]/div[2]/div/span[2]/text()')
            laptop.add_css('rated', '[data-test="mms-customer-rating"] span::text')
            laptop.add_value('stars',len(stars))
            laptop.add_css('url','a::attr(href)')

        #check if there are more pages and get the info of those products as well 
        next_page = response.css('[rel="next"] ::attr(href)').get()
        #if next_page has a url, it will use that url for the parse function 
        if next_page is not None:
            next_page_url = next_page
            yield response.follow(next_page_url, callback=self.parse)

            yield laptop.load_item()
            
            #store data to csv
            with open('mediamarkt_laptops.csv', 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([laptop.get_output_value('brand'), laptop.get_output_value('model'), laptop.get_output_value('price'), laptop.get_output_value('rated'), laptop.get_output_value('stars'), laptop.get_output_value('url')])