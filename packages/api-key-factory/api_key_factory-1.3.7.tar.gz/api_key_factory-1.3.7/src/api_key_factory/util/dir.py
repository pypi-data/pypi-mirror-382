# -*- coding: utf-8 -*-

import os

import click
from pydantic import BaseModel


class Dir(BaseModel):
    """Utility class for a directory."""

    path: str

    def __init__(self, dir_path: click.Path | None = None, create: bool = False):
        """Constructor.

        Args:
            dir_path (click.Path | None): Directory file path. \
                Current working directory if None.
            create (bool, optional): Create directory if doesn't exist. \
                Defaults to False.

        Raises:
            FileNotFoundError: When create is False and directory not found.
        """
        if dir_path is None:
            path = os.getcwd()
        else:
            path = click.format_filename(str(dir_path))

        if not os.path.exists(path):
            if create:
                os.makedirs(path)
            else:
                raise FileNotFoundError(f"Directory {path} not found!")

        super().__init__(path=path)
