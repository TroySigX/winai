import scrapy
from scrapy.crawler import CrawlerProcess

class BillboardItem(scrapy.Item):
    name = scrapy.Field()
    artist = scrapy.Field()

class BillboardSpider(scrapy.Spider):
    name = 'billboard'
    start_urls = ['https://www.billboard.com/charts/hot-100']

    headers = {
        'user-agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
    }

    custom_settings = {
        'FEED_FORMAT' : 'json',
        'FEED_URI' : 'Resources/web scraping/billboard/result.json'
    }

    def parse(self, response, **kwargs):
        item = BillboardItem()

        result = response.css('.chart-element__information')
        for x in result:
            item['name'] = x.css('.text--truncate.color--primary').css('::text').extract_first()
            item['artist'] = x.css('.text--truncate.color--secondary').css('::text').extract_first()
            yield item

if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(BillboardSpider)
    process.start()