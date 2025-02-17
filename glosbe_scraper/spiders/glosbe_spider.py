import scrapy
from urllib.parse import urljoin

class GlosbeSpider(scrapy.Spider):
    name = "glosbe_translations"
    allowed_domains = ["glosbe.com"]
    custom_settings = {
        'CONCURRENT_REQUESTS': 5,
        'DOWNLOAD_DELAY': 1,
        'RETRY_TIMES': 3,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 429],
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'translations_%(range_start)s_%(range_end)s.csv',
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    def __init__(self, range_start=0, range_end=1000, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.range_start = int(range_start)
        self.range_end = int(range_end)
        self.start_urls = [
            f"https://glosbe.com/topwords/en/te/{self.range_start}-{self.range_end}"
        ]

    def parse(self, response):
        words = response.css("li.mb-4 a::text").getall()
        
        for word in words:
            url = urljoin(response.url, f"/en/te/{word.strip().replace(' ', '%20')}")
            yield scrapy.Request(
                url,
                callback=self.parse_word,
                meta={'word': word.strip(), 'handle_httpstatus_list': [404]}
            )

    def parse_word(self, response):
        if response.status == 404:
            self.logger.warning(f"Missing page: {response.url}")
            yield {
                'english_word': response.meta['word'],
                'telugu_word': None,
                'status': 'missing'
            }
            return

        word = response.meta['word']
        translations = []
        
        # Extract translation pairs
        for pair in response.css('div.direction-pair'):
            english = pair.css('div.w-1/2.dir-aware-pr-1')
            telugu = pair.css('div.w-1/2.dir-aware-pl-1.dense')
            
            if not english or not telugu:
                continue
                
            eng_sentence = english.css('::text').get(default='').strip()
            tel_sentence = telugu.css('::text').get(default='').strip()
            eng_keyword = english.css('strong.keyword::text').get(default='').strip()
            tel_keyword = telugu.css('strong.keyword::text').get(default='').strip()

            translations.append({
                'english_word': word,
                'english_keyword': eng_keyword,
                'english_sentence': eng_sentence,
                'telugu_keyword': tel_keyword,
                'telugu_sentence': tel_sentence,
                'source_url': response.url
            })

        if not translations:
            yield {'english_word': word, 'status': 'no_translations'}
        else:
            yield from translations
