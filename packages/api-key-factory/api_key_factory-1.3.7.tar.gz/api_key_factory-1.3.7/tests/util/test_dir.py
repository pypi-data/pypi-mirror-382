# -*- coding: utf-8 -*-

import os

import click
import pytest

from api_key_factory.util.dir import Dir


class TestDir:
    def test_dir_blank(self) -> None:
        d = Dir()
        p = os.getcwd()
        assert d.path == p

    def test_dir_not_exist(self) -> None:
        cp = click.Path()
        with pytest.raises(FileNotFoundError) as excinfo:
            Dir(cp)
        assert "not found!" in str(excinfo.value)
