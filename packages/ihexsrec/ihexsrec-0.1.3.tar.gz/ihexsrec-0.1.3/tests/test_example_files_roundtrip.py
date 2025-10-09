import io
import os
import pytest

from ihexsrec import IHEXSREC, MemoryImage, IntelHexCodec, SrecCodec


def _mk_img_with_ela_and_data():
    """
    Build a MemoryImage with data spanning an Extended Linear Address boundary
    and an explicit linear entry point.
    Layout:
      - 0x00010000.. : a block of bytes
      - 0x00010020.. : another small block
      - entry linear : 0x00010000
    """
    img = MemoryImage()
    img.write_bytes(0x00010000, bytes(range(0x10)))        # 16 bytes
    img.write_bytes(0x00010010, bytes(range(0x11, 0x21)))  # next 16 bytes
    img.write_bytes(0x00010020, b"\xDE\xAD\xBE\xEF")
    img.entry.linear = 0x00010000
    return img


def _mk_img_16bit_srec_style():
    """
    Small image with 16-bit addresses (forces S1 records when addr_width=None).
    """
    img = MemoryImage()
    img.write_bytes(0x0000, b"\x01\x02\x03\x04")
    img.write_bytes(0x0010, b"\x11\x22\x33\x44")
    return img


def _mk_img_with_segmented_entry():
    """
    Image that has a segmented entry (CS:IP). This will emit Start Segment (03)
    in Intel HEX and an S7/S8/S9 terminator chosen from linear entry for SREC.
    """
    img = MemoryImage()
    img.write_bytes(0x200, b"HELLOWORLD")
    img.entry.segmented = (0xF000, 0x0100)  # linear = 0xF0000 + 0x100
    return img


def test_example_hex_file_roundtrip(tmp_path):
    # Build the image and encode to Intel HEX lines using the library
    img = _mk_img_with_ela_and_data()
    hex_lines = IntelHexCodec.to_lines(img, record_size=16)

    # Write a real file
    hex_path = tmp_path / "example.hex"
    with open(hex_path, "w", encoding="utf-8") as f:
        f.write("\n".join(hex_lines) + "\n")

    # Reload via path
    doc = IHEXSREC.load(str(hex_path))
    assert doc.image.min_addr == 0x00010000
    assert doc.image.max_addr >= 0x00010023
    assert doc.image.entry.linear == 0x00010000

    # Convert to SREC file and reload
    srec_path = tmp_path / "example_from_hex.srec"
    doc.save_as_srec(str(srec_path), record_size=16, header="hdr")
    doc2 = IHEXSREC.load(str(srec_path))

    # Sanity on data continuity
    assert doc2.image.read_bytes(0x00010000, 0x24)[:4] == bytes(range(4))
    assert doc2.image.get_byte(0x00010020) == 0xDE
    assert doc2.image.get_byte(0x00010023) == 0xEF


def test_example_hex_with_entry_start_linear(tmp_path):
    img = _mk_img_with_ela_and_data()
    # Already has entry.linear set by builder
    hex_path = tmp_path / "example_with_entry.hex"
    with open(hex_path, "w", encoding="utf-8") as f:
        for ln in IntelHexCodec.to_lines(img, record_size=8):
            f.write(ln + "\n")

    # Reload and verify entry
    doc = IHEXSREC.load(str(hex_path))
    assert doc.image.entry.linear == 0x00010000

    # Export binary slice and check contents
    blob = doc.to_bin(start=0x00010000, end=0x00010020)
    assert blob[:4] == b"\x00\x01\x02\x03"
    assert len(blob) == 0x20


def test_example_srec_roundtrip_and_entry(tmp_path):
    # Build an image and let SREC encoder pick address width based on max addr
    img = _mk_img_with_ela_and_data()
    srec_lines = SrecCodec.to_lines(img, record_size=16, addr_width=4, header="hdr-test")

    srec_path = tmp_path / "example.srec"
    with open(srec_path, "w", encoding="utf-8") as f:
        f.write("\n".join(srec_lines) + "\n")

    doc = IHEXSREC.load(str(srec_path))
    # Convert to HEX and back to ensure round-trip
    hex_lines = doc.to_intel_hex(record_size=16)
    doc2 = IHEXSREC.load(hex_lines)
    assert doc2.image.entry.linear == img.entry.linear
    assert doc2.image.read_bytes(0x00010020, 4) == b"\xDE\xAD\xBE\xEF"


def test_tiny_16bit_srec_file(tmp_path):
    img = _mk_img_16bit_srec_style()
    # addr_width=None -> choose S1 automatically for <= 0xFFFF
    srec_lines = SrecCodec.to_lines(img, record_size=8, addr_width=None, header="tiny")
    srec_path = tmp_path / "tiny_mixed.srec"
    with open(srec_path, "w", encoding="utf-8") as f:
        f.write("\n".join(srec_lines) + "\n")

    doc = IHEXSREC.load(str(srec_path))
    # Export and verify blob matches original
    assert doc.to_bin(start=0x0000, end=0x0004) == b"\x01\x02\x03\x04"
    assert doc.to_bin(start=0x0010, end=0x0014) == b"\x11\x22\x33\x44"

    # Convert to HEX and back again with a small record size to stress splitting
    hex_lines = doc.to_intel_hex(record_size=4)
    doc2 = IHEXSREC.load(hex_lines)
    assert doc2.to_bin(start=0x0000, end=0x0014)[0:4] == b"\x01\x02\x03\x04"


def test_segmented_entry_files_both_formats(tmp_path):
    img = _mk_img_with_segmented_entry()

    # HEX path
    hex_path = tmp_path / "seg_entry.hex"
    with open(hex_path, "w", encoding="utf-8") as f:
        for ln in IntelHexCodec.to_lines(img, record_size=16):
            f.write(ln + "\n")
    doc_hex = IHEXSREC.load(str(hex_path))
    assert doc_hex.image.entry.segmented == (0xF000, 0x0100)

    # SREC path
    srec_path = tmp_path / "seg_entry.srec"
    with open(srec_path, "w", encoding="utf-8") as f:
        for ln in SrecCodec.to_lines(img, record_size=16, addr_width=4, header="hdr"):
            f.write(ln + "\n")
    doc_srec = IHEXSREC.load(str(srec_path))
    # SREC parser stores linear entry (terminator). For segmented entry we only guaranteed HEX start-segment.
    assert doc_srec.image.entry.linear is not None

    # Binary export equivalence across formats
    assert doc_hex.to_bin() == doc_srec.to_bin()


def test_example_conversion_cli_like_flow(tmp_path):
    """
    Simulate a small CLI workflow:
      - load HEX
      - save SREC
      - reload and save HEX again
      - compare binary outputs
    """
    base = _mk_img_with_ela_and_data()
    hex_in = tmp_path / "in.hex"
    with open(hex_in, "w", encoding="utf-8") as f:
        for ln in IntelHexCodec.to_lines(base, record_size=8):
            f.write(ln + "\n")

    # Load from disk
    doc = IHEXSREC.load(str(hex_in))
    # Save as SREC
    srec_out = tmp_path / "out.srec"
    doc.save_as_srec(str(srec_out), record_size=8, header="hdr")

    # Reload SREC and save back to HEX with a different record_size
    doc2 = IHEXSREC.load(str(srec_out))
    hex_out = tmp_path / "roundtrip.hex"
    doc2.save_as_hex(str(hex_out), record_size=16)

    # Compare binary payloads across all stages
    b0 = base.export_bin(base.min_addr, base.max_addr + 1)
    b1 = IHEXSREC.load(str(srec_out)).to_bin(start=base.min_addr, end=base.max_addr + 1)
    b2 = IHEXSREC.load(str(hex_out)).to_bin(start=base.min_addr, end=base.max_addr + 1)
    assert b0 == b1 == b2
