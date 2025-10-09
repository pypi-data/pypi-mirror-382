import pytest
from ihexsrec import MemoryImage, ImageError

def test_move_window_overwrite_false_allows_self_overlap():
    img = MemoryImage()
    img.write_bytes(0x1000, b"\xAA\xBB\xCC\xDD")

    # Move overlapping forward by +1 with overwrite=False; should NOT raise
    moved = img.move_window(to=0x1001, start=0x1000, end=0x1004, overwrite=False, shift_entry=False)
    assert moved == 4
    # Now only dest exists (move semantics)
    assert img.get_byte(0x1001) == 0xAA
    assert img.get_byte(0x1004) == 0xDD
    assert img.get_byte(0x1000, fill=0x00) == 0x00  # source removed

def test_move_window_overwrite_false_blocks_external_collision():
    img = MemoryImage()
    img.write_bytes(0x2000, b"\x11\x22\x33")
    img.write_bytes(0x3001, b"\xEE")  # pre-existing destination byte (not part of move)

    with pytest.raises(ImageError):
        img.move_window(to=0x3000, start=0x2000, end=0x2003, overwrite=False)

def test_copy_window_replace_false_writes_only_empty():
    img = MemoryImage()
    img.write_bytes(0x4000, b"\x01\x02\x03")
    img.set_byte(0x5001, 0xEE)  # block middle
    written = img.copy_window(to=0x5000, start=0x4000, end=0x4003, replace=False)
    assert written == 2
    assert img.get_byte(0x5000) == 0x01
    assert img.get_byte(0x5001) == 0xEE
    assert img.get_byte(0x5002) == 0x03
