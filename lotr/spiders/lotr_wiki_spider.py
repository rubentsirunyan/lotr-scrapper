import re
import scrapy


class LotrWikiSpider(scrapy.Spider):
    """
    docstring
    """

    name = "lotrwiki"
    start_urls = [
        'http://lotr.wikia.com/wiki/Category:Characters',
    ]

    def __init__(self):
        self.ss = {
            'characters': 'div#mw-content-text div#mw-pages table tr td',
            'next_page': 'div.wikia-paginator a.paginator-next::attr(href)',
            'info': 'section.pi-item div.pi-item',
            'info_key': 'h3.pi-data-label::text',
            'info_value': 'div.pi-data-value.pi-font *::text',
            'name': 'header#PageHeader h1.page-header__title::text',
            'see_more_b': '//*[@id="{}" or @id="{}"]/parent::*/following-sibling::ul[1]/li/*[1]/text()',
            'see_more_no_b': '//*[@id="{}" or @id="{}"]/parent::*/following-sibling::ul[1]/li/text()',
        }

    def parse(self, response):

        for td in response.css(self.ss['characters']):
            for li in td.css('ul li'):
                url = response.urljoin(li.css('a::attr(href)').extract_first())
                yield scrapy.Request(url=url,
                                     callback=self.parse_character_details)

        next_page = response.css(self.ss['next_page']).extract_first()
        if next_page is not None:
            yield response.follow(next_page,
                                  callback=self.parse)

    def parse_character_details(self, response):
        self.i = {}
        for s in response.css(self.ss['info']):
            if "see more" in ''.join(s.css(self.ss['info_value']).extract()):
                self.i[s.css(self.ss['info_key']).extract_first()]\
                 = self.parse_see_more(response, s.css(self.ss['info_key']).extract_first())
            elif "Titles" in s.css(self.ss['info_key']).extract_first()\
                 or "Other names" in s.css(self.ss['info_key']).extract_first()\
                 or "Weapon" in s.css(self.ss['info_key']).extract_first():
                self.i[s.css(self.ss['info_key']).extract_first()]\
                 = self.parse_more_details(s.css(self.ss['info_value']).extract())
            else:
                self.i[s.css(self.ss['info_key']).extract_first()]\
                 = ''.join(self.parse_more_details(s.css(self.ss['info_value']).extract()))
        self.i['Name'] = response.css(self.ss['name']).extract_first()
        yield self.i

    def parse_see_more(self, response, title):
        self.r = response
        self.t1 = title.replace(' ', '_')
        self.t2 = title.title().replace(' ', '_')
        # if len(title.split()) > 2:
        #     self.t1 = '_'.join(self.t1.split())
        #     self.t2 = '_'.join(self.t2.split())
        if self.r.xpath(self.ss['see_more_b'].format(self.t1, self.t2)):
            return self.r.xpath(self.ss['see_more_b'].format(self.t1, self.t2)).extract()
        else:
            lst = self.r.xpath(self.ss['see_more_no_b'].format(self.t1, self.t2)).extract()
            lst = [i.replace("\n", '') for i in lst]
            return lst

    def parse_more_details(self, _list):
        self.expr = re.compile("\\[[0-9]\\]")
        self.list = _list
        for i in self.list:
            if self.expr.match(i):
                self.list.remove(i)
        self.list = ''.join(self.list).split(',')
        for i in self.list:
            self.list[self.list.index(i)] = i.strip()
        return self.list
