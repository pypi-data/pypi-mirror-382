[![Version][version-image]][pypi-url]
[![Supported Python Version][py-versions-image]][pypi-url]
[![Downloads][downloads-image]][pypi-url]
[![Build Status][build-image]][build-url]

---

# Magic-i18n

Internationalization with special contextvars magic.


Key features:

- Relies on a mechanism of implicit context passing for asynchronous functions.
- Supports template formatting via %.
- Texts are defined separately from their usage location and passed as variables.
- Supports temporary (local) language overrides.
- Can be used both standalone and within ASGI applications.
- Utility for checking the correctness of texts for CICD.


Provides:

- container for text/template variations,
- language context manager,
- lazy template for partial text formatting,
- middleware for ASGI-compatible frameworks.
- checking utility.


## Install

```sh
pip install magic-i18n
```


## Declaration and basic usage

```python
from magic_i18n import Text, set_default_language, language

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

Context manager for temporarily changing the current language.

```python
with language('ru'):
    print(message % name)

with language(language) as lang:
    log.debug('Send with language %s', lang)
    print(message % name)
```

Get a string in the specified language

```python
print(message | 'ru')
print(message | lang)
```

## Template formatting

Template in different languages

```python
message = Text(en='hello ${name}', ru='привет ${name}')

print(message % 'Alex')  
print(message % ('Alex',))  
print(message % {'name': 'Alex'})  
# all prints `привет Alex` (ru - default language)
```

Partial formatting and deferred evaluation.

```python
lazy_template = Text(en='hello ${name}, open ${target}', ru='привет ${name}, открой ${target}')

print(lazy_template)
# print `привет ${name}, открой ${target}`

lazy_template % 'Alex'
print(lazy_template)
# print `привет Alex, открой ${target}`

lazy_template % 'Telegram'
print(lazy_template)
# print `привет Alex, открой Telegram`

lazy_template % {'target': 'Site'}  # set or replace
print(lazy_template)
# print `привет Alex, открой Site`

lazy_template(target='Calc')  # set or replace
print(lazy_template | 'en')
# print `hello Alex, open Calc`
```


## ASGI middleware
The ASGI middleware retrieves the language from the `Accept-Language` header 
and sets it as the current language if it's present in the `accept_languages` option.

Options:
- `application` - wrapped ASGI application.
- `default_language` - (default: en) Used when the user's language is unknown or 
    unavailable. This is the default only for ASGI and does not call `set_default_language`.
- `accept_languages` - list of available languages. The `default_language` must be included 
    in this list.

```python
application = I18nMiddleware(
    application,
    default_language='en',
    accept_languages=['en', 'ru'],
)
```

The header parser pattern `r'([a-zA-Z]{2}[-a-zA-Z0-9]*)'` can be modified in 
`header_parser` class attribute.

```python
I18nMiddleware.header_parser = re.compile(...)
```


## Linter

Provides:
- Check for required languages
- Check that all versions of the text templates have the same arguments.
- Prohibit text duplication
- Spell check (requires pyspellchecker)

```bash
$ magic-i18n --help
...

$ magic-i18n example.lint_erorrs
Run magic-i18n linter
  load [examples.lint_errors]
5 text objects found
[check-arguments] Text(asd | AD4JT53R): The `ru` arguments differ from fallback
[check-arguments] Text(asd ${a} | ADJ6CPYN): The `ru` arguments differ from fallback
[deny-doubles] Text(asd ${a} | ADJ6CPYN): Double detected
[required-languages] Text(asd проверка % & тест? | C2E2VTY): Required language(s) `en` are not provided
[required-languages] Text(asd | AD4JT53R): Required language(s) `en` are not provided
Failed with 5 errors
```


<!-- Badges -->
[pypi-url]: https://pypi.org/project/magic-i18n
[version-image]: https://img.shields.io/pypi/v/magic-i18n.svg
[py-versions-image]: https://img.shields.io/pypi/pyversions/magic-i18n.svg
[downloads-image]: https://img.shields.io/pypi/dm/magic-i18n.svg
[build-url]: https://github.com/scailer/magic-i18n/actions
[build-image]: https://github.com/scailer/magic-i18n/workflows/Tests/badge.svg
