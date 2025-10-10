# tests/test_copy.py
import pytest

from ihexsrec import MemoryImage, IHEXSREC, ImageError

def bytes_at(img: MemoryImage, addr: int, n: int) -> bytes:
    return bytes(img.get_byte(addr + i) for i in range(n))

def make_img_at(addr: int, data: bytes) -> MemoryImage:
    img = MemoryImage()
    img.write_bytes(addr, data)
    return img

def test_copy_into_empty_area_replace_false():
    img = make_img_at(0x800, b"\xDE\xAD\xBE\xEF")
    written = img.copy_window(to=0xF000, start=0x800, end=0x804, replace=False)
    assert written == 4

    assert bytes_at(img, 0x800, 4) == b"\xDE\xAD\xBE\xEF"
    assert bytes_at(img, 0xF000, 4) == b"\xDE\xAD\xBE\xEF"

    assert img.first_address() == 0x800
    assert img.last_address() >= 0xF003

def test_copy_into_nonempty_area_replace_false_skips_existing():
    img = make_img_at(0x800, b"\xAA\xBB\xCC")
    img.set_byte(0xF001, 0xEE)

    written = img.copy_window(to=0xF000, start=0x800, end=0x803, replace=False)
    assert written == 2

    assert img.get_byte(0xF000) == 0xAA
    assert img.get_byte(0xF001) == 0xEE   
    assert img.get_byte(0xF002) == 0xCC

def test_copy_into_nonempty_area_replace_true_overwrites():
    img = make_img_at(0x900, b"\x11\x22\x33")
    img.write_bytes(0xA000, b"\xFF\xFF\xFF")

    written = img.copy_window(to=0xA000, start=0x900, end=0x903, replace=True)
    assert written == 3
    assert bytes_at(img, 0xA000, 3) == b"\x11\x22\x33"

def test_copy_overlap_forward_memmove_safe():
    data = b"\x01\x02\x03\x04"
    img = make_img_at(0x1000, data)

    written = img.copy_window(to=0x1001, start=0x1000, end=0x1004, replace=True)
    assert written == 4

    assert bytes_at(img, 0x1001, 4) == data
    assert bytes_at(img, 0x1000, 4) == b"\x01\x01\x02\x03"


def test_copy_overlap_backward_memmove_safe():
    data = b"\x10\x20\x30\x40"
    img = make_img_at(0x2001, data)

    written = img.copy_window(to=0x2000, start=0x2001, end=0x2005, replace=True)
    assert written == 4

    assert bytes_at(img, 0x2000, 4) == data
    assert bytes_at(img, 0x2001, 4) == b"\x20\x30\x40\x40"


def test_copy_does_not_change_entry_points():
    img = make_img_at(0x3000, b"\xAA\xBB\xCC")
    img.entry.linear = 0x12345678
    img.entry
