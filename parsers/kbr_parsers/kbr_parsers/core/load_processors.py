import calendar
import datetime
import logging
import re
from typing import Union, Optional
from urllib.parse import urljoin, urlparse
import bs4
from scrapy import Selector
# from selfsec.sanitizers.sanitizer import HtmlSanitizer
# from selfsec.utils import LocalSettings
import dateparser
from itemloaders.processors import Compose

logger = logging.getLogger(__name__)


class NormalizeUrl:
    def __init__(self, base_url):
        self.base_url = base_url

    def __call__(self, value):
        if isinstance(value, list):
            norm_values = []
            for v in value:
                norm_values.append(self.normalize(v))
            return norm_values
        return self.normalize(value)

    def normalize(self, value):
        if value.startswith(('https://', 'http://', 'data:')):
            return value
        elif value.startswith('//'):
            protocol, *_ = urlparse(self.base_url)
            value = urljoin(f'{protocol}://', value)
        else:
            value = urljoin(self.base_url, value)
        return value


class NormalizeUrlWithLoaderContext(NormalizeUrl):
    """Нормализует урлы в Compose, scheme, netloc берет из response в loader_context"""

    base_url: str

    def __init__(self, base_url: str = None):
        super().__init__(base_url=base_url)

    def _setup_base_url(self, loader_context):
        protocol, netloc, *_ = urlparse(loader_context["response"].url)
        self.base_url = f"{protocol}://{netloc}"

    def __call__(self, value, loader_context=None):
        self._setup_base_url(loader_context=loader_context)
        return super().__call__(value=value)


class Iframe:
    """iframe[src] rename to a[href] """
    def __call__(self, value):
        iframe = Selector(text=value).xpath("//iframe").get()
        if iframe:
            soup = bs4.BeautifulSoup(value, 'lxml')
            for ifr in soup.select('iframe'):
                url = self.get_src(ifr)
                if not url:
                    logger.warning(f'{self.__class__.__name__} :: don\'n src-like attribute \n {value} \n {str(ifr)}')
                    continue
                sup = soup.new_tag('a')
                sup['href'] = url
                sup.string = url
                ifr.insert_after(sup)
                ifr.unwrap()
            value = str(soup)
        return value

    def get_src(self, tree):
        url = None
        try:
            url = tree['src']
        except KeyError as e:
            for key in tree.attrs:
                if 'src' in key:
                    return tree[key]
        return url


class Strip:
    def __init__(self, arg=None):
        self.arg = arg

    def __call__(self, value):
        if isinstance(value, list):
            new_value_list = [v.strip(self.arg) for v in value]
            return new_value_list
        value = value.strip(self.arg)
        if not value:
            return None
        return value


class Join:
    def __init__(self, arg=''):
        self.arg = arg

    def __call__(self, values):
        if isinstance(values, list):
            values = self.arg.join(values)
        return values


class Replace:
    def __init__(self, old, new, count=None):
        if count is None:
            self.replace_args = old, new
        else:
            self.replace_args = old, new, count

    def __call__(self, value):
        if value is None:
            return
        if isinstance(value, (list, tuple)):
            values = [v.replace(*self.replace_args) for v in value]
            return values
        value = value.replace(*self.replace_args)
        return value.replace(*self.replace_args)


# def default_sanitizer():
#     sanitizer = HtmlSanitizer(tags={
#         "a", "h1", "h2", "h3", "strong", "em", "p", "ul", "ol",
#         "li", "br", "sub", "sup", "hr", "img", "blockquote", "pre", "code"},
#         attributes={"a": ("href", "original", "title",),
#                     "img": ("src", "original", "title",),
#                     "blockquote": ("data-author", "data-cid",
#                                    "data-time")}, )
#     return sanitizer


class ReSearchID:
    re_compile = None
    skip_digit: bool

    def __init__(self, re_compile: re.compile = None, skip_digit: bool = True):
        if re_compile:
            self.re_compile = re_compile
        self.skip_digit = skip_digit

    def __call__(self, value: Union[str, list, int]) -> Union[str, list, int]:
        if isinstance(value, int):
            return value
        if isinstance(value, list):
            values = []
            for val in value:
                if not val.isdigit() and self.skip_digit:
                    val = self.search(value=val)
                values.append(val)
            return values
        if not value.isdigit() and self.skip_digit:
            value = self.search(value=value)
        return value

    def search(self, value):
        try:
            value = self.re_compile.search(value)[1]
        except (ValueError, TypeError) as e:
            pass
            # settings = LocalSettings.get()
            # if settings and settings.get('DEBUG_RE_SEARCH', None):
            #     logger.debug(f"{self.__class__.__name__}, value= {value}:: {self.re_compile}:: {e}, {e.args}")
        return value


class ReSearch(ReSearchID):
    """Копия, для понятности в коде"""
    pass


class UnixUtcTime:
    def __call__(self, value: datetime.datetime):
        try:
            if isinstance(value, datetime.date):
                # epoch_utc = int(datetime.datetime.timestamp(dtime_obj))
                # calendar учитывает timezone локальной машины
                value = int(calendar.timegm(value.utctimetuple()))
        except Exception as e:
            logger.debug(f"{self.__class__.__name__} :: {value} :: {e}, {e.args}")
        return value


class StrpTime:

    def __init__(self, format_time):
        self.format_time = format_time

    def __call__(self, value):
        if isinstance(value, (list, tuple)):
            value = value[0]
        if isinstance(value, (int, datetime.datetime)):
            return value
        if value.isdigit():
            value = datetime.datetime.fromtimestamp(int(value))
            return value
        if isinstance(value, str):
            try:
                value = datetime.datetime.strptime(value, self.format_time)
            except Exception as e:
                logger.debug(f"{self.__class__.__name__} :: {value} :: {e}, {e.args}")
        else:
            return value
        return value


def digit_to_int(value: str):
    return int(value) if value.isdigit() else value


class DeleteExpands:
    """del <a>Click to expand...</a>, <a>Нажмите для раскрытия...</a> ... """

    _texts = {'Click to expand...', 'Нажмите для раскрытия...', 'Нажмите, чтобы раскрыть...',
              'Genişletmek için tıkla ...'}

    def __call__(self, value):
        qoute_expand = Selector(text=value).xpath(self._create_check_xpath()).get()
        if qoute_expand:
            soup = bs4.BeautifulSoup(value, 'lxml')
            for ex in soup.select('a'):
                if ex.text in self._texts:
                    ex.decompose()
            value = str(soup)
        return value

    def _create_check_xpath(self):
        values = []
        for text in self._texts:
            value = f"//a[text() = '{text}']"
            values.append(value)
        xpath = ' | '.join(values)
        return xpath


class DelTag:
    def __init__(self, tag: str, attr: str, attr_value: str):
        self.tag = tag
        self.attr = attr
        self.attr_value = attr_value

    def __call__(self, value):
        soup = bs4.BeautifulSoup(value, 'lxml')
        tags = soup.find_all(self.tag, attrs={self.attr: self.attr_value})
        for ex in tags:
            ex.decompose()
        value = str(soup)
        return value


class DelDuplicates:
    def __call__(self, value):
        if value and isinstance(value, list):
            value = list(set(value))
        return value


class DefaultDateParser:
    """
    https://dateparser.readthedocs.io/en/v1.0.0/settings.html
    """
    # settings = {
    #     'DATE_ORDER': 'DMY'
    # }
    # assumes default order: MDY
    require_parts = ['day', 'month']
    relative_base: Optional[datetime.datetime] = None

    def __init__(self, date_order: str = 'DMY', relative_base: Optional[datetime.datetime] = None):
        self.date_order = date_order
        if relative_base:
            self.relative_base = relative_base

    def __call__(self, value):
        if not isinstance(value, (datetime.datetime, int)):
            try:
                value = dateparser.parse(value, settings=self.settings)
            except Exception as e:
                logger.debug(f'{self.__class__.__name__} :: {value} ::: {e}, {e.args}')
        return value

    @property
    def settings(self):
        settings = {
            'DATE_ORDER': self.date_order,
            'REQUIRE_PARTS': self.require_parts
        }
        if getattr(self, 'relative_base', None):
            settings.update({'RELATIVE_BASE': self.relative_base})
        return settings


def is_root_id(value: Union[str, int]):
    if isinstance(value, int):
        return value
    values_eq = ['/', ]
    values_endswith = ['index.php', 'forum.php', '/forum', 'forums.php']
    for v_eq in values_eq:
        if v_eq == value:
            return '0'
    for v_end in values_endswith:
        if value.endswith(v_end):
            return '0'
    return value


class FirstBlockquoteToDiv:
    def __init__(self, class_: str = 'postcontent restore'):
        self.class_ = class_

    def __call__(self, value):
        soup = bs4.BeautifulSoup(value, 'lxml')
        quote = soup.find('blockquote', class_=self.class_)
        quote.name = 'div'
        return str(soup)


class Picture(Iframe):
    """<Picture> <img>[like src ('data-src')] to src """
    def __call__(self, value):
        picture = Selector(text=value).xpath("//picture").get()
        if picture:
            soup = bs4.BeautifulSoup(value, 'lxml')
            for img in soup.select('img'):
                url = self.get_src(img)
                if not url:
                    logger.warning(f'{self.__class__.__name__} :: don\'n src-like attribute \n {value} \n {str(img)}')
                    continue
                if not url.startswith('http'):
                    try:
                        url = re.search(r'(https?://.+)', url)[1]
                    except TypeError:
                        continue
                img['src'] = url
            value = str(soup)
        return value


class ReplaceTags:
    """
    It replaces tag to new tag(name) for css selector
    """
    css_selector: str  # 'div.quotemain'
    new_tag_name: str  # 'blockquote'

    def __init__(self, css_selector: str = None, new_tag_name: str = None):
        self.css_selector = css_selector if css_selector else self.css_selector
        self.new_tag_name = new_tag_name if new_tag_name else self.new_tag_name

    def __call__(self, value):
        soup = bs4.BeautifulSoup(value, 'lxml')
        tags = soup.select(self.css_selector)
        if tags:
            for tag in tags:
                tag.name = self.new_tag_name
            value = str(soup)
        return value


class TakeLastDigitFromStr:
    """
    It takes first digit from revers string and returns digit or None

    value (str): '/retirement/14610-early-retirement.html'
    return (str): '14610'
    """

    def __call__(self, value: Union[list, str]) -> Union[str, None]:
        result = ''
        if isinstance(value, list):
            value = value[0]
        if isinstance(value, str):
            digit_found = False
            for x in value[::-1]:
                if x.isdigit():
                    result += x
                    if digit_found is False:
                        digit_found = True
                else:
                    if digit_found:
                        break
        return result[::-1] if result else None


class DelEmptyIframe:
    """
    It tries to find and delete empty iframe tags
    """

    def __call__(self, value):
        iframe = Selector(text=value).xpath("//iframe").get()
        if iframe:
            soup = bs4.BeautifulSoup(value, 'lxml')
            for ifr in soup.select('iframe'):
                url = Iframe().get_src(tree=ifr)
                if not url:
                    ifr.decompose()
            value = str(soup)
        return value


class StripList:
    """
    It strip whitespaces in every value from the list
    """

    def __call__(self, value: Union[list, tuple]) -> Union[list, tuple, None]:
        return [x.strip() for x in value if x.strip()]
