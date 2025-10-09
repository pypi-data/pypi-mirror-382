import os
import io
import tempfile
import pytest

from ihexsrec import IHEXSREC, MemoryImage, IntelHexCodec, SrecCodec, ImageError, __version__, __name__

def test_metadata_exports():
    assert isinstance(__version__, str) and len(__version__) > 0
    assert __name__ == "ihexsrec"

def test_load_sniff_hex_and_srec_from_strings():
    # Build small HEX via codec
    img = MemoryImage()
    img.write_bytes(0x00, b"\xAA\xBB")
    hex_lines = IntelHexCodec.to_lines(img)
    srec_lines = SrecCodec.to_lines(img)

    # load(list_of_lines) with sniffing
    doc_hex = IHEXSREC.load(hex_lines)
    doc_srec = IHEXSREC.load(srec_lines)

    assert doc_hex.to_bin()[:2] == b"\xAA\xBB"
    assert doc_srec.to_bin()[:2] == b"\xAA\xBB"

def test_convert_between_formats_and_roundtrip_equivalence():
    img = MemoryImage()
    img.write_bytes(0x20, b"\x01\x02\x03\x04")
    img.entry.linear = 0x100020

    hex_lines = IntelHexCodec.to_lines(img)
    # -> SREC using facade
    srec_lines = IHEXSREC.convert(hex_lines, to="srec", record_size=8, addr_width=3, header="testhdr")
    # and back
    hex_lines2 = IHEXSREC.convert(srec_lines, to="hex", record_size=8)

    img1 = IntelHexCodec.parse_lines(hex_lines)
    img2 = IntelHexCodec.parse_lines(hex_lines2)

    assert img1.export_bin(0x20, 0x24) == img2.export_bin(0x20, 0x24)
    assert img1.entry.linear == img2.entry.linear

def test_save_helpers_write_files(tmp_path):
    doc = IHEXSREC()
    doc.write(0x100, b"HELLO")
    doc.set_entry_linear(0x100)

    hex_path = tmp_path / "out.hex"
    srec_path = tmp_path / "out.srec"
    bin_path = tmp_path / "out.bin"

    doc.save_as_hex(str(hex_path))
    doc.save_as_srec(str(srec_path), header="hdr")
    doc.save_as_bin(str(bin_path), start=0x100, end=0x105)

    assert hex_path.exists() and srec_path.exists() and bin_path.exists()
    with open(bin_path, "rb") as f:
        assert f.read() == b"HELLO"

def test_write_insert_delete_chain_and_entries():
    d = IHEXSREC()
    d.write(0x00, b"\xAA\xBB\xCC")
    d.insert(0x01, b"\x11\x22", shift_entry=True)
    d.set_entry_linear(0x0002)  # after insert, will check separately
    # Delete including entry -> clears linear when inside window
    d.delete(0x0001, 3, shift_entry=True)  # deletes 0x01..0x03
    assert d.image.entry.linear is None

def test_convert_invalid_target_raises():
    with pytest.raises(ValueError):
        IHEXSREC.convert([], to="elf")
