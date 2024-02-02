import scrapy
import re

class FilmsSpider(scrapy.Spider):
    name = "films"
    allowed_domains = ["ru.wikipedia.org"]
    start_urls = ["https://ru.wikipedia.org/wiki/Категория:Фильмы_по_алфавиту"]

    def clean(self, data):
        clean_syms = r'(\[|\()\w+.?(\]|\))|\xa0|\n|\\d|рус.|англ.|\[*?\]|/|\*|\(|\)|\[|\]|\,\ |\,'
        return ';'.join([text.strip() for text in data if not re.search(clean_syms, text)]).replace(',,,', ',').replace(',,', ',').split(',')

    def parse_film_info(self, response):

        title = response.css('table.infobox th.infobox-above *::text').get()
        genre = response.css('table.infobox[data-name="Фильм"] td.plainlist *[data-wikidata-property-id="P136"] *::text').getall()
        director = response.css('table.infobox td.plainlist span[data-wikidata-property-id="P57"] *::text').getall()
        country = response.css('table.infobox td.plainlist *[data-wikidata-property-id="P495"] span::text').getall()
        year = next((i for i in response.css('table.infobox tr:contains("Год")  *::text').getall() if len(i) == 4), None)

        yield {
            'Название': title,
            'Жанр': self.clean(genre),
            'Режиссер': self.clean(director),
            'Страна': self.clean(country),
            'Год': year
        }

    def parse(self, response):
        for link in response.css('div.mw-category a::attr(href)'):
            yield response.follow(link, callback=self.parse_film_info)

        next_page = response.xpath("//*[contains(text(), 'Следующая страница')]/@href").extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

