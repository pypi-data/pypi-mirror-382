import argparse
import importlib
import re
import sys
import tomllib

from collections.abc import Generator
from copy import copy
from itertools import chain
from string import Template
from typing import Literal, NamedTuple

from magic_i18n.text import TEXT_REGISTRY, LangType, Text

from .utils import short_hash


PYPROJECT = 'pyproject.toml'
DEFAULT_CONFIG = {
    'ignore': [],
    'check-arguments': True,
    'deny-doubles': True,
    'required-languages': [],
    'spell-check': False,
    'spell-check-ignore': [],
}

parser = argparse.ArgumentParser(description='Run magic-i18n linters')
parser.add_argument('modules', metavar='MODULE_PATH', type=str, nargs='+',
    help='Modules that will be imported for text initialization.')
parser.add_argument('--check-arguments', action=argparse.BooleanOptionalAction,
    help='Check that all versions of the text templates have the same arguments.')
parser.add_argument('--deny-doubles', action=argparse.BooleanOptionalAction,
    help='Prohibit text duplication')
parser.add_argument('--spell-check', action=argparse.BooleanOptionalAction,
    help='Spell check (requires pyspellchecker)')
parser.add_argument('--required-languages', type=str,
    help='Comma-separated list of required languages (en,ru,fr)')
parser.add_argument('--spell-check-ignore', type=str,
    help='Comma-separated list of words that are ignored when checking spelling (asd,qwe)')
parser.add_argument('--ignore', type=str,
    help='Comma-separated text (or it crc32 hashes) all checks ignore (asdtext,AD4JT53R)')


class LintError(NamedTuple):
    rule: Literal['deny-doubles', 'required-languages', 'check-arguments', 'spell-check']
    text: Text
    details: str


def run() -> None:
    global TEXT_REGISTRY  # noqa PLW0603

    sys.stdout.write('Run magic-i18n linter\n')
    sys.path.append('.')
    call_args = parser.parse_args()
    config = load_config(call_args)

    for module in call_args.modules:
        importlib.import_module(module)
        sys.stdout.write(f'  load [\x1b[33m{module}\x1b[0m]\n')

    sys.stdout.write(f'{len(TEXT_REGISTRY)} text objects found\n')

    registry = copy(TEXT_REGISTRY)

    if config['ignore']:
        for text in TEXT_REGISTRY:
            if text.fallback in config['ignore'] or short_hash(text.fallback) in config['ignore']:
                sys.stdout.write(f'  ignore [\x1b[33m{text!r}\x1b[0m]\n')
                registry.remove(text)

    errors = run_checks(config, registry)

    for err in errors:
        sys.stdout.write(f'[\x1b[31m{err.rule}\x1b[0m] {err.text!r}: {err.details}\n')

    if errors:
        parser.exit(1, f'\x1b[31mFailed\x1b[0m with {len(errors)} errors\n')
    else:
        parser.exit(0, '\x1b[32mSuccess\x1b[0m\n')


def load_config(args: argparse.Namespace) -> dict:
    pyproject = tomllib.load(open(PYPROJECT, 'rb'))
    config = pyproject.get('tool', {}).get('magic-i18n', {})
    config = DEFAULT_CONFIG | config

    if args.check_arguments is not None:
        config['check-arguments'] = args.check_arguments

    if args.deny_doubles is not None:
        config['deny-doubles'] = args.deny_doubles

    if args.spell_check is not None:
        config['spell-check'] = args.spell_check

    if args.required_languages is not None:
        if args.required_languages:
            config['required-languages'] = args.required_languages.split(',')
        else:
            config['required-languages'] = []

    if args.spell_check_ignore is not None:
        if args.spell_check_ignore:
            config['spell-check-ignore'] = args.spell_check_ignore.split(',')
        else:
            config['spell-check-ignore'] = []

    if args.ignore is not None:
        if args.ignore:
            config['ignore'] = args.ignore.split(',')
        else:
            config['ignore'] = []

    return config


def run_checks(config: dict, registry: list[Text]) -> list[LintError]:
    errors: list[LintError] = []

    if config['check-arguments']:
        errors.extend(run_check_arguments(registry))

    if config['deny-doubles']:
        errors.extend(run_check_doubles(registry))

    if languages := config['required-languages']:
        errors.extend(run_check_languages(registry, set(languages)))

    if config['spell-check']:
        errors.extend(run_check_spell(registry, config['spell-check-ignore']))

    return errors


def run_check_languages(registry: list[Text], languages: set[LangType]) -> Generator[LintError]:
    for text in registry:
        if langs := (languages - set(text.translations)):
            _langs = ','.join(langs)
            yield LintError(
                rule='required-languages',
                text=text,
                details=f'Required language(s) `{_langs}` are not provided'
            )


def run_check_doubles(registry: list[Text]) -> Generator[LintError]:
    _list: list[str] = []

    for text in registry:
        if text.fallback in _list:
            yield LintError(
                rule='deny-doubles',
                text=text,
                details='Double detected'
            )

        _list.append(text.fallback)


def run_check_arguments(registry: list[Text]) -> Generator[LintError]:
    for text in registry:
        fb_ids = Template(text.fallback).get_identifiers()

        for lang, _text in text.translations.items():
            ids = Template(_text).get_identifiers()

            if fb_ids != ids:
                yield LintError(
                    rule='check-arguments',
                    text=text,
                    details=f'The `{lang}` arguments differ from fallback'
                )


def run_check_spell(registry: list[Text], ignore: list[str]) -> Generator[LintError]:
    try:
        from spellchecker import SpellChecker  # noqa PLC0415
    except ImportError:  # pragma: no cover
        sys.stdout.write('[\x1b[31mspell-check\x1b[0m] FAILED: install magic-i18n[spell]\n')
        return

    all_languages = set(chain(*[text.translations for text in registry]))
    checkers = {
        lang: SpellChecker(language=lang)
        for lang in set(SpellChecker.languages()) & all_languages
    }

    word_parser = {
        '': re.compile(r'(?<!\${)[\w\'-]+', re.U | re.I),
        'ru': re.compile(r'[а-яА-Я-]+', re.U | re.I),
        'en': re.compile(r'(?<!\${)[a-zA-Z-\']+', re.U | re.I),
    }

    for text in registry:
        for lang, _text in text.translations.items():
            checker = checkers.get(lang, checkers['en'])
            parser = word_parser.get(lang, word_parser[''])

            prepared_text = parser.findall(_text)
            prepared_text = list(set(prepared_text) - set(ignore))

            for misspelled in checker.unknown(prepared_text):
                correction = checker.correction(misspelled)
                yield LintError(
                    rule='spell-check',
                    text=text,
                    details=f'`{misspelled}` is misspelled, perhaps `{correction}` will do?'
                )
