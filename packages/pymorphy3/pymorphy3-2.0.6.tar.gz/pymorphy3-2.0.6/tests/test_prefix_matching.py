import pytest

from pymorphy3 import lang
from pymorphy3.dawg import PrefixMatcher, PythonPrefixMatcher

MATCHERS = [PythonPrefixMatcher, PrefixMatcher]
HAS_PREFIXES = [
    ["псевдокот", True],
    ["кот", False],
]
PREFIXES = [
    ['псевдокот', ['псевдо']],
    ['супер-кот', ['супер', 'супер-']],
    ['кот', []],
]

@pytest.mark.parametrize('matcher_cls', MATCHERS)
@pytest.mark.parametrize(['word', 'is_prefixed'], HAS_PREFIXES)
def test_prefix_matcher_is_prefixed(matcher_cls, word, is_prefixed):
    matcher = matcher_cls(lang.ru.KNOWN_PREFIXES)
    assert matcher.is_prefixed(word) == is_prefixed


@pytest.mark.parametrize('matcher_cls', MATCHERS)
@pytest.mark.parametrize(['word', 'prefixes'], PREFIXES)
def test_prefix_matcher_prefixes(matcher_cls, word, prefixes):
    matcher = matcher_cls(lang.ru.KNOWN_PREFIXES)
    assert set(matcher.prefixes(word)) == set(prefixes)
