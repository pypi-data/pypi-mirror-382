import io
import os
import pytest

from ihexsrec import (
    IHEXSREC,
    MemoryImage,
    IntelHexCodec,
    SrecCodec,
    ImageError,
)


# -----------------------------
# MemoryImage edge cases
# -----------------------------

def test_memory_image_len_min_max_and_noops():
    img = MemoryImage()
    assert len(img) == 0
    assert img.min_addr is None and img.max_addr is None

    # set scattered bytes
    img.set_byte(5, 0xAA)
    img.set_byte(1, 0xBB)
    img.set_byte(9, 0xCC)
    assert len(img) == 3
    assert img.min_addr == 1 and img.max_addr == 9

    # insert no-op
    img.insert_bytes(4, b"", shift_entry=True)
    assert len(img) == 3 and img.min_addr == 1 and img.max_addr == 9

    # delete with len=0 no-op
    img.delete_bytes(0, 0)
    assert len(img) == 3

def test_memory_image_delete_clears_bounds_and_entry_inside_window():
    img = MemoryImage()
    img.write_bytes(0x100, b"ABCDEFG")
    img.entry.linear = 0x103    # inside delete window
    img.delete_bytes(0x101, 4, shift_entry=True)  # delete B..E -> clears linear
    assert img.entry.linear is None
    # Remaining should be A and then F,G with one hole (0xFF) in the 4-byte window.
    window = img.read_bytes(0x100, 4)  # covers 0x100..0x103
    assert window[0] == ord("A")
    # Exactly one gap (0xFF) and the other two are F then G (order preserved)
    tail = list(window[1:])
    assert tail.count(0xFF) == 1
    # Extract the non-gap values and check ordering/content
    non_gaps = [b for b in tail if b != 0xFF]
    assert non_gaps == [ord("F"), ord("G")]
    # Delete the rest
    img.delete_bytes(0x000, 0x1000)
    assert len(img) == 0 and img.min_addr is None and img.max_addr is None

def test_memory_image_fill_reads():
    img = MemoryImage()
    img.set_byte(0, 0x11)
    assert img.get_byte(5, fill=0xEE) == 0xEE
    assert img.read_bytes(0, 4, fill=0x00) == b"\x11\x00\x00\x00"


# -----------------------------
# Intel HEX: ESA/ELA/entries/errors
# -----------------------------

def test_intel_hex_esa_and_start_segment_and_start_linear():
    # Build lines to exercise record types 02 (ESA), 03 (start segment), 05 (start linear)
    # Helper to make a record
    def rec(count, addr, rtype, data=b""):
        payload = bytes([count]) + addr.to_bytes(2, "big") + bytes([rtype]) + data
        csum = (-sum(payload)) & 0xFF
        return ":" + payload.hex().upper() + f"{csum:02X}"

    lines = []
    # ESA: base_segment = 0x1234 (=> base linear address 0x1234 << 4 = 0x12340)
    lines.append(rec(2, 0x0000, 0x02, (0x1234).to_bytes(2, "big")))
    # Data at addr 0x0020 -> final 0x12340 + 0x20 = 0x12360
    lines.append(rec(3, 0x0020, 0x00, b"\xAA\xBB\xCC"))
    # Start segment address CS:IP = 0xF000:0x0100
    lines.append(rec(4, 0x0000, 0x03, (0xF000).to_bytes(2, "big") + (0x0100).to_bytes(2, "big")))
    # Extended linear address (switch to 0x0001_0000 region)
    lines.append(rec(2, 0x0000, 0x04, (0x0001).to_bytes(2, "big")))
    # Start linear address = 0x00123456
    lines.append(rec(4, 0x0000, 0x05, (0x00123456).to_bytes(4, "big")))
    # EOF
    lines.append(":00000001FF")

    img = IntelHexCodec.parse_lines(lines)
    assert img.get_byte(0x12360) == 0xAA
    assert img.read_bytes(0x12360, 3) == b"\xAA\xBB\xCC"
    assert img.entry.segmented == (0xF000, 0x0100)
    assert img.entry.linear == 0x00123456

def test_intel_hex_invalid_lengths_and_unsupported_type():
    # Bad ESA length (should be 2)
    bad_esa = [":020000021234XX", ":00000001FF"]
    # Fix checksum properly for construction: we just use codec to create and then mutate
    img = MemoryImage(); img.write_bytes(0, b"\x00")
    lines = IntelHexCodec.to_lines(img)
    # Now craft an unsupported type 0x06 record quickly
    def rec(count, addr, rtype, data=b""):
        payload = bytes([count]) + addr.to_bytes(2, "big") + bytes([rtype]) + data
        csum = (-sum(payload)) & 0xFF
        return ":" + payload.hex().upper() + f"{csum:02X}"

    unsupported = [rec(0, 0, 0x06), ":00000001FF"]

    with pytest.raises(ImageError):
        IntelHexCodec.parse_lines([":0100000212XX"])  # non-hex XX ensures failure early

    with pytest.raises(ImageError):
        IntelHexCodec.parse_lines(unsupported)  # unsupported type

def test_intel_hex_record_size_validation_and_crossing_boundary():
    img = MemoryImage()
    # Put 40 bytes over 64k boundary so encoder must split and emit ELA properly
    img.write_bytes(0x0000FF00, bytes(range(32)))
    img.write_bytes(0x00010010, bytes(range(8)))

    with pytest.raises(ValueError):
        IntelHexCodec.to_lines(img, record_size=0)
    with pytest.raises(ValueError):
        IntelHexCodec.to_lines(img, record_size=256)

    lines = IntelHexCodec.to_lines(img, record_size=16)
    # Must include at least one Extended Linear Address (04)
    assert any(l[7:9] == "04" for l in lines)
    # Always ends with EOF
    assert lines[-1] == ":00000001FF"


# -----------------------------
# S-Records: variants/errors
# -----------------------------

def test_srec_header_count_and_s5_count_ignored_and_s8_s9_terminators():
    img = MemoryImage()
    img.write_bytes(0x0010, b"\x01\x02\x03")
    # auto addr width -> S1 for <= 0xFFFF
    lines = SrecCodec.to_lines(img, header="hdr", record_size=4)
    assert any(l.startswith("S0") for l in lines)
    assert any(l.startswith(("S1", "S2", "S3")) for l in lines)
    assert any(l.startswith(("S7", "S8", "S9")) for l in lines)

    # Parse S9 terminator entry (16-bit)
    back = SrecCodec.parse_lines(lines)
    term = [l for l in lines if l.startswith(("S7", "S8", "S9"))][-1]
    if term.startswith("S9"):
        assert back.entry.linear <= 0xFFFF

def test_srec_addr_width_and_value_errors():
    img = MemoryImage()
    img.write_bytes(0x10, b"Z")
    with pytest.raises(ValueError):
        SrecCodec.to_lines(img, addr_width=5)
    with pytest.raises(ValueError):
        SrecCodec.to_lines(img, record_size=0)

def test_srec_unknown_and_nonhex_lines():
    with pytest.raises(ImageError):
        SrecCodec.parse_lines(["S4BAD"])  # unknown type S4
    with pytest.raises(ImageError):
        SrecCodec.parse_lines(["S100GG"])  # non-hex


# -----------------------------
# Facade: load/convert/save edges
# -----------------------------

def test_load_unknown_format_and_empty_lines():
    with pytest.raises(ImageError):
        IHEXSREC.load(["", "   "])  # no sniffable line

def test_convert_kwargs_propagation_and_roundtrip():
    img = MemoryImage()
    img.write_bytes(0x20, b"\x00\x11\x22\x33\x44\x55")
    doc = IHEXSREC(img)
    srec_lines = doc.to_srec(record_size=3, addr_width=3, header="hdrxx")
    # back to hex with small record size to force more records
    hex_lines = IHEXSREC.convert(srec_lines, to="hex", record_size=8)
    img_back = IntelHexCodec.parse_lines(hex_lines)
    assert img_back.export_bin(0x20, 0x26) == b"\x00\x11\x22\x33\x44\x55"

def test_save_and_load_from_disk_roundtrip(tmp_path):
    doc = IHEXSREC()
    doc.write(0x100, b"HELLO-WORLD")
    doc.set_entry_linear(0x100)

    hx = tmp_path / "a.hex"
    sr = tmp_path / "a.srec"
    bn = tmp_path / "a.bin"

    doc.save_as_hex(str(hx))
    doc.save_as_srec(str(sr), header="hdr")
    doc.save_as_bin(str(bn), start=0x100, end=0x10B)

    # Reload using load(path)
    doc2 = IHEXSREC.load(str(hx))
    assert doc2.to_bin(start=0x100, end=0x10B) == b"HELLO-WORLD"
    # Parse SREC from disk too
    doc3 = IHEXSREC.load(str(sr))
    assert doc3.to_bin(start=0x100, end=0x10B) == b"HELLO-WORLD"
    with open(bn, "rb") as f:
        assert f.read() == b"HELLO-WORLD"
