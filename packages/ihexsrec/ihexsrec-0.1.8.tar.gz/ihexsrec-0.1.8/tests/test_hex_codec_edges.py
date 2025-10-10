# tests/test_hex_codec_edges.py
import pytest
from ihexsrec import MemoryImage, IntelHexCodec, ImageError

def _hex_line(count, addr, rtype, data):
    # count must be len(data)
    assert count == len(data)
    payload = bytes([count]) + addr.to_bytes(2, "big") + bytes([rtype]) + bytes(data)
    return ":" + payload.hex().upper() + f"{IntelHexCodec._csum(payload):02X}"

def test_hex_parse_with_ela_and_data_spanning_boundaries():
    # Build valid ELA + data records programmatically
    lines = []
    # ELA = 0x0001
    lines.append(_hex_line(2, 0x0000, 0x04, (0x0001).to_bytes(2, "big")))
    # 16 bytes at 0x10000: 01..10
    lines.append(_hex_line(16, 0x0000, 0x00, bytes(range(1, 17))))
    # ELA = 0x0002
    lines.append(_hex_line(2, 0x0000, 0x04, (0x0002).to_bytes(2, "big")))
    # 16 bytes at 0x20000: 11..20
    lines.append(_hex_line(16, 0x0000, 0x00, bytes(range(0x11, 0x21))))
    # EOF
    lines.append(":00000001FF")

    img = IntelHexCodec.parse_lines(lines)
    assert img.get_byte(0x10000) == 0x01
    assert img.get_byte(0x1000F) == 0x10
    assert img.get_byte(0x20000) == 0x11
    assert img.get_byte(0x2000F) == 0x20

def test_hex_parse_start_records_both_linear_and_segmented():
    lines = []
    # ELA 0 (optional)
    lines.append(_hex_line(2, 0x0000, 0x04, (0x0000).to_bytes(2, "big")))
    # Start Segment (rtype=0x03), data= CS(2) + IP(2)
    lines.append(_hex_line(4, 0x0000, 0x03, (0x0123).to_bytes(2,"big")+ (0x0456).to_bytes(2,"big")))
    # Start Linear (rtype=0x05), data= 4 bytes
    lines.append(_hex_line(4, 0x0000, 0x05, (0x01020304).to_bytes(4,"big")))
    lines.append(":00000001FF")

    img = IntelHexCodec.parse_lines(lines)
    assert img.entry.segmented == (0x0123, 0x0456)
    assert img.entry.linear == 0x01020304

def test_hex_bad_checksum_and_length_mismatch():
    # Bad checksum: correct record but flip checksum byte
    good = _hex_line(1, 0x0000, 0x00, b"\xAA")
    bad_sum = good[:-2] + ("00")  # force wrong checksum
    with pytest.raises(ImageError):
        IntelHexCodec.parse_lines([bad_sum])

    # Length mismatch: count says 0x10 but only 15 data bytes present
    broken = ":100000000102030405060708090A0B0C0D0E0F68"  # (kept for negative test)
    with pytest.raises(ImageError):
        IntelHexCodec.parse_lines([broken])
