# -*- coding: utf-8 -*-

import os
import shutil

from click.testing import CliRunner

from api_key_factory import api_key_factory


class Test_generate:
    def test_generate_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(api_key_factory.cli, ["generate", "--help"])
        assert result.exit_code == 0
        assert "generate [OPTIONS]" in result.stdout

    def test_generate_without_option(self) -> None:
        runner = CliRunner()
        result = runner.invoke(api_key_factory.cli, ["generate"])
        assert result.exit_code == 0
        out = result.stdout
        lines = out.splitlines()
        assert len(lines) == 1
        key_hash = lines[0].split()
        assert len(key_hash[0]) == 36
        assert len(key_hash[1]) == 64

    def test_generate_with_n_option(self) -> None:
        runner = CliRunner()
        result = runner.invoke(api_key_factory.cli, ["generate", "-n", "3"])
        assert result.exit_code == 0
        out = result.stdout
        lines = out.splitlines()
        assert len(lines) == 3
        key_hash = lines[0].split()
        assert len(key_hash[0]) == 36
        assert len(key_hash[1]) == 64

    def test_generate_with_num_option(self) -> None:
        runner = CliRunner()
        result = runner.invoke(api_key_factory.cli, ["generate", "--num", "3"])
        assert result.exit_code == 0
        out = result.stdout
        lines = out.splitlines()
        assert len(lines) == 3
        key_hash = lines[0].split()
        assert len(key_hash[0]) == 36
        assert len(key_hash[1]) == 64

    def test_generate_with_p_option(self) -> None:
        runner = CliRunner()
        result = runner.invoke(api_key_factory.cli, ["generate", "-p", "test"])
        assert result.exit_code == 0
        out = result.stdout
        lines = out.splitlines()
        assert len(lines) == 1
        key_hash = lines[0].split()
        assert len(key_hash[0]) == 41
        assert len(key_hash[1]) == 64
        assert key_hash[0][:5] == "test-"

    def test_generate_with_prefix_option(self) -> None:
        runner = CliRunner()
        result = runner.invoke(api_key_factory.cli, ["generate", "--prefix", "test"])
        assert result.exit_code == 0
        out = result.stdout
        lines = out.splitlines()
        assert len(lines) == 1
        key_hash = lines[0].split()
        assert len(key_hash[0]) == 41
        assert len(key_hash[1]) == 64
        assert key_hash[0][:5] == "test-"

    def test_generate_with_blank_prefix_option(self) -> None:
        runner = CliRunner()
        result = runner.invoke(api_key_factory.cli, ["generate", "--prefix", ""])
        assert result.exit_code == 0
        out = result.stdout
        lines = out.splitlines()
        assert len(lines) == 1
        key_hash = lines[0].split()
        assert len(key_hash[0]) == 36
        assert len(key_hash[1]) == 64

    def test_generate_in_file(self) -> None:
        if os.path.exists("tmp_test"):
            shutil.rmtree("tmp_test")
        runner = CliRunner()
        result = runner.invoke(api_key_factory.cli, ["generate", "-d", "tmp_test"])
        assert result.exit_code == 0
        out = result.stdout
        output = out.splitlines()
        assert len(output) == 3
        assert "Success! 1 keys and hashes" in output[0]
        assert "tmp_test/keys.txt" in output[1]
        assert "tmp_test/hashes.txt" in output[2]
        assert os.path.exists("tmp_test/keys.txt")
        assert os.path.exists("tmp_test/hashes.txt")
        with open("tmp_test/keys.txt", "r") as fk:
            ck = fk.readlines()
        assert len(ck) == 1
        assert len(ck[0].strip()) == 36
        with open("tmp_test/hashes.txt", "r") as fh:
            ch = fh.readlines()
        assert len(ch) == 1
        assert len(ch[0].strip()) == 64
        shutil.rmtree("tmp_test")

    def test_generate_in_file_with_long_option(self) -> None:
        if os.path.exists("tmp_test"):
            shutil.rmtree("tmp_test")
        runner = CliRunner()
        result = runner.invoke(api_key_factory.cli, ["generate", "--dir", "tmp_test"])
        assert result.exit_code == 0
        out = result.stdout
        output = out.splitlines()
        assert len(output) == 3
        assert "Success! 1 keys and hashes" in output[0]
        assert "tmp_test/keys.txt" in output[1]
        assert "tmp_test/hashes.txt" in output[2]
        assert os.path.exists("tmp_test/keys.txt")
        assert os.path.exists("tmp_test/hashes.txt")
        with open("tmp_test/keys.txt", "r") as fk:
            ck = fk.readlines()
        assert len(ck) == 1
        assert len(ck[0].strip()) == 36
        with open("tmp_test/hashes.txt", "r") as fh:
            ch = fh.readlines()
        assert len(ch) == 1
        assert len(ch[0].strip()) == 64
        shutil.rmtree("tmp_test")

    def test_generate_in_file_with_n_option(self) -> None:
        if os.path.exists("tmp_test"):
            shutil.rmtree("tmp_test")
        runner = CliRunner()
        result = runner.invoke(api_key_factory.cli, ["generate", "-d", "tmp_test", "-n", "3"])
        assert result.exit_code == 0
        out = result.stdout
        output = out.splitlines()
        assert len(output) == 3
        assert "Success! 3 keys and hashes" in output[0]
        with open("tmp_test/keys.txt", "r") as fk:
            ck = fk.readlines()
        assert len(ck) == 3
        assert len(ck[0].strip()) == 36
        assert len(ck[2].strip()) == 36
        with open("tmp_test/hashes.txt", "r") as fh:
            ch = fh.readlines()
        assert len(ch) == 3
        assert len(ch[0].strip()) == 64
        assert len(ch[2].strip()) == 64
        shutil.rmtree("tmp_test")

    def test_generate_file_with_num_option(self) -> None:
        if os.path.exists("tmp_test"):
            shutil.rmtree("tmp_test")
        runner = CliRunner()
        result = runner.invoke(api_key_factory.cli, ["generate", "-d", "tmp_test", "--num", "3"])
        assert result.exit_code == 0
        out = result.stdout
        output = out.splitlines()
        assert len(output) == 3
        assert "Success! 3 keys and hashes" in output[0]
        with open("tmp_test/keys.txt", "r") as fk:
            ck = fk.readlines()
        assert len(ck) == 3
        assert len(ck[0].strip()) == 36
        assert len(ck[2].strip()) == 36
        with open("tmp_test/hashes.txt", "r") as fh:
            ch = fh.readlines()
        assert len(ch) == 3
        assert len(ch[0].strip()) == 64
        assert len(ch[2].strip()) == 64
        shutil.rmtree("tmp_test")

    def test_generate_file_with_p_option(self) -> None:
        if os.path.exists("tmp_test"):
            shutil.rmtree("tmp_test")
        runner = CliRunner()
        result = runner.invoke(api_key_factory.cli, ["generate", "-d", "tmp_test", "-p", "test"])
        assert result.exit_code == 0
        out = result.stdout
        output = out.splitlines()
        assert len(output) == 3
        assert "Success! 1 keys and hashes" in output[0]
        assert "tmp_test/test_keys.txt" in output[1]
        assert "tmp_test/test_hashes.txt" in output[2]
        assert os.path.exists("tmp_test/test_keys.txt")
        assert os.path.exists("tmp_test/test_hashes.txt")
        with open("tmp_test/test_keys.txt", "r") as fk:
            ck = fk.readlines()
        assert len(ck) == 1
        assert len(ck[0].strip()) == 41
        assert ck[0][:5] == "test-"
        with open("tmp_test/test_hashes.txt", "r") as fh:
            ch = fh.readlines()
        assert len(ch) == 1
        assert len(ch[0].strip()) == 64
        shutil.rmtree("tmp_test")

    def test_generate_file_with_prefix_option(self) -> None:
        if os.path.exists("tmp_test"):
            shutil.rmtree("tmp_test")
        runner = CliRunner()
        result = runner.invoke(api_key_factory.cli, ["generate", "-d", "tmp_test", "--prefix", "test"])
        assert result.exit_code == 0
        out = result.stdout
        output = out.splitlines()
        assert len(output) == 3
        assert "Success! 1 keys and hashes" in output[0]
        assert "tmp_test/test_keys.txt" in output[1]
        assert "tmp_test/test_hashes.txt" in output[2]
        assert os.path.exists("tmp_test/test_keys.txt")
        assert os.path.exists("tmp_test/test_hashes.txt")
        with open("tmp_test/test_keys.txt", "r") as fk:
            ck = fk.readlines()
        assert len(ck) == 1
        assert len(ck[0].strip()) == 41
        assert ck[0][:5] == "test-"
        with open("tmp_test/test_hashes.txt", "r") as fh:
            ch = fh.readlines()
        assert len(ch) == 1
        assert len(ch[0].strip()) == 64
        shutil.rmtree("tmp_test")

    def test_generate_file_with_blank_prefix_option(self) -> None:
        if os.path.exists("tmp_test"):
            shutil.rmtree("tmp_test")
        runner = CliRunner()
        result = runner.invoke(api_key_factory.cli, ["generate", "-d", "tmp_test", "--prefix", ""])
        assert result.exit_code == 0
        out = result.stdout
        output = out.splitlines()
        assert len(output) == 3
        assert "Success! 1 keys and hashes" in output[0]
        assert "tmp_test/keys.txt" in output[1]
        assert "tmp_test/hashes.txt" in output[2]
        assert os.path.exists("tmp_test/keys.txt")
        assert os.path.exists("tmp_test/hashes.txt")
        with open("tmp_test/keys.txt", "r") as fk:
            ck = fk.readlines()
        assert len(ck) == 1
        assert len(ck[0].strip()) == 36
        with open("tmp_test/hashes.txt", "r") as fh:
            ch = fh.readlines()
        assert len(ch) == 1
        assert len(ch[0].strip()) == 64
        shutil.rmtree("tmp_test")

    # def test_generate_in_file_err_dir(self) -> None:
    #     runner = CliRunner()
    #     result = runner.invoke(api_key_factory.cli, ["generate", "-d", "/root/test"])
    #     assert result.exit_code == 1
    #     assert "Output directory can not be created!" in result.stdout

    def test_generate_in_file_err_file_keys(self) -> None:
        if not os.path.exists("tmp_test"):
            os.makedirs("tmp_test")
        with open("tmp_test/keys.txt", "w"):
            pass
        runner = CliRunner()
        result = runner.invoke(api_key_factory.cli, ["generate", "-d", "tmp_test"])
        assert result.exit_code == 1
        assert "Error: File already exists in directory tmp_test!" in result.stderr
        shutil.rmtree("tmp_test")

    def test_generate_in_file_err_file_hashes(self) -> None:
        if not os.path.exists("tmp_test"):
            os.makedirs("tmp_test")
        with open("tmp_test/hashes.txt", "w"):
            pass
        runner = CliRunner()
        result = runner.invoke(api_key_factory.cli, ["generate", "-d", "tmp_test"])
        assert result.exit_code == 1
        assert "Error: File already exists in directory tmp_test!" in result.stderr
        shutil.rmtree("tmp_test")
