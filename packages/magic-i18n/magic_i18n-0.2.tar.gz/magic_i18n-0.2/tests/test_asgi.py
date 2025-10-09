from unittest.mock import AsyncMock

import pytest

from magic_i18n import DEFAULT_LANG, LANG, I18nMiddleware


DATA = {
    'no-http': ('en', {'type': 'lifespan'}),
    'no-headers': ('en', {'type': 'http'}),
    'any-lang': (
        'en', {'type': 'http', 'headers': [(b'accept-language', b'*')]}
    ),
    'simple': (
        'ru', {'type': 'http', 'headers': [(b'accept-language', b'ru')]}
    ),
    'two-variants': (
        'fr', {'type': 'http', 'headers': [(b'accept-language', b'fr, en')]}
    ),
    'unknown-lang': (
        'en', {'type': 'http', 'headers': [(b'accept-language', b'by')]}
    ),
    'unknown-first-lang': (
        'ru', {'type': 'http', 'headers': [(b'accept-language', b'by, ru;q=0.9')]}
    ),
    'complex': (
        'fr', {
            'type': 'http',
            'headers': [(b'accept-language', b'de-DA, de;q=0.9, nw;q=0.8, fr;q=0.7, *;q=0.5')]
        }
    ),
    'with-location': (
        'en-US', {'type': 'http', 'headers': [(b'accept-language', b'en-US,en;q=0.9')]}
    ),
    'many-headers': (
        'en', {'type': 'http', 'headers': [(b'accept-language', b'*'), (b'pragma', b'no-cache')]}
    ),
}


@pytest.fixture(params=list(DATA.values()), ids=list(DATA.keys()))
def data(request):
    return request.param[0], request.param[1]


async def test_I18nMiddleware(data):
    lang, scope = data

    async def app(scope, receive, send):
        assert LANG.get(DEFAULT_LANG) == lang

    i18n_app = I18nMiddleware(app, 'en', ['en', 'ru', 'fr', 'en-US'])

    await i18n_app(scope, AsyncMock(), AsyncMock())
