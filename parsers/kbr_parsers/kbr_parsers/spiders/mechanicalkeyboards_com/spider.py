import re
from typing import Union
from urllib.parse import urljoin

import scrapy
from itemloaders.processors import Compose, TakeFirst
from scrapy import Item
from scrapy.http import Response, HtmlResponse

from ...core.base_spider import DefaultSpider
from ...core import base_spider
from ...core.load_processors import NormalizeUrl, Strip, Join, Replace

SCHEME = 'https'
HOST = 'mechanicalkeyboards.com'
B_URL = f"{SCHEME}://{HOST}/"

class BrandsSpider(DefaultSpider):
    base_url = urljoin(B_URL, 'shop/')
    name = "mechanicalkeyboards_com"
    # allowed_domains = []
    start_urls = [
        # "https://mechanicalkeyboards.com/shop/index.php?l=product_list&c=110",
        # "https://mechanicalkeyboards.com/shop/index.php?l=product_list&c=242",
        # "https://mechanicalkeyboards.com/shop/index.php?l=product_list&c=1229"  # other
        # "https://mechanicalkeyboards.com/shop/index.php?l=product_list&c=205"
        # "https://mechanicalkeyboards.com/shop/index.php?l=product_detail&p=3873",
        # "https://mechanicalkeyboards.com/shop/index.php?l=product_list&c=239",
        # "https://mechanicalkeyboards.com/shop/index.php?l=product_list&c=771",
        # "https://mechanicalkeyboards.com/shop/index.php?l=product_list&c=1178"

        "https://mechanicalkeyboards.com/shop/index.php?l=product_list&c=107",  # switches
        # "https://mechanicalkeyboards.com/shop/index.php?l=product_detail&p=103",
        # "https://mechanicalkeyboards.com/shop/index.php?l=product_detail&p=3008",
        # "https://mechanicalkeyboards.com/shop/index.php?l=product_detail&p=6915"
    ]

    def setup(self):
        self.keyboard_parser_cls = KeyboardParser
        self.switch_parser_cls = SwitchParser
        self.keycap_parser_cls = KeycapParser
        self.brand_parser_cls = BrandParser
        super().setup()


class BrandParser(base_spider.BrandParser):
    # def parse(self, response: HtmlResponse) -> Union[Item, dict, None]:
    #     for item in super().parse(response=response):
    #         if item['name'] == 'Other':
    #             yield
    #         else:
    #             yield item

    def loader_setup(self, response: HtmlResponse, loader):
        loader.add_value('url', response.url)
        loader.replace_field('name', output_processor=Compose(TakeFirst(),
                                                              lambda x: x.split('Keyboards')[0],
                                                              lambda x: x.strip()))
        loader.replace_field('avatar', output_processor=Compose(TakeFirst(), NormalizeUrl(base_url=self.base_url) ))
        return loader

    @classmethod
    def is_self_page(cls, response: Response):
        trig = response.xpath("//li[@class = 'trail-item'][last()]"
                              "/a[contains(text(), 'by Brand') or contains(text(), 'Other')]").get()
        return bool(trig)


class KeyboardParser(base_spider.KeyboardParser):
    def parse(self, response: HtmlResponse) -> Union[Item, dict, None]:
        for item in super().parse(response=response):
            item['brand'] = item['brand'].split(item['name'])[0].strip()
            if not item['brand']:
                item['brand'] = response.xpath("(//li[@class = 'trail-item'])[last()]//a/text()").get()
            item['name'] = item['name'].split(item['brand'])[-1].strip()
            if item['name'] == item['parent']:
                del item['parent']
            yield item

    def loader_setup(self, response: HtmlResponse, loader):
        loader.add_value('url', response.url)
        loader.replace_field('brand', output_processor=Compose(Join(), Replace('Keyboards', ''), Strip()))
        loader.replace_field('name', output_processor=Compose(TakeFirst(),
                                                              Replace('Keyboards', ''),
                                                              lambda x: x.replace('Mechanical Keyboard', ''),
                                                              Strip(),
                                                              # lambda x: x.split('Keyboards')[0],
                                                              ))
        loader.replace_field('avatar', output_processor=Compose(TakeFirst(), NormalizeUrl(base_url=self.base_url)))
        loader.replace_field('keycaps', output_processor=Compose(Join(''), Strip(), ))
        loader.replace_field('backlighting', output_processor=Compose(Join(''), Strip(), ))
        loader.replace_field('features', output_processor=Compose(Join('\n'), Strip(), ))
        loader.replace_field('description', output_processor=Compose(Strip(), Join('\n'), Strip(), ))
        loader.replace_field('photo_urls', output_processor=Compose(NormalizeUrl(base_url=self.base_url)))
        return loader

    @classmethod
    def is_self_page(cls, response: Response):
        trig = response.xpath("//li[@class = 'trail-item'][last()]"
                              "/a[contains(text(), 'Keyboards')"
                              " and not( contains(text(), 'Mechanical Keyboards'))]").get()
        trig2 = response.xpath("//li[@class = 'trail-end'][last()]/a[not(contains(text(), 'Keyboards'))]")
        trig3 = response.xpath("//h1[contains(text(),'Other')]/text()").get()
        if trig3:
            return False
        return all([trig, trig2])


class KeycapParser(base_spider.KeycapParser):
    @classmethod
    def is_self_page(cls, response: Response):
        return


class SwitchParser(base_spider.SwitchParser):
    def parse(self, response: HtmlResponse) -> Union[Item, dict, None]:
        for item in super().parse(response=response):
            self._lubed(item=item)
            if 'parent' in item:
                if not item['parent']:
                    del item['parent']

                item['parent'] = item['parent'].split(item['brand'])[0].strip()
                if item['name'] == item['parent'] or not item['parent']:
                    del item['parent']
            yield item

    def _lubed(self, item):
        if 'lubed' in item and item['lubed'] is None:
            del item['lubed']

    def loader_setup(self, response: HtmlResponse, loader):
        loader.add_value('url', response.url)
        loader.replace_field('photo_urls', output_processor=Compose(NormalizeUrl(base_url=self.base_url)))
        loader.replace_field('avatar', output_processor=Compose(TakeFirst(), NormalizeUrl(base_url=self.base_url)))
        loader.replace_field('parent', output_processor=Compose(TakeFirst(), Strip()))
        loader.replace_field('type',
                             output_processor=Compose(TakeFirst(), lambda x: x.lower(),
                                                      lambda x: 'click' if 'click' in x else x,
                                                      Strip(), ))
        sanit = lambda x: re.sub(r'UP TO \d+% QUANTITY DISCOUNT!?', '', x)
        sanit2 = lambda x: re.sub(r'Bulk quantity discount', '', x)
        sanit_tuple = (sanit, sanit2)
        loader.replace_field('description', output_processor=Compose(lambda x: [s.replace('\r', '') for s in x],
                                                                     Strip(), Strip('\n'), lambda x: [s for s in x if s],
                                                                     Join('\n'), Strip(), ))
        loader.replace_field('features', output_processor=Compose(Strip(),
                                                                  lambda x: [s for s in x if s],
                                                                  Join('\n'),
                                                                  *sanit_tuple,
                                                                  Strip(), ))
        loader.replace_field('brand', output_processor=Compose(Join(), Replace('Switches', ''), Strip()))
        loader.replace_field('actuation_force', output_processor=Compose(TakeFirst(), Replace('Actuation Force:', ''), Strip(), ))
        loader.replace_field('lubed', output_processor=Compose(Join('/n'),
                                                               lambda x: False if 'unlubed' in x.lower() else x,
                                                               lambda x: False if x and 'un-lubed' in x.lower() else x,
                                                               lambda x: True if x and 'lubed' in x.lower() else x,
                                                               lambda x: None if not isinstance(x, bool) else x
                                                               ))
        return loader

    @classmethod
    def is_self_page(cls, response: Response):
        trig = response.xpath("//h4[@class = 'name' and contains(text(), 'Switches')]/text()")
        return all([trig])
