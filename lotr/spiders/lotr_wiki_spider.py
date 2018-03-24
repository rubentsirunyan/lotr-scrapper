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
        self.sections = {
            'characters':  'div#mw-content-text div div#mw-pages div.mw-content-ltr table tr td',
            'next_page': 'div.wikia-paginator ul li a.paginator-next::attr(href)',
            'info': 'section.pi-item div.pi-item',
            'info_key': 'h3.pi-data-label::text',
            'info_value': 'div.pi-data-value.pi-font *::text',
            'name': 'header#PageHeader.page-header h1.page-header__title::text',
            'see_more': "//h3/span[contains(text(), '{}')]/parent::*/following-sibling::ul[1]/li/b/text()"
        }

    def parse(self, response):

        for td in response.css(self.sections['characters']):
            for li in td.css('ul li'):
                url = response.urljoin(li.css('a::attr(href)').extract_first())
                yield scrapy.Request(url=url,
                                     callback=self.parse_character_details)

        next_page = response.css(self.sections['next_page']).extract_first()
        if next_page is not None:
            yield response.follow(next_page,
                                  callback=self.parse)

    def parse_character_details(self, response):
        self.info_dict = {}
        for section in response.css(self.sections['info']):
            if "see more" in section.css(self.sections['info_value']).extract():
                self.info_dict[section.css(self.sections['info_key']).extract_first()] = self.parse_see_more(response, section.css(self.sections['info_key']).extract_first())
            elif "Titles" in section.css(self.sections['info_key']).extract_first()\
                 or "Other names" in section.css(self.sections['info_key']).extract_first()\
                 or "Weapon" in section.css(self.sections['info_key']).extract_first():
                self.info_dict[section.css(self.sections['info_key']).extract_first()] = self.parse_more_details(section.css(self.sections['info_value']).extract())
            else:
                self.info_dict[section.css(self.sections['info_key']).extract_first()] = ''.join(self.parse_more_details(section.css(self.sections['info_value']).extract()))
        self.info_dict['Name'] = response.css(self.sections['name']).extract_first()
        yield self.info_dict

    def parse_see_more(self, response, title):
        self.response = response
        self.title = title
        return self.response.xpath(self.sections['see_more'].format(self.title.title())).extract()

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
