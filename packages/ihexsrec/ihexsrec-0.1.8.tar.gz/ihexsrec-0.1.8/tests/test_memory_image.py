import io
import os
import tempfile
import pytest

from ihexsrec import MemoryImage, EntryPoint, ImageError

def test_memory_image_basic_rw_and_bounds():
    img = MemoryImage()
    assert len(img) == 0
    assert img.export_bin() == b""

    # Sparse writes
    img.set_byte(0x10, 0xAA)
    img.set_byte(0x12, 0xCC)
    img.write_bytes(0x11, b"\xBB\xCC")  # overwrite 0x11 and 0x12
    assert img.min_addr == 0x10
    assert img.max_addr == 0x12

    # Reads with fill
    assert img.get_byte(0x0F) == 0xFF
    assert img.read_bytes(0x10, 3) == b"\xAA\xBB\xCC"

def test_memory_image_insert_delete_and_shift_entry_linear():
    img = MemoryImage()
    img.write_bytes(0x1000, b"ABCDEF")
    img.entry.linear = 0x1003

    # Insert 2 bytes at 0x1002; everything at >= 0x1002 shifts by 2
    img.insert_bytes(0x1002, b"XY", shift_entry=True)

    assert img.read_bytes(0x1000, 8) == b"ABXYCDEF"
    # entry >= insert point -> shifted by +2
    assert img.entry.linear == 0x1005

    # Delete 3 bytes starting at 0x1001; entry >= (start+len) -> -3
    img.delete_bytes(0x1001, 3, shift_entry=True)
    # After deletion, removed B,X,Y -> remaining A C D E F
    assert img.read_bytes(0x1000, 5) == b"ACDEF"
    assert img.entry.linear == 0x1002  # 0x1005 - 3

def test_memory_image_insert_delete_and_shift_entry_segmented():
    img = MemoryImage()
    img.write_bytes(0x200, b"ABCDEFGH")
    # CS:IP -> linear = CS<<4 + IP
    img.entry.segmented = (0x1000, 0x0005)  # linear 0x10000 + 5 = 0x10005

    # Insert below entry -> no shift
    img.insert_bytes(0x0100, b"ZZ", shift_entry=True)
    assert img.entry.segmented == (0x1000, 0x0005)

    # Insert at/after entry -> shift IP (16-bit wrap in code)
    img.insert_bytes(0x10005, b"QQQ", shift_entry=True)
    cs, ip = img.entry.segmented
    assert cs == 0x1000 and ip == (0x0005 + 3) & 0xFFFF

def test_iter_segments_and_export_bin_with_fill():
    img = MemoryImage()
    img.write_bytes(0x00, b"\x01\x02\x03")
    img.write_bytes(0x10, b"\xAA\xBB")

    segs = list(img.iter_segments())
    assert segs == [
        (0x00, 0x03, b"\x01\x02\x03"),
        (0x10, 0x12, b"\xAA\xBB"),
    ]

    # Export a window covering gap -> filled with 0xFF
    blob = img.export_bin(0x00, 0x12, fill=0xEE)
    assert blob[:3] == b"\x01\x02\x03"
    assert blob[3:0x10] == b"\xEE" * (0x10 - 3)
    assert blob[0x10:0x12] == b"\xAA\xBB"