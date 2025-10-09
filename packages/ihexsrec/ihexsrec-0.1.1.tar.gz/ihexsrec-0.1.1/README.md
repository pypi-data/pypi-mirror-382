# ihexsrec - Python package for Intel Hex and Motorola SREC files

[![PyPI - Version](https://img.shields.io/pypi/v/ihexrec?style=for-the-badge)](https://pypi.org/project/ihexsrec)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ihexsrec?style=for-the-badge)
![GitHub License](https://img.shields.io/github/license/devcoons/ihexsrec?style=for-the-badge)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/ihexsrec?style=for-the-badge&color=%23F0F)

A lightweight Python library for reading, writing, and converting between Intel HEX and Motorola S-Record files.
It also provides an in-memory representation of binary data (MemoryImage) that can be modified and exported in multiple formats.

## Features

- Parse Intel HEX (.hex) and Motorola SREC (.srec) files
- Convert between HEX ↔ SREC
- Modify memory data in-place (insert, delete, overwrite)
- Export to binary (.bin) format
- Preserve and modify entry points (linear or segmented)
- No external dependencies, pure Python 3
- MIT licensed

## Installation

```
pip install ihexsrec
```

## Quick Example

```
from ihexsrec import IHEXSREC

# Load from an Intel HEX file
doc = IHEXSREC.load("firmware.hex")

# Modify bytes
doc.write(0x1000, b"\x01\x02\x03\x04")

# Convert to SREC and save
doc.save_as_srec("firmware.srec")

# Export a raw binary region
data = doc.to_bin(start=0x1000, end=0x2000)
with open("firmware.bin", "wb") as f:
    f.write(data)
```

## API Overview

### Core Classes

- MemoryImage: Sparse in-memory representation of addressable bytes
- IntelHexCodec: Intel HEX parser and encoder
- SrecCodec: Motorola SREC parser and encoder
- IHEXSREC: High-level facade providing load/save/convert helpers

### Common Methods (IHEXSREC)

- `load(path_or_lines)` : Load HEX or SREC file automatically
- `to_intel_hex()` / `to_srec()` : Convert memory image to text lines
- `save_as_hex(path)` / `save_as_srec(path)` : Save as Intel HEX or SREC
- `to_bin(start=None, end=None)` / `save_as_bin(path)` : Export to raw binary
- `insert(addr, data)` / `delete(addr, length)` : Modify image data
- `set_entry_linear(addr)` / `set_entry_segmented(cs, ip)` : Manage entry points

# License

MIT License © 2025 Ioannis D. (devcoons)
