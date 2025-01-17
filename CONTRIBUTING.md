# Contributing to Telegram File Statistics Bot

Thank you for considering contributing to the Telegram File Statistics Bot! We welcome contributions from the community and are excited to see what you can bring to the project.

## Table of Contents

- [Contributing to Telegram File Statistics Bot](#contributing-to-telegram-file-statistics-bot)
  - [Table of Contents](#table-of-contents)
  - [Code of Conduct](#code-of-conduct)
  - [How to Contribute](#how-to-contribute)
    - [Reporting Bugs](#reporting-bugs)
    - [Suggesting Features](#suggesting-features)
    - [Submitting Pull Requests](#submitting-pull-requests)
  - [Development Setup](#development-setup)
  - [Running Tests](#running-tests)
  - [Running the linting tools](#running-the-linting-tools)
  - [Translations](#translations)
  - [CI/CD](#cicd)

## Code of Conduct

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) to understand the standards we expect from our community.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue using the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md). Provide as much detail as possible to help us understand and reproduce the issue.

### Suggesting Features

If you have an idea for a new feature, please create an issue using the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md). Describe your idea in detail and explain why it would be beneficial to the project.

### Submitting Pull Requests

1. Fork the repository.
2. Create a new branch for your feature or bugfix:
    ```sh
    git checkout -b my-feature-branch
    ```
3. Make your changes.
4. Ensure that your code follows the project's style and guidelines.
5. Write tests for your changes, if applicable.
6. Commit your changes, following the [conventional commits](https://www.conventionalcommits.org/) format:
    ```sh
    git commit -m "<type>: description of my changes"
    ```
7. Push your branch to your fork:
    ```sh
    git push origin my-feature-branch
    ```
8. Create a pull request using the [pull request template](.github/pull_request_template.md).

## Development Setup

To set up the development environment, follow these steps:

1. Clone the repository:
    ```sh
    git clone https://github.com/Francesco146/telegram-file-statistics-bot.git
    cd telegram-file-statistics-bot
    ```

2. Install `uv` if you haven't already:
    ```sh
    pip install uv
    ```

3. Create a new virtual environment using `uv`:
    ```sh
    uv venv
    ```
    and activate it:
    ```sh
    source .venv/bin/activate
    ```

4. Install the required packages using `uv`:
    ```sh
    uv sync --all-extras --dev
    ```

## Running Tests

To run the tests, use the following command:
```sh
uv run pytest
```
Wanted passing tests are `100%`.

## Running the linting tools

To run the linting tools, use the following command:
```sh
uv run pylint $(find src tests -name "*.py" -type f)
```
Wanted score is `10.00/10`.

## Translations

We use `msgfmt.py` and `pygettext.py` for handling translations. Here is how you can contribute to translations:

1. Extract translatable strings using `pygettext.py`:
    ```sh
    pygettext.py -d base -o locales/base.pot src/
    ```

2. Update the `.po` files for the respective languages by editing the `locales/<lang>/LC_MESSAGES/base.po` file.

3. Compile the `.po` files to `.mo` files using `msgfmt.py`:
    ```sh
    msgfmt.py -o locales/<lang>/LC_MESSAGES/base.mo locales/<lang>/LC_MESSAGES/base.po
    ```

4. Verify that the translations are working correctly by running the bot and checking the translated messages.

## CI/CD

This project uses GitHub Actions for continuous integration and deployment. The workflows are defined in the [`.github/workflows`](.github/workflows) directory:
- [`nightly-build.yml`](.github/workflows/nightly-build.yml): Runs nightly builds, which releases a new version (pre-release) at each latest commit. In the release, it builds the wheel and uploads it to GitHub Releases, along with the source distribution. This workflow runs only if the latest commit is not a release commit.
- [`release.yml`](.github/workflows/release.yml): Creates stable releases. It builds the wheel and uploads it to GitHub Releases, along with the source distribution. This workflow matches the commit message with the pattern `chore: bump version to <version>` to determine the version number, where `<version>` is something like `v*.*.*`.
- [`pylint.yml`](.github/workflows/pylint.yml): Runs Pylint for code linting, and updates the badge in the README.
- [`unit-tests.yml`](.github/workflows/unit-tests.yml): Runs unit tests using Pytest, and updates the badge in the README.


Thank you for contributing to the Telegram File Statistics Bot!