# DGI

DGI: The Deep-neural-network General Inference framework.

## Installation

You can install DGI using pip:

```bash
pip install dgi-serve
```

## Quick Start

```python
from dgi import hello_world

# Use the package
print(hello_world())
```

## Features

- Simple and easy to use
- Well documented
- Fully tested

## Usage

Here's a basic example of how to use DGI:

```python
import dgi

# Example usage
dgi.main()
```

## Development

To set up the development environment:

```bash
# Clone the repository
git clone https://github.com/deepnova/dgi-serve.git
cd dgi-serve

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
black .
flake8 .
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Wilhelm Jung

## Changelog

### 0.1.0-dev (Development Release)
- Development version of DGI package
- Basic framework structure
- Core inference functionality outline

### 0.1.0 (Initial Release)
- Initial release of DGI package
- Basic functionality implemented