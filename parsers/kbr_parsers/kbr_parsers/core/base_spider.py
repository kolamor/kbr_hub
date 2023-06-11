import pathlib
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Type

from scrapy.http import Response

from .base_parser import BaseParser
from ..helpers.jemes import Jemes
from ..items import ItemLoaderEx, PageItemLoader, BrandItemLoader, KeyboardItemLoader, KeycapItemLoader, \
    SwitchItemLoader

import scrapy


class BaseSpider(scrapy.Spider, ABC):
    page_loader_cls: Type[ItemLoaderEx] = PageItemLoader
    brand_loader_cls: Type[ItemLoaderEx] = BrandItemLoader
    keyboard_loader_cls: Type[ItemLoaderEx] = KeyboardItemLoader
    keycap_loader_cls: Type[ItemLoaderEx] = KeycapItemLoader
    switch_loader_cls: Type[ItemLoaderEx] = SwitchItemLoader

    page_parser: BaseParser
    brand_parser: BaseParser
    keyboard_parser: BaseParser
    keycap_parser: BaseParser
    switch_parser: BaseParser

    page_parser_cls: Type[BaseParser]
    brand_parser_cls: Type[BaseParser]
    keyboard_parser_cls: Type[BaseParser]
    keycap_parser_cls: Type[BaseParser]
    switch_parser_cls: Type[BaseParser]

    version = '0.0.1'

    @dataclass
    class jemes:
        page: Jemes
        brand: Jemes
        keyboard: Jemes
        keycap: Jemes
        switch: Jemes
        
    def __init__(self, *args, **kwargs):
        self.setup()
        super().__init__(*args, **kwargs)

    @abstractmethod
    def setup(self):
        """Вызывается при инициализации паука. тут можно настраивать классы итемов и ставить xpath"""
        raise NotImplementedError


class DefaultSpider(BaseSpider):
    base_url: str

    def __init__(self, *args, **kwargs):
        self.page_parser_cls = PageParser
        self.keyboard_parser_cls = KeyboardParser
        self.keycap_parser_cls = KeycapParser
        self.switch_parser_cls = SwitchParser
        self.brand_parser_cls = BrandParser

        super().__init__(*args, **kwargs)

    def setup(self):
        self.jemes.page = Jemes(pathlib.Path(__file__).parent.parent /'spiders' / self.name / "xpath_json/page.json")
        self.jemes.brand = Jemes(pathlib.Path(__file__).parent.parent / 'spiders' / self.name / "xpath_json/brand.json")
        self.jemes.keyboard = Jemes(pathlib.Path(__file__).parent.parent / 'spiders' / self.name / "xpath_json/keyboard.json")
        self.jemes.keycap = Jemes(pathlib.Path(__file__).parent.parent / 'spiders' / self.name / "xpath_json/keycap.json")
        self.jemes.switch = Jemes(pathlib.Path(__file__).parent.parent /'spiders' / self.name / "xpath_json/switch.json")

        self.page_parser = self.page_parser_cls(loader_cls=self.page_loader_cls, jemes=self.jemes.page,
                                                base_url=self.base_url)
        self.brand_parser = self.brand_parser_cls(loader_cls=self.brand_loader_cls, jemes=self.jemes.brand,
                                                  base_url=self.base_url)
        self.keyboard_parser = self.keyboard_parser_cls(loader_cls=self.keyboard_loader_cls, jemes=self.jemes.keyboard,
                                                        base_url=self.base_url)
        self.keycap_parser = self.keycap_parser_cls(loader_cls=self.keycap_loader_cls, jemes=self.jemes.keycap,
                                                    base_url=self.base_url)
        self.switch_parser = self.switch_parser_cls(loader_cls=self.switch_loader_cls, jemes=self.jemes.switch,
                                                    base_url=self.base_url)

    def parse(self, response, **kwargs):
        yield from self.parse_ext(response=response)

    def parse_ext(self, response: Response):
        yield from self._parse_ext(response=response)

        if self.page_parser.is_self_page(response=response):
            for item_page in self.page_parser.parse(response=response):
                if not item_page:
                    break

                _urls = []
                for k, v in item_page.items():
                    if k.endswith(('_url', '_urls')):
                        _ = _urls.extend(v) if isinstance(v, list) else _urls.append(v)

                requests = response.follow_all(_urls)
                for r in requests:
                    yield r

    def _parse_ext(self, response: Response):
        parsers = [self.keyboard_parser, self.keycap_parser, self.brand_parser, self.switch_parser]
        for parser in parsers:
            if parser.is_self_page(response=response):
                yield from parser.parse(response=response)


class PageParser(BaseParser):
    @classmethod
    def is_self_page(cls, response: Response):
        return True


class BrandParser(BaseParser):
    pass


class KeyboardParser(BaseParser):
    pass


class KeycapParser(BaseParser):
    pass


class SwitchParser(BaseParser):
    pass
