import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

#https://www.metacritic.com/game/switch/the-legend-of-zelda-breath-of-the-wild

class CriticSpider(CrawlSpider):
    name = "user_critic_spider"
    start_urls = ['https://www.metacritic.com/']

    rules = (
        Rule(LinkExtractor(allow='game/pc', deny = 'user-reviews')),
        Rule(LinkExtractor(allow = 'user-reviews'), callback= 'parse_item')
        )
    
    def parse_item(self, response):
        game_title = response.css('h1::text').get()
        reviews_elements = response.css('#main.col.main_col div.review_content')
        for review_element in reviews_elements:   
            yield {
                'game_title': game_title,
                'user_name': review_element.css('div.name a::text').get(),
                'user_score': review_element.css('div.review_grade div.indiv::text').get(),
                'review_date': review_element.css('div.date::text').get(),
                'review_text': review_element.xpath('normalize-space(.//div[@class="review_body"]/span/text())').get()
                }            
            

            