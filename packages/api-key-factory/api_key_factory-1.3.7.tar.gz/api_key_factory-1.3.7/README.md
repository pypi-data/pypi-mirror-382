# `api-key-factory`

[![Software License](https://img.shields.io/badge/license-MIT-informational.svg?style=for-the-badge)](LICENSE)
[![semantic-release: angular](https://img.shields.io/badge/semantic--release-angular-e10079?logo=semantic-release&style=for-the-badge)](https://github.com/semantic-release/semantic-release)
[![Pipeline Status](https://img.shields.io/gitlab/pipeline-status/op_so/projects/api-key-factory?style=for-the-badge)](https://gitlab.com/op_so/projects/api-key-factory/pipelines)

[![Built with Material for MkDocs](https://img.shields.io/badge/Material_for_MkDocs-526CFE?style=for-the-badge&logo=MaterialForMkDocs&logoColor=white)](https://op_so.gitlab.io/projects/api-key-factory/) Source code documentation

<img src="https://gitlab.com/op_so/projects/api-key-factory/-/raw/main/api_key_factory.png?ref_type=heads" alt="Logo of api-key-factory" width="150px" height="150px" style="display: block; margin: 0 auto; border: solid; border-color: #5f6368; border-radius: 20px;">

## Overview

`api-key-factory` is a CLI tool to generate API keys and their corresponding [SHA-256](https://en.wikipedia.org/wiki/SHA-2) hashes. The secret part of the key is an [UUID (Universally Unique Identifier) version 4 (random)](https://en.wikipedia.org/wiki/Universally_unique_identifier#Version_4_(random)).

Example of generated a API key:

```bash
mykey-8590efb6-0a68-4390-8537-99a54928c669
```

```bash
Usage: api-key-factory [OPTIONS] COMMAND [ARGS]...

  A simple CLI tool to generate API keys and their corresponding SHA-256
  hashes.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  generate  Command to generate API keys and their corresponding SHA-256...
```

## `generate`

Generate api keys and hashes in standart terminal output (stdout) or in 2 distinct files (`[prefix_]keys.txt`, `[prefix_]hashes.txt`) in a defined directory.

```bash
Usage: api-key-factory generate [OPTIONS]

  Command to generate API keys and their corresponding SHA-256 hashes.

  Args:     output_dir (click.Path): Directory to output keys and hashes.
  num (int): Number of API keys to generate. Default 1.     prefix (str):
  Prefix at the beginning of the key.

  Raises:     click.ClickException: Error when writing output files

Options:
  -d, --dir DIRECTORY      Directory to output keys and hashes. If not set
                           output to stdout.
  -n, --num INTEGER RANGE  Number of API keys to generate  [x>=1]
  -p, --prefix TEXT        Add a prefix at the beginning of the key
  --help                   Show this message and exit.
```

Example:

```bash
$ api-key-factory generate --num 2
d097dccc-cd24-4137-8ddb-d03f8b07d8d9   8b89600015b273c28f966f368456e45e01df239a36bf939ff72a16881f775679
c2d79a40-388e-4709-9e4b-903035b0e71e   fb22be500af1ef0479745bbbce847854da33f5e910361ad278e0282995b95f4d
$ api-key-factory generate --prefix mykey
mykey-3532dceb-f38a-491b-814d-9607bc9a947a   83309f0b7cd16fbd02edc85dbe32fc3326367618cf80a885f649d8e4eaeb43b3
$ api-key-factory generate -p mykey -n 5 --dir out
Success! 5 keys and hashes have been written to the files:
 - out/mykey_keys.txt
 - out/mykey_hashes.txt
```

## Installation

### With `Python` environment

To use:

- Minimal Python version: 3.10

Installation with Python `pip`:

```bash
python3 -m pip install api-key-factory
api-key-factory --help
```

## Developement

### With [uv](https://docs.astral.sh/uv/) and [Task](https://taskfile.dev/)

To use:

- Minimal Python version: 3.10
- `uv` installation documentation: [https://docs.astral.sh/uv/getting-started/installation/](https://docs.astral.sh/uv/getting-started/installation/)
- `task` installation documentation: [https://taskfile.dev/installation/](https://taskfile.dev/installation/)

```bash
# Set environment
uv sync
# Format
task 00:10-format
# Lint
task 00:20-lint
# Tests
task 00:40-test
# Run
uv run api-key-factory --help
```

## Authors

<!-- vale off -->
- **FX Soubirou** - *Initial work* - [GitLab repositories](https://gitlab.com/op_so)
<!-- vale on -->

## License

<!-- vale off -->
This program is free software: you can redistribute it and/or modify it under the terms of the MIT License (MIT).
See the [LICENSE](https://opensource.org/licenses/MIT) for details.
<!-- vale on -->
