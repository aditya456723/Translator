import scrapy
import pandas as pd

class GlosbeSpider(scrapy.Spider):
    name = "glosbe"
    allowed_domains = ["glosbe.com"]
    
    # Generate URLs dynamically
    start_urls = [f"https://glosbe.com/topwords/en/te/{i}-{i+1000}" for i in range(0, 13000, 1000)]

    def parse(self, response):
        words = response.css("li.mb-4 a::text").getall()

        for word in words:
            word_url = f"https://glosbe.com/en/te/{word.replace(' ', '%20')}"
            yield scrapy.Request(word_url, callback=self.parse_word, meta={'word': word})

    def parse_word(self, response):
        word = response.meta['word']
        english_sentences = response.css("div.w-1\\/2.dir-aware-pr-1::text").getall()
        telugu_sentences = response.css("div.w-1\\/2.dir-aware-pl-1.dense::text").getall()

        for eng, tel in zip(english_sentences, telugu_sentences):
            yield {
                'English Sentence': eng.strip(),
                'Telugu Sentence': tel.strip(),
                'English Keyword': word,
                'Telugu Keyword': tel.strip().split(" ")[0] if tel else None
            }
