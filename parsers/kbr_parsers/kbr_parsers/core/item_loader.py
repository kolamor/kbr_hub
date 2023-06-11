import logging

import scrapy
from itemloaders.processors import TakeFirst
from scrapy import Field, Item
from scrapy.loader import ItemLoader
from itemloaders.common import wrap_loader_context


__all__ = ["CustomBaseItemLoader"]

logger = logging.getLogger(__name__)


class CustomBaseItemLoader(ItemLoader):
    """
    Загрузчик полей для Item.
    """
    fields_set = dict()

    _type = 'base'
    parent = None

    def __init__(self, response=None, selector=None, parent=None,  **context):
        super().__init__(selector=selector, response=response, parent=parent, **context)
        self.fields_set = self.default_item_class.fields

        if not context.get('skip_item_type'):
            self._add_field('_item_type', scrapy.Field(output_processor=TakeFirst()))
            self.add_value('_item_type', self.default_item_class.__name__)

        for name, field in self.default_item_class.fields.items():
            if not isinstance(field, Field):
                raise TypeError(f"Value `{name}` must be of type Field, not `{type(field)}`")
            self._add_field(name, field)
        self.__sub_loaders = dict()

    @property
    def type(self):
        return self._type

    def add_field(self, field_name: str, **field):
        """
        Добавляет после с именем `field_name`.

        :param field_name: название поля
        :return:
        """
        if field_name in self.fields_set:
            field = Field(self.fields_set[field_name], **field)
        else:
            field = Field(**field)
        self._add_field(field_name, field)

    def remove_field(self, field_name: str):
        """
        Позволяет удалить поле и его значение.

        :param field_name:
        :return:
        """
        self.clear_field(field_name)
        self.item.fields.pop(field_name)

    def clear_field(self, field_name: str):
        if not self.is_field_exists(field_name):
            raise KeyError(f"Field `{field_name}` not exists!")
        self.item._values.pop(field_name, None)
        self._values.pop(field_name, None)

    def replace_field(self, old_name: str, new_name: str = None, **field):
        """
        Меняет имя, а также метданные поля.

        >>> f = CustomBaseItemLoader()
        >>> f.add_field('message')
        >>> f.add_value('message', 'text')
        >>> f.load_item()
        {'message': ['text']}
        >>> f.replace_field('message', output_processor=TakeFirst())
        >>> f.load_item()
        {'message': 'text'}

        :param old_name: старое имя
        :param new_name: новое, если нужно переименовать
        :param input_processor: новый препроцессор, если нужно установить
        :param output_processor: новый постпроцессор, если нужно
        :return:
        """
        name = new_name or old_name
        value = self._values.get(old_name)
        self.remove_field(old_name)
        self.add_field(name, **field)
        if value:
            self.add_value(name, value)

    def is_field_exists(self, name):
        return name in self.item.fields

    def _add_field(self, name, field):
        if self.is_field_exists(name):
            pass
        self.item.fields[name] = field

    def _get_required_fields_name(self):
        return [y for y, x in self.item.fields.items() if x.get('required') and y not in self]

    def get_output_value(self, field_name):
        proc = self.get_output_processor(field_name)
        proc = wrap_loader_context(proc, self.context)
        try:
            return proc(self._values[field_name])
        except Exception as e:
            raise ValueError(
                f"Error with output processor {self.__name__} in {self.__str_processor_for(field_name)}:"
                f" field={field_name} value={self._values[field_name]} error='{e.__name__}: {str(e)}'")

    def __str_processor_for(self, field_name) -> str:
        proc = self.get_output_processor(field_name)
        if hasattr(proc, "functions"):
            # This is Compose(*functions)
            return f"{type(proc).__name__}({', '.join([getattr(x, '__name__', type(x).__name__) for x in proc.functions])})"
        else:
            return getattr(proc, '__name__', type(proc).__name__)

    def __contains__(self, item):
        return item in self._values

    def __len__(self):
        return len(self._values)

    def __bool__(self):
        if self._get_required_fields_name():
            return False
        else:
            return bool(self._values)


class ErrorCreate(Exception):
    pass


# class FbcItemCls:
#     """Класс фабрика классов items, возвращает класс одинакого _type """
#     cls_instance = {}
#
#     def __new__(cls):
#         raise ErrorCreate("Cannot be created, initialized")
    #
    # @classmethod
    # def _create(cls, _type, class_name):
    #     return type(class_name, (Item, _type), {})
    #
    # @classmethod
    # def get(cls, _type, class_name):
    #     if class_name not in cls.cls_instance:
    #         default_item_cls = cls._create(_type, class_name)
    #         cls.cls_instance.update({class_name: default_item_cls})
    #     else:
    #         default_item_cls = cls.cls_instance[class_name]
    #     return default_item_cls
