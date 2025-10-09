import re
import typing

from .text import LANG, LangType


Scope = typing.MutableMapping[str, typing.Any]
Message = typing.MutableMapping[str, typing.Any]

Receive = typing.Callable[[], typing.Awaitable[Message]]
Send = typing.Callable[[Message], typing.Awaitable[None]]
Application = typing.Callable[[Scope, Receive, Send], typing.Awaitable[None]]


class I18nMiddleware:
    '''
        The ASGI middleware retrieves the language from the `Accept-Language` header
        and sets it as the current language if it's present in the `accept_languages` option.

        Options:
        - `application` - wrapped ASGI application.
        - `default_language` - (default: en) Used when the user's language is unknown or
            unavailable. This is the default only for ASGI and does not call `set_default_language`.
        - `accept_languages` - list of available languages. The default_language must be included
            in this list.

        ```
            application = I18nMiddleware(
                application,
                default_language='en',
                accept_languages=['en', 'ru'],
            )
        ```

        The header parser pattern `r'([a-zA-Z]{2}[-a-zA-Z0-9]*)'` can be modified in
        `header_parser` class attribute.

        ```
            I18nMiddleware.header_parser = re.compile(...)
        ```

    '''
    app: Application
    default_language: LangType
    accept_languages: typing.Iterable[LangType]
    header_parser: re.Pattern = re.compile(r'([a-zA-Z]{2}[-a-zA-Z0-9]*)')

    def __init__(
        self,
        app: Application,
        default_language: LangType = 'en',
        accept_languages: typing.Iterable[LangType] | None = None,
    ) -> None:
        self.app = app
        self.default_language = default_language
        self.accept_languages = accept_languages or [default_language]

    def chose_language(self, header_value: str) -> LangType:
        for lang in self.header_parser.findall(header_value):
            if lang in self.accept_languages:
                return lang

        return self.default_language

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope['type'] == 'http':
            for name, value in scope.get('headers', []):
                if name == b'accept-language' and value:
                    LANG.set(self.chose_language(str(value, 'utf8')))

        await self.app(scope, receive, send)
