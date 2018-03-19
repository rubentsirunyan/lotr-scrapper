import scrapy


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
            info_dict[section.css('h3.pi-data-label.pi-secondary-font::text').extract_first()] = ''.join(section.css('div.pi-data-value.pi-font *::text').extract())
        info_dict['name'] = response.css('header#PageHeader.page-header div.page-header__main h1.page-header__title::text').extract_first(),
        yield info_dict
