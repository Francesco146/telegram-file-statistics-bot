# Contributing to Telegram File Statistics Bot

Thank you for considering contributing to the Telegram File Statistics Bot! We welcome contributions from the community and are excited to see what you can bring to the project.

- [Contributing to Telegram File Statistics Bot](#contributing-to-telegram-file-statistics-bot)
  - [📜 Code of Conduct](#-code-of-conduct)
  - [🤝 How to Contribute](#-how-to-contribute)
    - [🐛 Reporting Bugs](#-reporting-bugs)
    - [💡 Suggesting Features](#-suggesting-features)
    - [🔄 Submitting Pull Requests](#-submitting-pull-requests)
  - [🛠️ Development Setup](#️-development-setup)
  - [✅ Running Tests](#-running-tests)
  - [🧹 Running the linting tools](#-running-the-linting-tools)
  - [🌐 Translations](#-translations)
  - [⚙️ GitHub Actions](#️-github-actions)

## 📜 Code of Conduct

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) to understand the standards we expect from our community.

## 🤝 How to Contribute

### 🐛 Reporting Bugs

If you find a bug, please create an issue using the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md). Provide as much detail as possible to help us understand and reproduce the issue.

### 💡 Suggesting Features

If you have an idea for a new feature, please create an issue using the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md). Describe your idea in detail and explain why it would be beneficial to the project.

### 🔄 Submitting Pull Requests

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

## 🛠️ Development Setup

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

## ✅ Running Tests

To run the tests, use the following command:
```sh
uv run pytest
```
Wanted passing tests are `100%`.

## 🧹 Running the linting tools

To run the linting tools, use the following command:
```sh
uv run pylint $(find src tests -name "*.py" -type f)
```
Wanted score is `10.00/10`.

## 🌐 Translations

We use `xgettext`, `msgmerge`, and `msgfmt` for handling translations. Here is how you can contribute to translations:

1. Run all steps (extract translatable strings, update the POT file, update the `.po` files, and compile the `.po` files to `.mo` files):
    ```sh
    make all
    ```

2. Verify that the translations are working correctly by running the bot and checking the translated messages. If you find any issues, use the built-in help command:
    ```sh
    make help
    ```

## ⚙️ GitHub Actions

This project utilizes GitHub Actions for automating continuous integration and deployment:

- **[Build Pull Request](.github/workflows/build_pr.yml)**: Executes automated checks and builds when a pull request is made to the `dev` branch.
- **[Release](.github/workflows/release.yml)**: Handles deployments whenever changes are pushed to `master` or `dev`, or manually triggered.
- **[Pytest](.github/workflows/pytest.yml)**: Runs unit tests with each code push, generating a badge to reflect test results.
- **[Pylint](.github/workflows/pylint.yml)**: Performs code linting on every code push, creating a badge to indicate the status.
- **[Create Pull Request](.github/workflows/open_pr.yml)**: Automatically generates a pull request from `dev` to `master` whenever new changes are pushed to `dev`, or triggered manually. 