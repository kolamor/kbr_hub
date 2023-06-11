import pathlib

import pytest
from scrapy import Selector
from scrapy.http import TextResponse

from ..kbr_parsers.helpers.jemes import Jemes
from ..kbr_parsers.items import BrandItem, BrandItemLoader

PATH_FILE = pathlib.Path(__file__).parent / 'test_fields.json'
XPATH_JSONS = pathlib.Path(__file__).parent / 'xpath_json'


class TestJemes:

    def test_load_jemes(self):
        path = PATH_FILE
        o = Jemes(file_path=path)
        assert o.test_xpath == '//div'


class TestItemLoader:

    def setup(self):
        context = {
            'url': 'http://testsource.org',
            'body': '<title>Title</title>',
            'encoding': 'utf-8'

        }
        self.response = TextResponse(**context)

    def test_base_loader(self):
        path = XPATH_JSONS / 'brand.json'
        loader = BrandItemLoader(response=self.response)
        loader.add_jemes(Jemes(file_path=path))
        loader.add_value('url', self.response.url)
        item = loader.load_item()
        assert isinstance(item, BrandItem)
        assert item['name'] == 'Title'


    # def test_forum_loader(self):
    #     jms = Jemes(file_path=PATH_FILE)
    #     body = '<body><div>wer</div></body>'
    #     selector = Selector(text=body)
    #     loader = ForumItem(self.response, selector=selector)
    #     loader.add_field('test')
    #     loader.replace_field('test', input_processor=Compose(Identity()), output_processor=Compose(TakeFirst()))
    #     loader.add_jemes(jms)
    #     assert isinstance(jms, Jemes)
    #     item = loader.load_item()
    #     assert item['test'] == '<div>wer</div>'
    #

