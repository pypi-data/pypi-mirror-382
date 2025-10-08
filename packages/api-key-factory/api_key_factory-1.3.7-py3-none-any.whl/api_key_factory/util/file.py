# -*- coding: utf-8 -*-

import os

from pydantic import BaseModel, StringConstraints
from typing_extensions import Annotated


class File(BaseModel):
    """Utility class for a file."""

    dir_path: str
    filename: Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]
    content: str = ""

    def __init__(self, filename: str, dir_path: str, new: bool = False):
        """Constructor.

        Args:
            filename (str): Name of the file.
            dir (Dir): Directory to save the file in.
            new (bool, optional): Should be a new file. \
                Defaults to False.

        Raises:
            FileNotFoundError: When create is False and directory not found.
            OSError: If the file cannot be written to.
        """
        super().__init__(dir_path=dir_path, filename=filename)

        file_path = f"{dir_path}/{filename}"

        if new and os.path.exists(file_path):
            raise FileExistsError(f"File {filename} already exists.")

        # touch file
        with open(file_path, "w"):
            pass

    def add_content(self, content: str = "") -> None:
        """Add content to the file.

        Args:
            filename (str): Name of the file. \
                Defaults to an empty string if not provided.
        """

        self.content += content

    def save(self) -> None:
        """Save the file.

        Raises:
            OSError: If the file cannot be written to.
        """

        file_path = f"{self.dir_path}/{self.filename}"
        with open(file_path, "w") as f:
            f.write(self.content)

    def protect(self) -> None:
        """Protect file by giving it read only access.

        Raises:
            PermissionError : if unable to change permissions.
        """
        file_path = f"{self.dir_path}/{self.filename}"
        os.chmod(file_path, 0o600)
