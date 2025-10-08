# -*- coding: utf-8 -*-

import click

from api_key_factory.factory.key import Key
from api_key_factory.util.dir import Dir
from api_key_factory.util.file import File


@click.group()
@click.version_option("1.3.7", prog_name="api_key_factory")
def cli() -> None:
    """A simple CLI tool to generate API keys and their corresponding
    SHA-256 hashes.
    """
    pass


@cli.command()
@click.option(
    "-d",
    "--dir",
    "output_dir",
    type=click.Path(exists=False, file_okay=False, dir_okay=True, writable=True),
    required=False,
    help="Directory to output keys and hashes. If not set output to stdout.",
)
@click.option(
    "-n",
    "--num",
    "num",
    type=click.IntRange(min=1),
    default=1,
    help="Number of API keys to generate",
)
@click.option(
    "-p",
    "--prefix",
    "prefix",
    type=str,
    default="",
    help="Add a prefix at the beginning of the key",
)
def generate(
    output_dir: click.Path | None,
    num: int,
    prefix: str,
) -> None:
    """Command to generate API keys and their corresponding SHA-256 hashes.

    Args:
        output_dir (click.Path): Directory to output keys and hashes.
        num (int): Number of API keys to generate. Default 1.
        prefix (str): Prefix at the beginning of the key.

    Raises:
        click.ClickException: Error when writing output files
    """
    if output_dir is not None:
        try:
            # Create directory if it doesn't exist
            dir = Dir(output_dir, True)
        except OSError as error:
            raise click.ClickException("Output directory can not be created!\n" + str(error))

        if len(prefix) > 0:
            keys_filename = f"{prefix}_keys.txt"
            hashes_filename = f"{prefix}_hashes.txt"
        else:
            keys_filename = "keys.txt"
            hashes_filename = "hashes.txt"

        try:
            keys_file = File(keys_filename, dir.path, True)
            hashes_file = File(hashes_filename, dir.path, True)
        except (FileExistsError, PermissionError) as error:
            raise click.ClickException(f"File already exists in directory {dir.path}!\n" + str(error))

        for _ in range(num):
            key = Key(prefix)
            keys_file.add_content(f"{key.get_value()}\n")
            hashes_file.add_content(f"{key.get_hash()}\n")

        try:
            keys_file.save()
            keys_file.protect()
            hashes_file.save()
        except (OSError, PermissionError) as error:
            raise click.ClickException("The file cannot be written to!\n" + str(error))

        click.echo(f"Success! {num} keys and hashes have been written to the files:")
        click.echo(f" - {dir.path}/{keys_filename}")
        click.echo(f" - {dir.path}/{hashes_filename}")
    else:
        for _ in range(num):
            key = Key(prefix)
            click.echo(f"{key.get_value()}   {key.get_hash()}")


if __name__ == "__main__":
    cli()  # pragma: no cover
