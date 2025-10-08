# -*- coding: utf-8 -*-

from click.testing import CliRunner

from api_key_factory import api_key_factory


class Test_api_key_factory:
    def test_api_key_factory_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(api_key_factory.cli, ["--help"])
        assert result.exit_code == 0
        assert "[OPTIONS]" in result.stdout

    def test_api_key_factory_version(self) -> None:
        runner = CliRunner()
        result = runner.invoke(api_key_factory.cli, ["--version"])
        assert result.exit_code == 0
        assert "version" in result.stdout
