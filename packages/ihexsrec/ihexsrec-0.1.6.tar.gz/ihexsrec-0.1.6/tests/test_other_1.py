import pytest
from ihexsrec import MemoryImage, IHEXSREC

def _linear_bytes(n: int) -> bytes:
    # 0x00, 0x01, ..., n-1 (mod 256)
    return bytes(range(n))

def test_replace_and_copy_with_memoryimage():
    """
    Build a 100-byte image with values 0..99.
    1) Replace bytes at addresses 5..10 (inclusive) with 6 new bytes.
    2) Copy bytes [20,40) (half-open) to the end (address 100).
    Validate boundaries, contents, and new size.
    """
    original = _linear_bytes(100)

    img = MemoryImage()
    img.write_bytes(0, original)
    assert img.first_address() == 0
    assert img.last_address() == 99

    # 1) Replace 5..10 inclusive => write 6 bytes at address 5
    repl = b"\xAA\xBB\xCC\xDD\xEE\xFF"  # length 6
    img.write_bytes(5, repl)

    # Check neighborhood: before/after replacement boundary
    assert img.get_byte(4) == original[4]          # unchanged
    assert bytes(img.read_bytes(5, 6)) == repl     # replaced region
    assert img.get_byte(11) == original[11]        # unchanged right after

    # Image size/bounds unchanged by an in-place overwrite
    assert img.first_address() == 0
    assert img.last_address() == 99

    # 2) Copy [20,40) (20 bytes) to end (address 100)
    # Expected payload is the original values 20..39 (unchanged by step 1)
    expected_payload = original[20:40]
    written = img.copy_window(to=100, start=20, end=40, replace=True)
    assert written == len(expected_payload)

    # Validate the new tail equals the expected payload
    tail = img.read_bytes(100, len(expected_payload))
    assert tail == expected_payload

    # Bounds and total span should now cover 0..119
    assert img.first_address() == 0
    assert img.last_address() == 119

    # Optional: export and confirm total length is 120 bytes
    flat = img.export_bin()
    assert len(flat) == 120
    # spot-check a few bytes
    assert flat[0] == 0x00
    assert flat[4] == 0x04
    assert flat[5:11] == repl                      # replaced region reflected in flat export
    assert flat[100:120] == expected_payload       # copied region appended

def test_replace_and_copy_with_facade():
    """
    Same scenario using the IHEXSREC façade:
      - overwrite 5..10 inclusive
      - copy [20,40) to end
    """
    original = _linear_bytes(100)

    doc = IHEXSREC()
    doc.write(0, original)

    # Replace 6 bytes starting at address 5
    repl = b"\xA1\xB2\xC3\xD4\xE5\xF6"
    doc.write(5, repl)

    # Copy [20,40) to the end (address 100)
    n = doc.copy(start=20, until=40, to=100, replace=True)
    assert n == 20

    img = doc.image
    assert img.first_address() == 0
    assert img.last_address() == 119

    # Validate contents
    assert bytes(img.read_bytes(5, 6)) == repl
    assert bytes(img.read_bytes(100, 20)) == original[20:40]
