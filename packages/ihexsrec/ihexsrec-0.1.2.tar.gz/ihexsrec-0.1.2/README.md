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

### Common Methods (`IHEXSREC`)

| Method | Description |
|---------|--------------|
| `load(path_or_lines)` | Load Intel HEX or Motorola SREC automatically and return an `IHEXSREC` instance. |
| `to_intel_hex(record_size=16)` | Convert the in-memory image to Intel HEX lines. |
| `to_srec(record_size=16, addr_width=None, header="ihexsrec")` | Convert the in-memory image to Motorola SREC lines. |
| `save_as_hex(path, record_size=16)` | Save the current image as an Intel HEX file. |
| `save_as_srec(path, record_size=16, addr_width=None, header="ihexsrec")` | Save the current image as a Motorola SREC file. |
| `to_bin(start=None, end=None, fill=0xFF)` | Export a raw binary slice of the image as bytes. |
| `save_as_bin(path, start=None, end=None, fill=0xFF)` | Save the current image (or a region) to a binary file. |
| `write(addr, data)` | Overwrite bytes starting at a specific address. |
| `insert(addr, data, shift_entry=False)` | Insert bytes and shift subsequent addresses upward. |
| `delete(addr, length, shift_entry=False)` | Delete a range of bytes and shift subsequent bytes downward. |
| `set_entry_linear(addr)` | Set or clear the **linear** entry point (e.g., 32-bit start address). |
| `set_entry_segmented(cs, ip)` | Set the **segmented** entry point (CS:IP pair). |
| `first_address()` | Return the lowest address present in memory, or `None` if empty. |
| `last_address()` | Return the highest address present in memory, or `None` if empty. |
| `occupied_ranges()` | Return a list of contiguous occupied address ranges as `(start, end_inclusive)` tuples. |
| `gap_ranges(within=None)` | Return a list of address gaps as `(start, end_inclusive)` tuples, optionally within a given window. |
| `fill_gaps(fill, within=None)` | Fill all detected gaps with a given one-byte value (e.g. `0xFF`). |
| `move(to, start=None, until=None, overwrite=True, shift_entry=True)` | Move a window of bytes—or the entire image—to a new base address. |
| `convert(input_lines_or_path, to, **kwargs)` | Convert directly from HEX→SREC or SREC→HEX in one step. |


# License

MIT License © 2025 Ioannis D. (devcoons)
