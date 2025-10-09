import argparse
import importlib
import sys
import tomllib

from copy import deepcopy
from unittest.mock import Mock, patch

import pytest

from magic_i18n import lint
from magic_i18n.lint import DEFAULT_CONFIG, TEXT_REGISTRY, Text


ARGS = argparse.Namespace(
    modules=['test_module'],
    check_arguments=None,
    deny_doubles=None,
    spell_check=None,
    required_languages=None,
    spell_check_ignore=None,
    ignore=None
)


@pytest.fixture(autouse=True)
def clear_registry(monkeypatch) -> None:
    global TEXT_REGISTRY  # noqa PLW0603
    TEXT_REGISTRY.clear()

    pyproject: dict = {'tool': {'magic-i18n': {}}}
    monkeypatch.setattr(tomllib, 'load', lambda x: pyproject)
    monkeypatch.setattr(sys, 'argv', ['magic-i18n', 'test_module'])


@patch.object(sys.stdout, 'write')
@patch.object(argparse.ArgumentParser, 'exit')
@patch.object(importlib, 'import_module')
def test_run_with_empty_registry(import_mock, exit_mock, stdout, monkeypatch):
    lint.run()

    stdout.assert_any_call('  load [\x1b[33mtest_module\x1b[0m]\n')
    exit_mock.assert_called_once_with(0, '\x1b[32mSuccess\x1b[0m\n')
    import_mock.assert_called()


@patch.object(argparse.ArgumentParser, 'exit')
@patch.object(importlib, 'import_module')
def test_run_with_texts(import_mock, exit_mock):
    Text(en='Test', ru='Тест')
    Text(en='Test', ru='Тест')

    lint.run()

    exit_mock.assert_called_once_with(1, '\x1b[31mFailed\x1b[0m with 1 errors\n')


@patch.object(sys, 'argv', ['magic-i18n', 'test_module', '--ignore=TestIgnore'])
@patch.object(argparse.ArgumentParser, 'exit')
@patch.object(importlib, 'import_module')
def test_run_with_ignore(import_mock, exit_mock, monkeypatch):
    Text(en='Test ${a}', ru='Тест ${a}')
    Text(en='TestIgnore', ru='Тест ${a}')

    lint.run()

    exit_mock.assert_called_once_with(0, '\x1b[32mSuccess\x1b[0m\n')


@pytest.mark.parametrize('args, expected', [
    ({'check_arguments': False}, {'check-arguments': False}),
    ({'deny_doubles': False}, {'deny-doubles': False}),
    ({'spell_check': True}, {'spell-check': True}),
    ({'required_languages': 'ru,en'}, {'required-languages': ['ru', 'en']}),
    ({'required_languages': ''}, {'required-languages': []}),
    ({'spell_check_ignore': 'asd,qwe'}, {'spell-check-ignore': ['asd', 'qwe']}),
    ({'spell_check_ignore': ''}, {'spell-check-ignore': []}),
    ({'ignore': 'Test,Else'}, {'ignore': ['Test', 'Else']}),
    ({'ignore': ''}, {'ignore': []}),
])
def test_load_config(args, expected):
    _args = deepcopy(ARGS)

    for key, value in args.items():
        setattr(_args, key, value)

    config = lint.load_config(_args)

    for key, value in expected.items():
        assert config[key] == value


@pytest.mark.parametrize('config, func, is_called', [
    (DEFAULT_CONFIG | {'check-arguments': False}, 'run_check_arguments', False),
    (DEFAULT_CONFIG | {'deny-doubles': False}, 'run_check_doubles', False),
    (DEFAULT_CONFIG | {'required-languages': ['ru']}, 'run_check_languages', True),
    (DEFAULT_CONFIG | {'spell-check': True}, 'run_check_spell', True),
])
def test_run_checks_ok(config, func, is_called, monkeypatch):
    mock = Mock(return_value=[])
    monkeypatch.setattr(lint, func, mock)

    result = lint.run_checks(config, [])

    assert mock.called == is_called
    assert len(result) == 0


@pytest.mark.parametrize('config, expected_error_count', [
    ({'langs': ['ru']}, 0),
    ({'langs': ['fr']}, 1),
])
def test_run_check_languages(config, expected_error_count):
    errors = list(lint.run_check_languages([Text(ru='Привет', en='Hello')], set(config['langs'])))
    assert len(errors) == expected_error_count


# Тестирование функции run_check_doubles
@pytest.mark.parametrize('texts, expected_error_count', [
    ([{'ru': 'Привет', 'en': 'Hello'}], 0),
    ([{'ru': 'Привет', 'en': 'Hello'}, {'ru': 'Привет', 'en': 'Hello'}], 1),
])
def test_run_check_doubles(texts, expected_error_count):
    errors = list(lint.run_check_doubles([Text(**text) for text in texts]))
    assert len(errors) == expected_error_count


# Тестирование функции run_check_arguments
@pytest.mark.parametrize('text, expected_error_count', [
    ({'ru': 'Привет ${name}', 'en': 'Hello ${name}'}, 0),
    ({'ru': 'Привет ${name}', 'en': 'Hello'}, 1),
])
def test_run_check_arguments(text, expected_error_count):
    errors = list(lint.run_check_arguments([Text(**text)]))
    assert len(errors) == expected_error_count


# Тестирование функции run_check_spell
@pytest.mark.parametrize('text, ignore, expected_error_count', [
    ({'ru': 'привет мир', 'en': 'hello world'}, [], 0),
    ({'ru': 'превет мир', 'en': 'hello world'}, [], 1),
    ({'ru': 'привет мир', 'en': 'hello wolrd'}, [], 1),
    ({'ru': 'привет мир', 'en': 'hello wolrd'}, ['wolrd'], 0),
])
def test_run_check_spell(text, ignore, expected_error_count):
    errors = list(lint.run_check_spell([Text(**text)], ignore))
    assert len(errors) == expected_error_count
