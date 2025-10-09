import pytest
from ihexsrec import MemoryImage, IntelHexCodec, ImageError

def _corrupt_intel_hex_checksum(line: str) -> str:
    assert line.startswith(":")
    # Turn the hex (without colon) into bytes, bump checksum by 1
    raw = bytes.fromhex(line[1:])
    bad = bytearray(raw)
    bad[-1] = (bad[-1] + 1) & 0xFF
    return ":" + bytes(bad).hex().upper()

def test_intel_hex_roundtrip_basic_and_ela_boundaries():
    img = MemoryImage()
    # Put data around a 64k boundary to enforce ELA records
    img.write_bytes(0x0000, b"\x11\x22\x33")
    img.write_bytes(0x10000, b"\xAA\xBB\xCC")  # forces ELA change
    img.entry.linear = 0x12345678

    lines = IntelHexCodec.to_lines(img, record_size=16)
    assert lines[0].startswith(":") and lines[-1] == ":00000001FF"
    # There should be at least one Extended Linear Address record (type 04)
    assert any(l[7:9] == "04" for l in lines)

    # Parse back
    img2 = IntelHexCodec.parse_lines(lines)
    assert img2.read_bytes(0x0000, 3) == b"\x11\x22\x33"
    assert img2.read_bytes(0x10000, 3) == b"\xAA\xBB\xCC"
    assert img2.entry.linear == 0x12345678

def test_intel_hex_empty_image_emits_eof_only():
    empty = MemoryImage()
    lines = IntelHexCodec.to_lines(empty)
    assert lines == [":00000001FF"]
    # Parsing that gives empty image again
    back = IntelHexCodec.parse_lines(lines)
    assert len(back) == 0 and back.export_bin() == b""

def test_intel_hex_detects_bad_checksum():
    img = MemoryImage()
    img.write_bytes(0x0000, b"\xDE\xAD\xBE\xEF")
    lines = IntelHexCodec.to_lines(img)
    # Corrupt the first data record (skip any 04 ELA if present)
    first_data_idx = next(i for i, l in enumerate(lines) if l[7:9] == "00")
    bad = lines[:]
    bad[first_data_idx] = _corrupt_intel_hex_checksum(lines[first_data_idx])
    with pytest.raises(ImageError):
        IntelHexCodec.parse_lines(bad)

def test_intel_hex_rejects_non_hex_or_missing_colon():
    with pytest.raises(ImageError):
        IntelHexCodec.parse_lines(["not-hex"])
    with pytest.raises(ImageError):
        IntelHexCodec.parse_lines([":GG"])  # non-hex
