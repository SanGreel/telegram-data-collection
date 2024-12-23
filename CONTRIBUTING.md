# Contributing to Telegram Data Collector

Thank you for considering contributing to the Telegram Data Collector project! We welcome contributions in the form of bug reports, feature requests, and pull requests.

## Table of Contents

1. [Code Style and Formatting](#code-style-and-formatting)
1. [Programming Patterns](#programming-patterns)
1. [Data Structure Integrity](#data-structure-integrity)
1. [Development Environment Setup](#development-environment-setup)
1. [Submitting a Pull Request](#submitting-a-pull-request)

## Code Style and Formatting

- Follow PEP 8 guidelines for Python code.
- Use type hints for function signatures and class attributes.
- We use two formatters:
    1. The main formatter for basic development is [`ruff`](https://docs.astral.sh/ruff/).
    1. For enhanced formatting, at the end of the development, we use [`pylint`](https://pylint.pycqa.org/en/latest/).
- Make sure to commit the IDE or editor configuration files to the repository to ensure consistent code formatting across contributors.
- Add tests for important code paths and edge cases. We use [`pytest`](https://docs.pytest.org/en/stable/) for testing.

## Programming Patterns

- Use classes to encapsulate related data and behavior.
- Follow the Single Responsibility Principle: each class should have one responsibility.
- Use inheritance and polymorphism where appropriate to promote code reuse and flexibility.
- Use dependency injection to manage dependencies between classes. For such purposes, we use [`factory.py`](/telegram_data_downloader/factory.py) module.
- Use asynchronous programming patterns where appropriate, especially for I/O-bound operations.

## Data Structure Integrity

**Important:** Do not change the fields in the resulting data structures (see [`dict_types/`](/telegram_data_downloader/dict_types/)). These structures are used throughout the codebase and any changes can lead to inconsistencies and bugs. Any changes have to be discussed and agreed upon by the maintainers.

## Development Environment Setup

1. Clone the repository:

    ```bash
    git clone <repo-url>
    cd telegram-data-collector
    ```

1. Install the package manager used by the project - [Poetry](https://python-poetry.org/):

    ```bash
    python3.11 -m pip install poetry
    ```

1. Install dependencies:

    ```bash
    poetry install
    ```

    In case you want to install the virtual environment in the current directory and not in the default Poetry location, you can run:

    ```bash
    POETRY_VIRTUALENVS_IN_PROJECT=true poetry install
    ```

1. Copy the [.env.sample](/.env.sample) and fill in the required values:

    ```bash
    cp .env.sample .env
    ```

    For basic usage, you only need to fill in the `API_ID` and `API_HASH` values. These can be obtained from [my.telegram.org](https://my.telegram.org/apps).

1. Activate the virtual environment:

    ```bash
    poetry shell
    ```

1. Run the tests:

    ```bash
    PYTHONPATH=$(pwd) pytest -v
    ```

    If you want to run test coverage, you can use:

    ```bash
    PYTHONPATH=$(pwd) pytest --cov=telegram_data_downloader
    ```

1. After making all your changes, run `ruff` and `pylint` for format validation:

    ```bash
    ruff
    ```

    ```bash
    pylint telegram_data_downloader
    ```

## Submitting a Pull Request

1. Fork the repository and create your branch from `master`.
1. If you've added code that should be tested, add tests.
1. Ensure the test suite passes.
1. Make sure your code lints.
1. If your code has substantial changes, update the [README.md](/README.md) and [CONTRIBUTING.md](/CONTRIBUTING.md) with details of changes to the interface.
1. Run the tests and ensure they pass. Try to reach the highest coverage possible.
1. Format your code with `ruff` and `pylint`.
1. Submit a pull request with a clear description of your changes.

<!-- markdownlint-disable-next-line MD026 -->
### Thank you for contributing!
