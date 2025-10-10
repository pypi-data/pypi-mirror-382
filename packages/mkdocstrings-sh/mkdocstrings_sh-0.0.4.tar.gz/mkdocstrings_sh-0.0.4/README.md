# mkdocstrings-sh

[![ci](https://github.com/kamilcuk/mkdocstrings-sh/workflows/ci/badge.svg)](https://github.com/kamilcuk/mkdocstrings-sh/actions?query=workflow%3Aci)
[![documentation](https://img.shields.io/badge/docs-mkdocs-708FCC.svg?style=flat)](https://kamilcuk.github.io/mkdocstrings-sh/)
[![pypi version](https://img.shields.io/pypi/v/mkdocstrings-sh.svg)](https://pypi.org/project/mkdocstrings-sh/)

A Sh handler for mkdocstrings.

This is a project unrelated to mkdocstrings-shell project. Naming it mkdocstrings-sh causes confusion with mkdocstrings-shell.
I do not intent to compete with the project. Just my documentation goals are different then mkdocstrings-shell. The features and style by mkdocstrings-shell were not in line with what I wanted. I decided to write my own library. This is the result.

See the generated mkdocs pages in github pages for documentation. <https://kamilcuk.github.io/mkdocstrings-sh/>

See examples/ page in github pages. There are examples with all the syntax and reference of the available tags.

## Installation

```bash
pip install mkdocstrings-sh
```

## Usage:

With the following header file:

```
--8<-- "docs/examples/readme.sh"
```

Generate docs for this file with this instruction in one of your Markdown page:

```
::: path/to/script
```

This will generate the following HTML:

::: docs/examples/readme.sh

### Single entity

It is also possible to generate only a specific function, variable or a section of the file by passing additional arguments to `:::`. The third argument specifies the entity type. The second argument specifies the name of the function or variable or section to gneerate documeanttion for.

```
::: docs/examples/readme.sh function_name function
::: docs/examples/readme.sh variable_name variable
::: docs/examples/readme.sh section_name section
```
