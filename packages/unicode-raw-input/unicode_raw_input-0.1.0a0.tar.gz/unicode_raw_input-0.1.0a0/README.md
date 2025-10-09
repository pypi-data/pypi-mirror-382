# unicode-raw-input

A cross-platform Unicode-aware replacement for Python's `raw_input()` (Python 2) and `input()` (Python 3) that handles Unicode text consistently across Python versions and operating systems.

## Installation

```bash
pip install unicode-raw-input
```

## Usage

```python
# coding=utf-8
from unicode_raw_input import unicode_raw_input

# Get Unicode text input from user
name = unicode_raw_input(u"Please enter your name: ")
print(u"Hello, " + name)
```

The function returns `typing.Text` (Unicode strings) regardless of Python version, ensuring consistent behavior across Python 2 and 3.

## Contributing

Contributions are welcome! Please submit pull requests or open issues on the GitHub repository.

## License

This project is licensed under the [MIT License](LICENSE).