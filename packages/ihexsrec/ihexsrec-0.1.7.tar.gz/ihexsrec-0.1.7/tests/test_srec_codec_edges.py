# tests/test_srec_codec_edges.py
import pytest
from ihexsrec import MemoryImage, SrecCodec, ImageError

def srec_build(typ: str, addr: int, data: bytes = b"") -> str:
    if typ in ("0", "1", "5", "9"):
        addr_len = 2
    elif typ in ("2", "8"):
        addr_len = 3
    elif typ in ("3", "7"):
        addr_len = 4
    else:
        raise ValueError("bad type")
    count = addr_len + len(data) + 1
    rec = bytes([count]) + addr.to_bytes(addr_len, "big") + data
    csum = SrecCodec._csum_bytes(rec)
    return f"S{typ}{rec.hex().upper()}{csum:02X}"

def test_srec_parse_s1_s2_s3_and_start_records():
    s0 = srec_build("0", 0x0000, b"TEST")            # header
    s1 = srec_build("1", 0x0010, b"\xAA")            # S1 @ 0x0010
    s2 = srec_build("2", 0x010020, b"\xBB")          # S2 @ 0x010020
    s3 = srec_build("3", 0x10000030, b"\xCC")        # S3 @ 0x10000030
    s7 = srec_build("7", 0x10000030, b"")            # Start address
    img = SrecCodec.parse_lines([s0, s1, s2, s3, s7])
    assert img.get_byte(0x0010) == 0xAA
    assert img.get_byte(0x010020) == 0xBB
    assert img.get_byte(0x10000030) == 0xCC
    assert img.entry.linear == 0x10000030

def test_srec_to_lines_addr_width_and_record_size():
    img = MemoryImage()
    img.set_byte(0x00FF, 0x11)
    img.set_byte(0x20_0000, 0x22)
    img.set_byte(0x1_0000_010, 0x33)

    lines = SrecCodec.to_lines(img, record_size=16, addr_width=4, header="hdr")
    assert any(line.startswith("S0") for line in lines)
    assert any(line.startswith("S3") for line in lines)
    assert lines[-1].startswith(("S7", "S8", "S9"))

def test_srec_bad_checksum_and_type():
    # bad checksum: flip last two hex digits
    good = srec_build("1", 0x0020, b"\xAA\xBB")
    bad = good[:-2] + "00"
    with pytest.raises(ImageError):
        SrecCodec.parse_lines([bad])

    with pytest.raises(ImageError):
        SrecCodec.parse_lines(["SX1300000000"])
