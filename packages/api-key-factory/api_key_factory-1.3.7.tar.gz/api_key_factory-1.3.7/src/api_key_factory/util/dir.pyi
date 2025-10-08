import click
from pydantic import BaseModel

class Dir(BaseModel):
    path: str
    def __init__(self, dir_path: click.Path | None = None, create: bool = False) -> None: ...
