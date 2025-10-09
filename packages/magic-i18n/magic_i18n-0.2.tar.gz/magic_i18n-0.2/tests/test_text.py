import asyncio
import random

import pytest

from magic_i18n import LANG, StrictText, Text, language, set_default_language


async def test_set_default_language():
    set_default_language('ru')
    set_default_language('en')


async def test_language_ok():
    LANG.set('en')

    assert LANG.get() == 'en'

    with language('ru'):
        assert LANG.get() == 'ru'

        with language('fr'):
            assert LANG.get() == 'fr'

        assert LANG.get() == 'ru'

    assert LANG.get() == 'en'


def test_Text_repr_ok():
    text = Text(en='text', ru='текст')
    assert repr(text) == 'Text(text | HOF2PRY)'

    text = Text('fallback', en='text', ru='текст')
    assert repr(text) == 'Text(fallback | GEMXUQQ)'

    text = Text('${a} fallback')
    assert repr(text) == 'Text(${a} fallback | NVGCEQY)'

    text = Text('${a} fallback') % 1
    assert repr(text) == 'Text(${a} fallback a=\'1\' | NVGCEQY)'


def test_Text_str_ok_simple():
    text = Text(en='plain text', ru='простой текст')

    with language('en'):
        assert str(text) == 'plain text'
        assert f'Is it {text}?' == 'Is it plain text?'
        assert str(text) + '.' == 'plain text.'
        assert ', '.join([str(text), str(text)]) == 'plain text, plain text'

    with language('ru'):
        assert str(text) == 'простой текст'
        assert f'Это {text}?' == 'Это простой текст?'
        assert str(text) + '.' == 'простой текст.'
        assert ', '.join([str(text), str(text)]) == 'простой текст, простой текст'


def test_Text_str_ok_template():
    text = Text(en='${a} text', ru='${a} текст')

    assert text | 'en' == '${a} text'
    assert text | 'ru' == '${a} текст'


def test_Text_call_ok():
    text = Text(en='hello ${name}', ru='привет ${name}')

    with language('en'):
        name, result = 'Alex', 'hello Alex'
        assert str(text(name=name)) == result

    with language('ru'):
        name, result = 'Алек', 'привет Алек'
        assert str(text(name=name)) == result

    text1 = text(name='Alex')
    text2 = text1(a=1)

    assert id(text) != id(text1)
    assert id(text1) == id(text2)


def test_Text_template_setter_fail():
    text = Text(en='hello ${name}', ru='привет ${name}')

    with pytest.raises(TypeError) as err:
        text.template = ''

    assert err.value.args == ('template is read-only', )


async def test_Text_str_ok_async():
    text = Text(en='plain text', ru='простой текст')

    async def _func(lang) -> str:
        await asyncio.sleep(.0001)

        with language(lang):
            return str(text)

    langs = [random.choice(['ru', 'en']) for x in range(1_000)]
    results = await asyncio.gather(*[_func(lang) for lang in langs])

    for lang, val in zip(langs, results, strict=False):
        assert text.translations.get(lang) == val


def test_Text_or_ok():
    text = Text(en='hello ${name}', ru='привет ${name}')

    assert text | 'ru' == 'привет ${name}'
    assert text | 'en' == 'hello ${name}'

    assert text % 'Алекс' | 'ru' == 'привет Алекс'
    assert text % 'Alex' | 'en' == 'hello Alex'


def test_Text_mod_ok_simple():
    assert str(Text('hello') % 'Alex') == 'hello'
    assert str(Text('hello') % ('Alex', 'else')) == 'hello'
    assert str(Text('hello') % {'name': 'Alex', 'a': 'else'}) == 'hello'


def test_Text_mod_ok_one_argument():
    assert str(Text('hello ${name}') % 'Alex') == 'hello Alex'
    assert str(Text('hello ${name}') % {'name': 'Alex'}) == 'hello Alex'
    assert str(Text('hello ${name}') % ('Alex', 'other')) == 'hello Alex'
    assert str(Text('hello ${name}') % {'name': 'Alex', 'a': 'other'}) == 'hello Alex'


def test_Text_mod_ok_partial():
    template = Text('hello ${name}, welcome to ${team}, visit ${url}')
    assert str(template) == 'hello ${name}, welcome to ${team}, visit ${url}'

    lazy_template = template % 'Alex'
    assert str(lazy_template) == 'hello Alex, welcome to ${team}, visit ${url}'

    lazy_template % ('Team', 'URL')
    assert str(lazy_template) == 'hello Alex, welcome to Team, visit URL'

    lazy_template % {'team': 'MyTeam'}
    assert str(lazy_template) == 'hello Alex, welcome to MyTeam, visit URL'


def test_StrictText_str_ok():
    text = StrictText(en='${a} text', ru='${a} текст')

    assert str(text % {'a': 1}) == '1 text'


def test_StrictText_str_fail():
    text = StrictText(en='${a} text', ru='${a} текст')

    with pytest.raises(KeyError):
        str(text % {'b': 1})


def test_StrictText_mod_ok_one_argument():
    text = StrictText(en='hello ${name}', ru='привет ${name}')

    with language('en'):
        name, result = 'Alex', 'hello Alex'
        assert str(text % name) == result
        assert str(text % (name, )) == result
        assert str(text % {'name': name}) == result

    with language('ru'):
        name, result = 'Алек', 'привет Алек'
        assert str(text % name) == result
        assert str(text % (name, )) == result
        assert str(text % {'name': name}) == result

    assert str(text % 1) == 'hello 1'
    assert str(text % None) == 'hello None'
    assert str(text % True) == 'hello True'
    assert str(text % Text) == 'hello <class \'magic_i18n.text.Text\'>'


def test_StrictText_mod_ok_many_arguments():
    text = StrictText(
        en='hello ${name}, welcome to ${team}',
        ru='привет ${name}, добро пожаловать в ${team}'
    )

    with language('en'):
        name, team, result = 'Alex', 'DreamTeam', 'hello Alex, welcome to DreamTeam'
        assert str(text % (name, team)) == result
        assert str(text % {'name': name, 'team': team}) == result

    with language('ru'):
        name, team, result = 'Алек', 'КомандаМечты', 'привет Алек, добро пожаловать в КомандаМечты'
        assert str(text % (name, team)) == result
        assert str(text % {'name': name, 'team': team}) == result


def test_StrictText_mod_fail_not_enough_arguments():
    text = StrictText(
        en='hello ${name}, welcome to ${team}',
        ru='привет ${name}, добро пожаловать в ${team}'
    )

    with pytest.raises(TypeError) as err:
        text % ('Alex', )

    assert err.value.args == ('not enough arguments for format string', )

    with pytest.raises(TypeError) as err:
        text % 'Alex'

    assert err.value.args == ('not enough arguments for format string', )


def test_StrictText_mod_fail_not_all_arguments_converted():
    text = StrictText(
        en='hello ${name}, welcome to ${team}',
        ru='привет ${name}, добро пожаловать в ${team}'
    )

    with pytest.raises(TypeError) as err:
        text % ('Alex', 'Team', 'Q')

    assert err.value.args == ('not all arguments converted during string formatting', )


def test_StrictText_mod_fail_formatting_not_required():
    text = StrictText(en='hello', ru='привет')

    with pytest.raises(TypeError) as err:
        text % 'Alex'

    assert err.value.args == ('formatting not required', )
