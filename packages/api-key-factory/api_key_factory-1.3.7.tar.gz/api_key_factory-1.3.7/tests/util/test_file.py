# -*- coding: utf-8 -*-

import os
import shutil

import pytest
from pydantic import ValidationError

from api_key_factory.util.file import File


class TestFile:
    def test_file_simple(self) -> None:
        if not os.path.exists("tmp_test"):
            os.makedirs("tmp_test")
        if os.path.exists("tmp_test/test.txt"):
            os.remove("tmp_test/test.txt")
        File("test.txt", "tmp_test")
        assert os.path.exists("tmp_test/test.txt")
        os.remove("tmp_test/test.txt")
        shutil.rmtree("tmp_test")

    # def test_file_enable_create(self) -> None:
    #     if os.path.exists("test.txt"):
    #         os.remove("test.txt")
    #     with pytest.raises(PermissionError) as excinfo:
    #         File("test.txt", "")
    #     assert "Permission denied" in str(excinfo.value)

    def test_file_filename_blank(self) -> None:
        if not os.path.exists("tmp_test"):
            os.makedirs("tmp_test")
        with pytest.raises(ValidationError) as excinfo:
            File("", "tmp_test")
        assert "validation error for File" in str(excinfo.value)
        shutil.rmtree("tmp_test")

    def test_file_add_content(self) -> None:
        if not os.path.exists("tmp_test"):
            os.makedirs("tmp_test")
        if os.path.exists("tmp_test/test.txt"):
            os.remove("tmp_test/test.txt")
        f = File("test.txt", "tmp_test")
        f.add_content("content1")
        assert f.content == "content1"
        shutil.rmtree("tmp_test")

    def test_file_add_content_with_previous_content(self) -> None:
        if not os.path.exists("tmp_test"):
            os.makedirs("tmp_test")
        if os.path.exists("tmp_test/test.txt"):
            os.remove("tmp_test/test.txt")
        f = File("test.txt", "tmp_test")
        f.content = "content1"
        f.add_content("content2")
        assert f.content == "content1content2"
        shutil.rmtree("tmp_test")

    def test_file_add_blank_content(self) -> None:
        if not os.path.exists("tmp_test"):
            os.makedirs("tmp_test")
        if os.path.exists("tmp_test/test.txt"):
            os.remove("tmp_test/test.txt")
        f = File("test.txt", "tmp_test")
        f.add_content("")
        assert f.content == ""
        shutil.rmtree("tmp_test")

    def test_file_save(self) -> None:
        if not os.path.exists("tmp_test"):
            os.makedirs("tmp_test")
        if os.path.exists("tmp_test/test.txt"):
            os.remove("tmp_test/test.txt")
        f = File("test.txt", "tmp_test")
        f.add_content("content1")
        f.save()
        with open("tmp_test/test.txt", "r") as fi:
            content = fi.read()
        assert content == "content1"
        shutil.rmtree("tmp_test")

    def test_file_protect(self) -> None:
        if not os.path.exists("tmp_test"):
            os.makedirs("tmp_test")
        if os.path.exists("tmp_test/test.txt"):
            os.remove("tmp_test/test.txt")
        f = File("test.txt", "tmp_test")
        f.protect()
        file_stats = os.stat("tmp_test/test.txt")
        mode = file_stats.st_mode
        permissions = mode & 0o777
        assert permissions == 0o600
        shutil.rmtree("tmp_test")
