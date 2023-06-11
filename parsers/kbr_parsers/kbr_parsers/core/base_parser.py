from typing import Union

from scrapy import Item
from scrapy.http import HtmlResponse, Response


class BaseParser:
    def __init__(self, *, loader_cls, base_url, jemes):
        self.base_url = base_url
        self.loader_cls = loader_cls
        self.jemes = jemes

    def parse(self, response: HtmlResponse) -> Union[Item, dict, None]:
        loader = self.loader_cls(response=response)
        loader = self.loader_setup(response=response, loader=loader)
        loader.add_jemes(self.jemes)
        yield loader.load_item()

    def loader_setup(self, response: HtmlResponse, loader):
        return loader

    @classmethod
    def is_self_page(cls, response: Response):
        raise NotImplementedError()
