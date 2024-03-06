import scrapy
import psycopg2
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

#This meta_critic_spider was written by Keije Mantje

#Using the CrawlSpider to crawl to all the critic reviews of all the pc games
class MetacriticspiderSpider(CrawlSpider):
    name = "meta_critic_spider"
    allowed_domains = ['metacritic.com']
        #Set the start url of the scraper on where the scraper should begin
    start_urls = ['https://www.metacritic.com/browse/games/release-date/available/pc/metascore']

        #Set rules for the CrawlSpider on which url the scraper should crawl
    rules = (
        #First rule is to extract the links where game/pc is in the url
        Rule(LinkExtractor(allow='game/pc', deny = 'critic-reviews')),

        #Second rule is to allow the critic reviews of the previous pages and then call the parse_item to those pages that will store the data
        Rule(LinkExtractor(allow = 'critic-reviews'), callback= 'parse_item')
        )


    #Set the parse_item
    def parse_item(self, response):
        #Extract the game title from the critic review page of that game
        game_title = response.xpath('//h1/text()').get()

        reviews_elements = response.css('#main.col.main_col div.review_content')

        #Loop through all the reviews of the critic review and store every information in a row
        for review_element in reviews_elements:
            
            yield {
                'game_title': game_title,
                'critic_name': review_element.css('div.source a.external::text').get(),
                'meta_score': review_element.css('div.review_grade div.indiv::text').get(),
                'review_date': review_element.xpath('normalize-space(.//div[@class="date"]/text())').get(),
                
                #Using normalize space to get rid of the extra spaces in the review body text to clean this column
                'review_text': review_element.xpath('normalize-space(.//div[@class="review_body"]/text())').get()
                }