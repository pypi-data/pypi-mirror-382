# lh-text-utils

Simple text processing utilities for Python.

## Installation

```bash
pip install lh-text-utils
```

## Usage

```python
from lh_text_utils import clean_text, word_count, slugify

# Clean and normalize text
clean_text("  Hello World!  ")  # "hello world!"

# Count words
word_count("Hello World!")  # 2

# Create URL slug
slugify("Hello World!")  # "hello-world"
```

## Functions

- `clean_text(text)` - Strip whitespace, normalize spaces, lowercase
- `word_count(text)` - Count words in text
- `slugify(text)` - Convert text to URL-friendly slug

**Requirements:** Python 3.11+  
**License:** MIT  
**Author:** Lokesh Soni