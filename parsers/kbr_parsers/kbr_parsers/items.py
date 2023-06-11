# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
from typing import Type

import scrapy
from itemloaders import ItemLoader
from itemloaders.processors import Compose, TakeFirst, Identity
from scrapy import Item

from .core.load_processors import NormalizeUrl, NormalizeUrlWithLoaderContext, Strip
from .helpers.jemes import Jemes

from .core.item_loader import CustomBaseItemLoader


class EmptyItemError(Exception):
    pass


class RequiredFieldsError(Exception):
    pass


def create_default_field():
    field = scrapy.Field(input_processor=Identity(), output_processor=TakeFirst())
    return field


def create_compose_field(*args):
    field = scrapy.Field(input_processor=Identity(), output_processor=Compose(*args))
    return field

class JemesItemLoader(CustomBaseItemLoader):
    def add_jemes(self, jemes: Jemes):
        if not isinstance(jemes, (Jemes, )):
            raise ValueError(f"add_jemes take 1 required positional argument type Jemes, not {type(jemes)}")
        for key in jemes:
            value = getattr(jemes, key)
            self.add_xpath(key, value)


class ItemLoaderEx(JemesItemLoader):
    def load_item(self):
        if not self:
            required_fields = self._get_required_fields_name()
            if required_fields:
                raise RequiredFieldsError(f"Fields {required_fields} is required but they is empty!")
            # else:
            #     raise EmptyItemError("Item is empty!")
        return super().load_item()


norm_urls = NormalizeUrlWithLoaderContext

class PageItem(Item):
    keyboard_urls = create_compose_field(norm_urls(), )
    brand_urls = create_compose_field(norm_urls(), )
    switch_urls = create_compose_field(norm_urls())
    keycap_urls = create_compose_field(norm_urls())
    next_urls = create_compose_field(norm_urls())


class PageItemLoader(ItemLoaderEx):
    default_item_class = PageItem


class BrandItem(Item):
    url = create_compose_field(TakeFirst(), norm_urls())
    name = create_compose_field(TakeFirst(), )
    description = create_default_field()
    avatar = create_compose_field(TakeFirst(), norm_urls())
    photo_urls = create_compose_field(norm_urls())
    media_urls = create_compose_field(norm_urls())


class BrandItemLoader(ItemLoaderEx):
    default_item_class = BrandItem


class KeyboardItem(Item):
    """
    Template:
        Physical Layout	ANSI
        Logical Layout	US QWERTY
        Frame Color	Black
        Primary LED Color	White
        Control LED Color	n/a
        Hotswap Sockets	No
        USB Key Rollover	6
        PS/2 Key Rollover	Full
        Multimedia Keys	Yes
        Switch Mount Type	Plate
        Built in Audio Port	No
        Built in Mic Port	No
        Interface(s)	USB,PS/2
        Windows Compatible	Yes
        Mac Compatible	Yes
        Linux Compatible	Yes
        Dimensions	5.60" x 14.30" x 1.20"
    """
    url = create_default_field()
    name = create_compose_field(TakeFirst(), )
    parent = create_compose_field(TakeFirst(), )
    brand = create_compose_field(TakeFirst(), )
    description = create_default_field()
    avatar = create_compose_field(TakeFirst(), norm_urls())
    product_price = create_compose_field(TakeFirst(), Strip())
    photo_urls = create_compose_field(norm_urls(), )
    media_urls = create_compose_field(norm_urls(), )
    switches = create_compose_field()
    keycaps = create_compose_field()
    backlighting = create_compose_field()
    features = create_compose_field()

    model = create_default_field()
    size = create_default_field()
    switch_stems = create_default_field()
    physical_layout = create_default_field()
    logical_layout = create_default_field()
    frame_color = create_default_field()
    primary_led_color = create_default_field()
    control_led_color = create_default_field()
    hotswap_sockets = create_default_field()
    usb_key_rollover = create_default_field()
    ps2_key_rollover = create_default_field()
    multimedia_keys = create_default_field()
    switch_mount_type = create_default_field()
    built_in_audio_port = create_default_field()
    built_in_mic_port = create_default_field()
    interfaces = create_default_field()
    windows_compatible = create_default_field()
    mac_compatible = create_default_field()
    linux_compatible = create_default_field()
    dimensions = create_default_field()

    other_info = create_compose_field()


class KeyboardItemLoader(ItemLoaderEx):
    default_item_class = KeyboardItem


class KeycapItem(Item):
    url = create_default_field()
    name = create_compose_field(TakeFirst(), )


class KeycapItemLoader(ItemLoaderEx):
    default_item_class = KeycapItem


class SwitchItem(Item):
    url = create_default_field()
    name = create_compose_field(TakeFirst(), )
    brand = create_compose_field(TakeFirst(), )
    description = create_default_field()
    avatar = create_compose_field(TakeFirst(), norm_urls())
    product_price = create_compose_field(TakeFirst(), Strip())
    photo_urls = create_compose_field(norm_urls(), )
    media_urls = create_compose_field(norm_urls(), )

    type = create_compose_field(TakeFirst(), )
    actuation_force = create_default_field()
    parent = create_default_field()
    lubed = create_default_field()
    features = create_compose_field()


class SwitchItemLoader(ItemLoaderEx):
    default_item_class = SwitchItem

