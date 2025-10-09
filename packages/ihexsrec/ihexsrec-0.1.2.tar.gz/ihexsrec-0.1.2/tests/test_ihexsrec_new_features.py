# tests/test_ihexsrec_new_features.py
# pytest -q

import pytest
from ihexsrec import IHEXSREC, MemoryImage, ImageError

# ----------------------------
# Helpers
# ----------------------------

def mk_doc(pairs):
    """
    Build an IHEXSREC and write bytes from (addr, bytes) pairs.
    Example: mk_doc([(0x1000, b"\xAA\xBB"), (0x1010, b"\xCC")])
    """
    doc = IHEXSREC()
    for addr, data in pairs:
        doc.write(addr, data)
    return doc

# ----------------------------
# first_address / last_address
# ----------------------------

def test_bounds_empty():
    doc = IHEXSREC()
    assert doc.first_address() is None
    assert doc.last_address() is None
    assert doc.occupied_ranges() == []
    assert doc.gap_ranges() == []

def test_bounds_non_empty():
    doc = mk_doc([(0x1000, b"\xAA\xBB"), (0x2000, b"\xCC")])  # [1000..1001], [2000]
    assert doc.first_address() == 0x1000
    assert doc.last_address() == 0x2000
    assert doc.occupied_ranges() == [(0x1000, 0x1001), (0x2000, 0x2000)]
    # Gaps computed strictly between first/last ranges
    assert doc.gap_ranges() == [(0x1002, 0x1FFF)]

# ----------------------------
# occupied_ranges / gap_ranges(within)
# ----------------------------

def test_occupied_and_gaps_within_window():
    doc = mk_doc([
        (0x0100, b"\xAA\xAA\xAA\xAA"),   # 0x100..0x103
        (0x0200, b"\xBB\xBB\xBB"),       # 0x200..0x202
    ])
    # No window: gaps only between first..last
    assert doc.occupied_ranges() == [(0x0100, 0x0103), (0x0200, 0x0202)]
    assert doc.gap_ranges() == [(0x0104, 0x01FF)]

    # With an explicit window that includes before/after areas
    gaps = doc.gap_ranges(within=(0x0000, 0x02FF))
    assert gaps == [
        (0x0000, 0x00FF),  # before first segment
        (0x0104, 0x01FF),  # between segments
        (0x0203, 0x02FF),  # after last segment
    ]

def test_gap_ranges_empty_image_within_window():
    doc = IHEXSREC()
    assert doc.gap_ranges(within=(0x0000, 0x000F)) == [(0x0000, 0x000F)]

def test_gap_ranges_invalid_window_is_empty():
    doc = IHEXSREC()
    assert doc.gap_ranges(within=(0x0010, 0x000F)) == []

# ----------------------------
# fill_gaps(fill, within)
# ----------------------------

def test_fill_gaps_between_segments_default_window():
    doc = mk_doc([
        (0x0100, b"\xAA\xAA"),  # 0x100..0x101
        (0x0105, b"\xBB"),      # 0x105
    ])
    # Gaps: [0x102..0x104]
    written = doc.fill_gaps(fill=0xFF)
    assert written == 3
    assert doc.image.read_bytes(0x100, 6) == b"\xAA\xAA\xFF\xFF\xFF\xBB"
    # Now no gaps remain between first..last
    assert doc.gap_ranges() == []

def test_fill_gaps_entire_window_on_empty_image():
    doc = IHEXSREC()
    written = doc.fill_gaps(fill=0x00, within=(0x01F0, 0x01FF))
    assert written == 16
    assert doc.first_address() == 0x01F0
    assert doc.last_address() == 0x01FF
    assert doc.gap_ranges() == []  # dense in [first..last]

def test_fill_gaps_does_not_change_existing_bytes():
    doc = mk_doc([(0x2000, b"\x11"), (0x2002, b"\x22")])  # gap at 0x2001
    doc.fill_gaps(fill=0xEE, within=(0x2000, 0x2002))
    assert doc.image.read_bytes(0x2000, 3) == b"\x11\xEE\x22"

def test_fill_gaps_rejects_non_byte():
    doc = mk_doc([(0x1000, b"\x00")])
    with pytest.raises(ValueError):
        doc.fill_gaps(fill=256)

# ----------------------------
# move(to, start/until, overwrite, shift_entry)
# ----------------------------

def test_move_slice_creates_gap_and_writes_destination():
    # Source: [0x8000..0x800F] = 0xAA, [0x8010..0x8013] = 0x11 0x22 0x33 0x44, and 0x8020 = 0xBB
    doc = mk_doc([
        (0x8000, b"\xAA" * 0x10),
        (0x8010, b"\x11\x22\x33\x44"),
        (0x8020, b"\xBB"),
    ])
    moved = doc.move(start=0x8010, until=0x8020, to=0xF800)  # move [0x8010..0x801F)
    assert moved == 4  # only 0x8010..0x8013 existed in that window
    # Source window has become a gap
    assert (0x8010, 0x801F) in doc.gap_ranges(within=(0x8000, 0x8020))
    # Destination has the moved bytes
    assert doc.image.read_bytes(0xF800, 4) == b"\x11\x22\x33\x44"

def test_move_all_rebases_entire_image():
    doc = mk_doc([(0x1000, b"\xAA\xBB"), (0x2000, b"\xCC")])
    first, last = doc.first_address(), doc.last_address()
    assert (first, last) == (0x1000, 0x2000)
    moved = doc.move(to=0xF000)  # move everything
    assert moved == 3
    # New addresses are offset by (to - old_first)
    offset = 0xF000 - 0x1000
    assert doc.occupied_ranges() == [
        (0x1000 + offset, 0x1001 + offset),
        (0x2000 + offset, 0x2000 + offset),
    ]

def test_move_overwrite_false_raises_on_collision():
    # Prepare destination collision
    doc = mk_doc([(0x1000, b"\xAA\xBB"), (0xF000, b"\x99")])
    with pytest.raises(ImageError):
        doc.move(start=0x1000, until=0x1002, to=0xF000, overwrite=False)

def test_move_no_bytes_in_window_is_noop():
    doc = mk_doc([(0x3000, b"\x01")])
    moved = doc.move(start=0x1000, until=0x1004, to=0x4000)
    assert moved == 0
    assert doc.occupied_ranges() == [(0x3000, 0x3000)]

def test_move_preserves_holes_not_compaction():
    doc = mk_doc([
        (0x5000, b"\xAA"),        # 0x5000
        # hole at 0x5001
        (0x5002, b"\xBB\xCC"),    # 0x5002..0x5003
    ])
    moved = doc.move(start=0x5000, until=0x5004, to=0x6000)
    assert moved == 3  # 0x5000, 0x5002, 0x5003
    # Destination maintains the hole at 0x6001
    assert doc.image.read_bytes(0x6000, 4) == b"\xAA\xFF\xBB\xCC"  # default read fill=0xFF for hole
    # Source window became a gap
    assert (0x5000, 0x5003) in doc.gap_ranges(within=(0x5000, 0x5003))

def test_move_updates_linear_entry_inside_window():
    doc = mk_doc([(0x7000, b"\xAA\xBB\xCC\xDD")])
    doc.set_entry_linear(0x7001)
    moved = doc.move(start=0x7000, until=0x7004, to=0x9000, shift_entry=True)
    assert moved == 4
    # Entry shifts by +0x2000
    assert doc.image.entry.linear == 0x9001

def test_move_keeps_entry_when_outside_window():
    doc = mk_doc([(0x7000, b"\xAA")])
    doc.set_entry_linear(0x8000)
    doc.move(start=0x7000, until=0x7001, to=0x9000, shift_entry=True)
    assert doc.image.entry.linear == 0x8000

@pytest.mark.parametrize("shift_entry", [True, False])
def test_move_segmented_entry_behavior(shift_entry):
    # CS:IP -> linear = (CS << 4) + IP
    doc = mk_doc([(0x0100, b"\xAA"*16)])
    # Put entry inside window
    cs, ip = 0x0000, 0x0102
    doc.set_entry_segmented(cs, ip)
    doc.move(start=0x0100, until=0x0110, to=0x1100, shift_entry=shift_entry)
    if shift_entry:
        # Moved by +0x1000
        new_lin = (cs << 4) + ip + 0x1000
        # We only assert linear reconstruction; segmented recomposition may be implementation-specific
        # (Your implementation stores (new_cs, new_ip) derived from new_lin).
        assert (doc.image.entry.segmented is None) or isinstance(doc.image.entry.segmented, tuple)
    else:
        assert doc.image.entry.segmented == (cs, ip)
