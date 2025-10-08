# Contributor Guide

Thank you for your interest in improving this project.
This project is open-source under the [MIT license] and
welcomes contributions in the form of bug reports, feature requests, and pull requests.

Here is a list of important resources for contributors:

- [Source Code]
- [Documentation]
- [Issue Tracker]
- [Code of Conduct]

## How to report a bug

Report bugs on the [Issue Tracker].

When filing an issue, make sure to answer these questions:

- Which operating system and Python version are you using?
- Which version of this project are you using?
- What did you do?
- What did you expect to see?
- What did you see instead?

The best way to get your bug fixed is to provide a test case,
and/or steps to reproduce the issue.

## How to request a feature

Request features on the [Issue Tracker].

## How to set up your development environment

You need Python 3.10+ and the following tools:

- [uv]
- [Nox]
- nbstripout

### Install [pipx]

```console
python -m pip install --user pipx
python -m pipx ensurepath
```

### Install [uv]

Instructions: <https://docs.astral.sh/uv/getting-started/installation/>

### Install [Nox]

```console
pipx install nox
```

### Install nbstripout

```console
pipx install nbstripout
```

### Install the pre-commit hooks

```console
nox --session=pre-commit -- install
```

### Install the package with development requirements

```console
uv sync --dev
```

## How to test the project

Run the full test suite:

```console
nox
```

List the available Nox sessions:

```console
nox --list-sessions
```

You can also run a specific Nox session.
For example, invoke the unit test suite like this:

```console
nox --session=tests
```

Unit tests are located in the _tests_ directory,
and are written using the [pytest] testing framework.

## How to incorporate breaking model changes

We keep the version of `ssb-datadoc-model` pinned since almost all changes there are breaking changes and we don't want this package to be bumped accidentally. When upgrading the version of this package there are a number of things to consider:

1. Bump the package version
1. Run the tests and see what fails
1. Handle upgrading older document versions by adding code in: [src/dapla_metadata/datasets/compatibility](src/dapla_metadata/datasets/compatibility)
   1. Write a handler function to make the necessary changes
   1. Register the handler function as a `BackwardsCompatibleVersion` instance
   1. Add a metadata document under `tests/datasets/resources/existing_metadata_file/compatibility/v<YOUR_VERSION>` for use in testing.
1. Fix any source or test code which refers to outdated fields
1. Upgrade all the documents in the [tests/datasets/resources/existing_metadata_file](tests/datasets/resources/existing_metadata_file) directory (NOT those in the `compatibility` directory) to the latest version. This can be done using the script e.g. `uv run python bin/upgrade_metadata_file.py --path tests/datasets/resources/existing_metadata_file/person_data_v1__DOC.json`

## How to submit changes

Open a [pull request] to submit changes to this project.

Your pull request needs to meet the following guidelines for acceptance:

- The Nox test suite must pass without errors and warnings.
- Include unit tests. This project maintains 100% code coverage.
- If your changes add functionality, update the documentation accordingly.

Feel free to submit early, though—we can always iterate on this.

To run linting and code formatting checks before committing your change, you can install pre-commit as a Git hook by running the following command:

```console
nox --session=pre-commit -- install
```

It is recommended to open an issue before starting work on anything.
This will allow a chance to talk it over with the owners and validate your approach.

[mit license]: https://opensource.org/licenses/MIT
[source code]: https://github.com/statisticsnorway/dapla-toolbelt-metadata
[documentation]: https://statisticsnorway.github.io/dapla-toolbelt-metadata
[issue tracker]: https://github.com/statisticsnorway/dapla-toolbelt-metadata/issues
[uv]: https://docs.astral.sh/uv/
[pipx]: https://pipx.pypa.io/
[nox]: https://nox.thea.codes/
[pytest]: https://pytest.readthedocs.io/
[pull request]: https://github.com/statisticsnorway/dapla-toolbelt-metadata/pulls

<!-- github-only -->

[code of conduct]: CODE_OF_CONDUCT.md
