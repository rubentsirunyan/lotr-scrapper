import scrapy
import re


class LotrWikiSpider(scrapy.Spider):
    name = "lotrwiki"
    start_urls = [
        'http://lotr.wikia.com/wiki/Category:Characters',
    ]

    def parse(self, response):
        # page = response.url.split("/")[-1]
        # filename = 'pages-%s.html' % page
        # with open(filename, 'wb') as f:
        #     f.write(response.body)
        characters = []
        for td in response.css('div#mw-content-text.mw-content-ltr.mw-content-text div div#mw-pages div.mw-content-ltr table tr td'):
            for li in td.css('ul li'):
                url = response.urljoin(li.css('a::attr(href)').extract_first())
                # self.log(url)
                yield scrapy.Request(url=url,callback=self.parse_character_details)

        next_page = response.css('div.wikia-paginator ul li a.paginator-next.button.secondary::attr(href)').extract_first()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_character_details(self, response):
        info = response.css('section.pi-item.pi-group.pi-border-color div.pi-item.pi-data.pi-item-spacing.pi-border-color')
        info_dict = {}
        for section in info:
            if "see more" in section.css('div.pi-data-value.pi-font *::text').extract():
                info_dict[section.css('h3.pi-data-label.pi-secondary-font::text').extract_first()] = self.parse_see_more(response, section.css('h3.pi-data-label.pi-secondary-font::text').extract_first())
            elif "Titles" in section.css('h3.pi-data-label.pi-secondary-font::text').extract_first() or "Other names" in section.css('h3.pi-data-label.pi-secondary-font::text').extract_first() or "Weapon" in section.css('h3.pi-data-label.pi-secondary-font::text').extract_first():
                info_dict[section.css('h3.pi-data-label.pi-secondary-font::text').extract_first()] = self.parse_more_details(section.css('div.pi-data-value.pi-font *::text').extract())
            else:
                info_dict[section.css('h3.pi-data-label.pi-secondary-font::text').extract_first()] = ''.join(self.parse_more_details(section.css('div.pi-data-value.pi-font *::text').extract()))
        info_dict['Name'] = response.css('header#PageHeader.page-header div.page-header__main h1.page-header__title::text').extract_first()
        self.log(info_dict)
        yield info_dict

    def parse_see_more(self, response, title):
        return response.xpath("//h3/span[contains(text(), '{}')]/parent::*/following-sibling::ul[1]/li/b/text()".format(title.title())).extract()

    def parse_more_details(self, _list):
        expr = re.compile("\\[[0-9]\\]")
        for i in _list:
            if expr.match(i):
                _list.remove(i)
        _list = ''.join(_list).split(',')
        for i in _list:
            _list[_list.index(i)] = i.strip()
        return _list