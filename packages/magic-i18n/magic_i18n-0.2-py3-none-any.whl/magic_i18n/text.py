from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from copy import deepcopy
from string import Template
from typing import Any

from .utils import short_hash


LangType = str
DEFAULT_LANG: LangType = 'en'
LANG: ContextVar[LangType] = ContextVar('lang')
TEXT_REGISTRY: list['Text'] = []


def set_default_language(lang: LangType) -> None:
    ''' Global set default language '''
    global DEFAULT_LANG  # noqa PLW0603
    DEFAULT_LANG = lang


@contextmanager
def language(lang: LangType) -> Iterator[LangType]:
    '''
        This is a context manager for temporarily changing the current language.

        ```
        with language('ru'):
            send(message % name)

        with language(user.language) as lang:
            log.debug('Send with language %s', lang)
            send(message % name)
        ```
    '''
    origin_lang = LANG.get(DEFAULT_LANG)
    LANG.set(lang)

    yield lang

    LANG.set(origin_lang)


class Text(Template):
    '''
        Text class serves as a container for representing text in different languages.
        It automatically selects the appropriate language based on the current context.
        If a suitable translation isn't found, a fallback value or the default language
        is returned. For simple usage, the class behaves like a regular string,
        but it also allows for field replacement using a template with the operator.

        Declaration examples:

        ```
            from magic_i18n import Text, set_default_language

            # setup global default language, must be called before running application
            set_default_language('ru')

            # Basic init without translations, fallback only
            message = Text('text')
            print(message)  # print `text`

            # Text in different languages, with default language for non-defined languages
            message = Text(en='text', ru='текст')
            print(message)  # print `текст` (ru - default language)

            # Text in different languages, with fallback for non-defined languages
            message = Text('fail', en='text', ru='текст')
            print(message)  # print `текст` (ru - default language)
        ```

        For template strings, it behaves like a string requiring formatting via %.

        ```
            # Template in different languages
            message = Text(en='hello ${name}', ru='привет ${name}')

            # print `текст` (ru - default language)
            print(message % 'Alex')
            print(message % ('Alex',))
            print(message % {'name': 'Alex'})
        ```
    '''

    fallback: str
    translations: dict[LangType, str]
    args: dict[str, str]  # for lazy formatting

    @property
    def template(self) -> str:
        return self.translations.get(LANG.get(DEFAULT_LANG), self.fallback)

    @template.setter
    def template(self, value: str) -> None:
        raise TypeError('template is read-only')

    def __init__(self, fallback: str = '', **translations: str) -> None:
        self.fallback = fallback or translations.get(DEFAULT_LANG, list(translations.values())[0])
        self.translations = translations
        self.args = {}
        TEXT_REGISTRY.append(self)

    def __repr__(self) -> str:
        _args = ''

        if self.args:
            _args = ' ' + ' '.join(f'{k}={v!r}' for k, v in self.args.items())

        return f'Text({self.fallback}{_args} | {short_hash(self.fallback)})'

    def __call__(self, **data: Any) -> 'Text':  # noqa ANN401
        ''' Make filled in copy '''
        obj = self if self.args else deepcopy(self)
        obj.args.update({name: str(value) for name, value in data.items()})
        return obj

    def __str__(self) -> str:
        return self.safe_substitute(**self.args)

    def __mod__(self, data: Any) -> 'Text':  # noqa ANN401
        ''' Partial formatting '''
        _data: dict = {}
        ids = [_id for _id in self.get_identifiers() if _id not in self.args]

        match data:
            case dict():
                _data = data
            case tuple() | list() | set():
                if ids:
                    _data = dict(zip(ids, data, strict=False))
            case _:
                if ids:
                    _data = {ids[0]: data}

        return self(**_data)

    def __or__(self, lang: LangType) -> str:
        ''' Text in specified language '''
        with language(lang):
            return str(self)


class StrictText(Text):
    def __str__(self) -> str:
        return self.substitute(self.args)

    def __mod__(self, data: Any) -> Text:  # noqa ANN401
        ''' Strict formatting '''
        match data:
            case dict():
                return self(**data)

            case tuple() | list() | set():
                ids = self.get_identifiers()

                if len(ids) > len(data):
                    raise TypeError('not enough arguments for format string')

                if len(ids) < len(data):
                    raise TypeError('not all arguments converted during string formatting')

                _data = dict(zip(self.get_identifiers(), data, strict=True))
                return self(**_data)

            case _:
                ids = self.get_identifiers()

                if not ids:
                    raise TypeError('formatting not required')

                if len(ids) > 1:
                    raise TypeError('not enough arguments for format string')

                return self(**{ids[0]: data})
