# -*- coding: utf-8 -*-

from api_key_factory.factory.key import Key


class TestKey:
    def test_default_constructor(self) -> None:
        k = Key()
        assert k.prefix == ""
        assert len(k.rand_uuid) == 36
        assert k.rand_uuid.count("-") == 4

    def test_constructor_with_prefix(self) -> None:
        k = Key("test")
        assert k.prefix == "test"
        assert len(k.rand_uuid) == 36
        assert k.rand_uuid.count("-") == 4

    def test_get_value_without_prefix(self) -> None:
        k = Key()
        v = k.get_value()
        assert len(v) == 36
        assert v.count("-") == 4

    def test_get_value_with_prefix(self) -> None:
        k = Key("test")
        v = k.get_value()
        assert len(v) == 41
        assert v.count("-") == 5
        assert v[:5] == "test-"

    def test_get_hash_without_prefix(self) -> None:
        k = Key()
        h = k.get_hash()
        assert len(h) == 64
        assert h.count("-") == 0

    def test_get_hash_without_prefix_defined_token(self) -> None:
        k = Key()
        k.rand_uuid = "6ad23e18-5ece-48ee-805d-e3ce973bd3de"
        h = k.get_hash()
        assert h == "d280d93d30b74ceca3cfd65e95c84affac408686f4d32b33723e6ac1e6378e10"

    def test_get_hash_with_prefix_defined_token(self) -> None:
        k = Key("test")
        k.rand_uuid = "6ad23e18-5ece-48ee-805d-e3ce973bd3de"
        h = k.get_hash()
        assert h == "89a239eddc4a3ad4e7ddca8e359b9859f15a1d844fad87a3a9e2b23b6df7b9fe"
