# ropey-py

Python bindings for the Rust [`ropey`](https://crates.io/crates/ropey) text rope library, built with PyO3.

---

## Features

- Fast, Unicode-aware text manipulation.
- Efficient insertions, deletions, and slicing.
- Conversion between byte, character, and line indices.
- Ideal for text editors and large document processing.

---

## Installation

Install directly from PyPI:

```bash
pip install ropey-py
```

---

## Example

```python
from ropey_py import Rope

r = Rope("Hello,\n🌍!")

print(r.len_chars())   # 9
print(r.char(7))       # 🌍
r.insert(5, " beautiful")
print(r.to_string())   # "Hello beautiful,\n🌍!"
```
