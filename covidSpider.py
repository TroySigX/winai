import re
import scrapy
from scrapy.crawler import CrawlerProcess

class CovidItem(scrapy.Item):
    region = scrapy.Field()
    total_case = scrapy.Field()
    new_case = scrapy.Field()
    active_case = scrapy.Field()
    total_death = scrapy.Field()
    new_death = scrapy.Field()
    total_recover = scrapy.Field()
    new_recover = scrapy.Field()

class CovidSpider(scrapy.Spider):
    name = 'covid'
    start_urls = ['https://www.worldometers.info/coronavirus']

    headers = {
        'user-agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
    }

    custom_settings = {
        'FEED_FORMAT': 'json',
        'FEED_URI': 'Resources/web scraping/covid/result.json'
    }

    def parse(self, response, **kwargs):
        item = CovidItem()

        data = response.css('td:nth-child(9) , td:nth-child(8) , td:nth-child(7) , td:nth-child(6) , td:nth-child(5) , td:nth-child(3) , td:nth-child(4) , td:nth-child(2)').extract()

        command = ['region', 'total_case', 'new_case', 'total_death', 'new_death', 'total_recover', 'new_recover', 'active_case']
        for i in range(0, len(data) - 7, 8):
            for j in range(8):
                begin = [x.start() for x in re.finditer('<', data[i + j])]
                end = [x.start() for x in re.finditer('>', data[i + j])]
                for k in range(0, len(end) - 1):
                    S = end[k] + 1
                    T = begin[k + 1]
                    res = data[i + j][S : T].strip()
                    if j == 0:
                        if res != '':
                            item[command[j]] = res
                            break
                    else:
                        if res == '':
                            res = '0'
                        else:
                            res = res.replace('+', '')
                        item[command[j]] = res
                        break
            yield item



if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(CovidSpider)
    process.start()