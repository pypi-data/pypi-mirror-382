from magic_i18n import Text, language, set_default_language


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

# Template in different languages
message = Text(en='hello ${name}', ru='привет ${name}')

# print `привет Alex` (ru - default language)
print(message % 'Alex')
print(message % ('Alex',))
print(message % {'name': 'Alex'})

# temporarily changing language
with language('en') as lang:
    # print `hello Alex` (en - temporal language)
    print(f'LANG={lang}', message % 'Alex')

# LazyTemplate enables partial formatting and deferred evaluation.
message = Text(en='hello ${name}, open ${target}', ru='привет ${name}, открой ${target}')

# get LazyTemplate from Text container
lazy_template = message
print(lazy_template, repr(lazy_template))
# print `привет ${name}, открой ${target}`

lazy_template = message % 'Alex'
print(lazy_template, repr(lazy_template))
# print `привет Alex, открой ${target}`

lazy_template % 'Telegram'
print(lazy_template | 'en')
# print `hello Alex, open Telegram`

lazy_template % {'target': 'Site'}
print(lazy_template | 'en')
# print `hello Alex, open Site`

lazy_template(target='Calc')
print(lazy_template | 'en')
# print `hello Alex, open Calc`
