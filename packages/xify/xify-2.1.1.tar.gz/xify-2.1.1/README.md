# Xify

<p align="center">
  <a href="https://pypi.org/project/xify/"><img alt="PyPI" src="https://img.shields.io/pypi/v/xify?color=blue"></a>
  <a href="https://pypi.org/project/xify/"><img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/xify"></a>
  <a href="https://github.com/filming/xify/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/badge/License--yellow.svg"></a>
</p>

Xify is a Python client for interacting with the X (formerly Twitter) API. This library provides an asynchronous interface to perform common tasks like creating tweets as well as providing authentication and custom error handling.

---

## Features

- **Send Tweets:** Contains functionality to send tweets. 
- **OAuth 1.0a Authentication:** Sign and authenticate requests to the X API.
- **Async HTTP Requests:** Uses `aiohttp` for efficient, non-blocking network operations.
- **Developer Experience:** Includes ruff, mypy, pre-commit, and commitizen for high-quality code.

---

## Installation

### From PyPI (Recommended)

```bash
pip install xify
```

### From Source

You can install Xify by cloning the repository directly or using pre-built wheel files.

**Prerequisites:** This project requires [uv](https://github.com/astral-sh/uv) for dependency management.

#### Option 1: Clone and Build

1. Clone the repository:
   ```bash
   git clone https://github.com/filming/xify.git
   cd xify
   ```

2. Install the project and its dependencies:
   ```bash
   uv sync
   ```

#### Option 2: Install from Pre-built Wheels

Pre-built wheel files are attached to each GitHub release. You can download and install them directly:

1. Go to the [GitHub releases page](https://github.com/filming/xify/releases)
2. Download the `.whl` file from the latest release
3. Install using pip:
   ```bash
   pip install path/to/downloaded/xify-*.whl
   ```

---

## Usage

Here's a basic example of how to use `Xify` to send out a tweet:

```python
import asyncio
from xify import Xify

async def main():
   x_consumer_key = "1111111111"
   x_consumer_secret = "2222222222"
   x_access_token = "3333333333"
   x_access_token_secret = "4444444444"

   async with Xify(
      x_consumer_key=x_consumer_key,
      x_consumer_secret=x_consumer_secret,
      x_access_token=x_access_token,
      x_access_token_secret=x_access_token_secret,
    ) as client:
      response = await client.tweet({"msg": "hello!"})

if __name__ == "__main__":
   asyncio.run(main())
```

---

## Development

This project uses modern Python development tools:

- **[uv](https://github.com/astral-sh/uv)** for dependency management
- **[ruff](https://github.com/astral-sh/ruff)** for linting and formatting  
- **[mypy](https://mypy.readthedocs.io/)** for type checking
- **[pre-commit](https://pre-commit.com/)** for git hooks
- **[commitizen](https://commitizen-tools.github.io/commitizen/)** for conventional commits

### Setting up for development:

1. Clone the repository:
   ```bash
   git clone https://github.com/filming/xify.git
   cd xify
   ```

2. Install dependencies (including dev tools):
   ```bash
   uv sync --extra dev
   ```

3. Set up pre-commit hooks:
   ```bash
   uv run pre-commit install
   ```
   
4. Start developing!

---

## Dependencies

All project dependencies are managed via [`pyproject.toml`](pyproject.toml) and use Python 3.10+.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contributing

Contributions, bug reports, and feature requests are welcome!
Please open an issue or submit a pull request on [GitHub](https://github.com/filming/xify).