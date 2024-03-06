import scrapy
import psycopg2
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

# Database connection
connection = psycopg2.connect(
    host='localhost',
    database='game_details',
    user='postgres',
    password=' ',
    port='5432'
)
cursor = connection.cursor()

# Create tables if they don't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS metacritic_games (
        id SERIAL PRIMARY KEY,
        title VARCHAR (255),
        metascore INTEGER,
        userscore VARCHAR (255),
        release_date DATE,
        genre VARCHAR (255),
        developer VARCHAR (255),
        publisher VARCHAR (255),
        image VARCHAR (255),
        summary VARCHAR(500),
        awards VARCHAR (255)
    );
""")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS meta_critic_review (
        id SERIAL PRIMARY KEY,
        game_id INTEGER,
        game_title TEXT,
        critic_name TEXT,
        meta_score INTEGER,
        review_date DATE,
        review_text TEXT,
        FOREIGN KEY (game_id) REFERENCES metacritic_games (id)
    );
""")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_reviews (
        id SERIAL PRIMARY KEY,
        game_id INTEGER,
        game_title TEXT,
        user_name TEXT,
        user_score INTEGER,
        review_date DATE,
        review_text TEXT,
        FOREIGN KEY (game_id) REFERENCES metacritic_games (id)
    );
""")
connection.commit()

# Helper function to get game_id by title
def get_game_id_by_title(title):
    cursor.execute("SELECT id FROM metacritic_games WHERE title = %s", (title,))
    result = cursor.fetchone()
    return result[0] if result else None

# First spider (Tarantula) - Collects game details
class Tarantula(scrapy.Spider):
    name = "tarantula"
    allowed_domains = ["metacritic.com"]
    start_urls = ["https://www.metacritic.com/browse/games/release-date/available/pc/metascore?page={}".format(i) for i in range(0, 1)]

    def parse(self, response):
        self.log("I just visited: " + response.url)

        for game in response.css('tr'):
            game_url = game.css('a[href*="/game/"]::attr(href)').extract_first()  # Extract the game URL

            if game_url is not None:
                game_url = response.urljoin(game_url)  # Join the relative URL with the base URL
                request = scrapy.Request(game_url, callback=self.parse_item)  # Send a request to the game URL
                yield request
    #Calling the different selectors
    def parse_item(self, response):
        metacritic_game = {
            'Title': response.css('h1::text').extract_first(),
            'Metascore': response.css('span[itemprop="ratingValue"]::text').extract_first(),
            'Summary': response.css('span.blurb_expanded::text').get(),
            'Userscore': response.css('div.metascore_w.user.large.game.positive::text').extract_first(),
            'Release_date': response.css('li.summary_detail.release_data > span.data::text').extract_first(),
            'Genre': response.css('li.summary_detail.product_genre > span.data::text').extract_first(),
            'Developer': response.css('a[href*="/company/"]::text').extract_first().strip(),
            'Publisher': response.css('li.summary_detail.publisher > span.data > a::text').extract_first().strip(),
            'Image': response.css('img.product_image::attr(src)').extract_first(),
            'Awards': response.xpath('normalize-space(.//div[@class="ranking_title"]/a/text())').extract()
            
        }

        # Insert the data into the PostgreSQL database
        cursor.execute("""
            INSERT INTO metacritic_games (title, metascore, userscore, release_date, genre, developer, publisher, image, awards)
            VALUES (%(Title)s, %(Metascore)s, %(Userscore)s, %(Release_date)s, %(Genre)s, %(Developer)s, %(Publisher)s, %(Image)s, %(Awards)s);
        """, metacritic_game)
        connection.commit()

        yield metacritic_game
    # Closing the spider
    def close_spider(self, spider):
        self.cursor.close()
        self.connection.close()

# Second spider (CriticSpider) - Collects critic reviews
class CriticSpider(CrawlSpider):
    name = "redback"
    start_urls = ['https://www.metacritic.com/browse/games/release-date/available/pc/metascore']

    rules = (
        Rule(LinkExtractor(allow='game/pc', deny = 'user-reviews')),
        Rule(LinkExtractor(allow = 'user-reviews'), callback= 'parse_item')
        )

    def parse_item(self, response):
        game_title = response.css('h1::text').get()
        game_id = get_game_id_by_title(game_title)
        if not game_id:
            return

        reviews_elements = response.css('#main.col.main_col div.review_content')
        for review_element in reviews_elements:
            critic_review = {
                'game_id': game_id,
                'game_title': game_title,
                'critic_name': review_element.css('div.source a.external::text').get(),
                'meta_score': review_element.css('div.review_grade div.indiv::text').get(),
                'review_date': review_element.xpath('normalize-space(.//div[@class="date"]/text())').get(),
                'review_text': review_element.xpath('normalize-space(.//div[@class="review_body"]/text())').get()
            }

            # Insert the data into the PostgreSQL database
            cursor.execute("""
                INSERT INTO meta_critic_review (game_id, game_title, critic_name, meta_score, review_date, review_text)
                VALUES (%(game_id)s, %(game_title)s, %(critic_name)s, %(meta_score)s, %(review_date)s, %(review_text)s);
            """, critic_review)
            connection.commit()

            yield critic_review

# Third spider (UserReviewSpider)
class UserReviewSpider(CrawlSpider):
    name = "huntsman"
    allowed_domains = ['metacritic.com']
        #Set the start url of the scraper on where the scraper should begin
    start_urls = ['https://www.metacritic.com/browse/games/release-date/available/pc/metascore']

    rules = (
        #First rule is to extract the links where game/pc is in the url
        Rule(LinkExtractor(allow='game/pc', deny = 'critic-reviews')),

        #Second rule is to allow the critic reviews of the previous pages and then call the parse_item to those pages that will store the data
        Rule(LinkExtractor(allow = 'critic-reviews'), callback= 'parse_item')
        )

    def parse_item(self, response):
        game_title = response.css('h1::text').get()
        game_id = get_game_id_by_title(game_title)
        if not game_id:
            return

        reviews_elements = response.css('#main.col.main_col div.review_content')
        for review_element in reviews_elements:
            user_review = {
                'game_id': game_id,
                'game_title': game_title,
                'user_name': review_element.css('div.name a::text').get(),
                'user_score': review_element.css('div.review_grade div.indiv::text').get(),
                'review_date': review_element.css('div.date::text').get(),
                'review_text': review_element.xpath('normalize-space(.//div[@class="review_body"]/span/text())').get()
            }

            # Insert the data into the PostgreSQL database
            cursor.execute("""
                INSERT INTO user_reviews (game_id, game_title, user_name, user_score, review_date, review_text)
                VALUES (%(game_id)s, %(game_title)s, %(user_name)s, %(user_score)s, %(review_date)s, %(review_text)s);
            """, user_review)
            connection.commit()

            yield user_review

# Close the database connection at the end
def close_spider(self, spider):
    cursor.close()
    connection.close()

