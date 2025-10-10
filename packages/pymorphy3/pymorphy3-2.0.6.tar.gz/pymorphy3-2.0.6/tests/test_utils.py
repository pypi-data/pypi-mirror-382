import pytest

from pymorphy3.utils import get_mem_usage


def test_get_mem_usage():
    pytest.importorskip("psutil")
    rss = get_mem_usage()
    assert 1000000 < rss < 1000000000  # 1MB to 1GB
