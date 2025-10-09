#########################################################################################
#                                                                                       #
# MIT License                                                                           #
#                                                                                       #
# Copyright (c) 2025 Ioannis D. (devcoons)                                              #
#                                                                                       #
# Permission is hereby granted, free of charge, to any person obtaining a copy          #
# of this software and associated documentation files (the "Software"), to deal         #
# in the Software without restriction, including without limitation the rights          #
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell             #
# copies of the Software, and to permit persons to whom the Software is                 #
# furnished to do so, subject to the following conditions:                              #
#                                                                                       #
# The above copyright notice and this permission notice shall be included in all        #
# copies or substantial portions of the Software.                                       #
#                                                                                       #
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR            #
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,              #
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE           #
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER                #
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,         #
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE         #
# SOFTWARE.                                                                             #
#                                                                                       #
#########################################################################################

from __future__ import annotations

__version__ = '0.1.2'
__name__ = "ihexsrec"
__all__ = ["IHEXSREC", "IntelHexCodec", "SrecCodec", "MemoryImage", "EntryPoint", "ImageError", "__version__"]

#########################################################################################
# IMPORTS                                                                               #
#########################################################################################


from dataclasses import dataclass
from typing import Dict, Iterable, Iterator, List, Optional, Tuple, Union

#########################################################################################
#########################################################################################

class ImageError(Exception):
    pass

#########################################################################################
#########################################################################################

@dataclass
class EntryPoint:
    linear: Optional[int] = None
    segmented: Optional[Tuple[int, int]] = None

#########################################################################################

class MemoryImage:
    def __init__(self) -> None:
        # Hold sparse bytes and track bounds and entry.
        self._mem: Dict[int, int] = {}
        self.min_addr: Optional[int] = None
        self.max_addr: Optional[int] = None
        self.entry = EntryPoint()

#########################################################################################

    @staticmethod
    def _check_addr(addr: int) -> int:
        a = int(addr)
        if a < 0:
            raise ValueError("address must be >= 0")
        return a

#########################################################################################

    def _touch_bounds(self, addr: int) -> None:
        # Update min/max bounds after a write.
        if self.min_addr is None or addr < self.min_addr:
            self.min_addr = addr
        if self.max_addr is None or addr > self.max_addr:
            self.max_addr = addr

#########################################################################################

    def set_byte(self, addr: int, value: int) -> None:
        # Write a single byte at an address.
        addr = self._check_addr(addr)
        if not (0 <= value <= 0xFF):
            raise ValueError("byte must be 0..255")
        self._mem[addr] = int(value)
        self._touch_bounds(addr)

#########################################################################################

    def get_byte(self, addr: int, *, fill: int = 0xFF) -> int:
        # Read a byte or return fill if missing.
        addr = self._check_addr(addr)
        return self._mem.get(addr, fill)

#########################################################################################

    def write_bytes(self, addr: int, data: Union[bytes, bytearray]) -> None:
        # Overwrite bytes starting at address.
        a = self._check_addr(addr)
        for i, b in enumerate(data):
            self.set_byte(a + i, b)

#########################################################################################

    def read_bytes(self, addr: int, length: int, *, fill: int = 0xFF) -> bytes:
        # Read a span of bytes with fill for gaps.
        a = self._check_addr(addr)
        if length < 0:
            raise ValueError("length must be >= 0")
        return bytes(self._mem.get(a + i, fill) for i in range(length))

#########################################################################################

    def insert_bytes(self, addr: int, data: Union[bytes, bytearray], *, shift_entry: bool = False) -> None:
        # Insert bytes and shift subsequent bytes upward.
        addr = self._check_addr(addr)
        n = len(data)
        if n == 0:
            return
        had_mem = bool(self._mem)
        keys: List[int] = []
        if self._mem:
            keys = [k for k in self._mem.keys() if k >= addr]
            for k in sorted(keys, reverse=True):
                self._mem[k + n] = self._mem.pop(k)
        for i, b in enumerate(data):
            self._mem[addr + i] = int(b)
        if self.min_addr is None or addr < self.min_addr:
            self.min_addr = addr
        if self.max_addr is None:
            self.max_addr = addr + n - 1
        else:
            moved = n if had_mem and keys else 0
            self.max_addr = max(self.max_addr + moved, addr + n - 1)
        if shift_entry and self.entry.linear is not None and addr <= self.entry.linear:
            self.entry.linear += n
        if shift_entry and self.entry.segmented is not None:
            cs, ip = self.entry.segmented
            lin = (cs << 4) + ip
            if addr >= lin:
                self.entry.segmented = (cs & 0xFFFF, (ip + n) & 0xFFFF)

#########################################################################################

    def delete_bytes(self, addr: int, length: int, *, shift_entry: bool = False) -> None:
        # Delete a window and shift subsequent bytes downward.
        addr = self._check_addr(addr); length = int(length)
        if length <= 0 or not self._mem:
            return
        for k in list(self._mem.keys()):
            if addr <= k < addr + length:
                self._mem.pop(k)
        keys = [k for k in self._mem.keys() if k >= addr + length]
        for k in sorted(keys):
            self._mem[k - length] = self._mem.pop(k)
        if self._mem:
            self.min_addr = min(self._mem.keys())
            self.max_addr = max(self._mem.keys())
        else:
            self.min_addr = self.max_addr = None
        if shift_entry and self.entry.linear is not None:
            if self.entry.linear >= addr + length:
                self.entry.linear -= length
            elif addr <= self.entry.linear < addr + length:
                self.entry.linear = None
        if shift_entry and self.entry.segmented is not None:
            cs, ip = self.entry.segmented
            lin = (cs << 4) + ip
            if lin >= addr + length:
                new_lin = lin - length
                new_ip = new_lin & 0xF
                new_cs = (new_lin - new_ip) >> 4
                self.entry.segmented = (new_cs & 0xFFFF, new_ip & 0xFFFF)
            elif addr <= lin < addr + length:
                self.entry.segmented = None

#########################################################################################

    def iter_segments(self) -> Iterator[Tuple[int, int, bytes]]:
        # Yield contiguous runs as (start, end_exclusive, data).
        if not self._mem:
            return
        addrs = sorted(self._mem.keys())
        start = prev = addrs[0]
        buf = [self._mem[start]]
        for a in addrs[1:]:
            if a == prev + 1:
                buf.append(self._mem[a])
            else:
                yield (start, prev + 1, bytes(buf))
                start = a; buf = [self._mem[a]]
            prev = a
        yield (start, prev + 1, bytes(buf))

#########################################################################################

    def export_bin(self, start: Optional[int] = None, end: Optional[int] = None, *, fill: int = 0xFF) -> bytes:
        # Export a flat binary between [start, end).
        if not self._mem:
            return b""
        lo = self.min_addr if start is None else self._check_addr(start)
        hi = (self.max_addr + 1) if end is None else self._check_addr(end)
        if lo is None or hi is None:
            return b""
        if hi < lo:
            raise ValueError("end must be >= start")
        return bytes(self._mem.get(a, fill) for a in range(lo, hi))

#########################################################################################

    def first_address(self) -> Optional[int]:
        # Lowest occupied address, or None if image is empty.
        return self.min_addr

#########################################################################################

    def last_address(self) -> Optional[int]:
        # Highest occupied address, or None if image is empty.
        return self.max_addr

#########################################################################################

    def occupied_ranges(self) -> List[Tuple[int, int]]:
        # Return a list of (start, end_inclusive) for each contiguous occupied span.
        return [(start, end_exclusive - 1) for start, end_exclusive, _ in self.iter_segments()]

#########################################################################################

    def gap_ranges(self, *, within: Optional[Tuple[int, int]] = None) -> List[Tuple[int, int]]:
        # Return a list of (start, end_inclusive) gaps between occupied ranges.
        if len(self) == 0:
            if within is None:
                return []
            lo, hi = int(within[0]), int(within[1])
            if lo > hi:           
                return []
            return [(lo, hi)]
        if within is None:
            lo = int(self.min_addr) 
            hi = int(self.max_addr)
        else:
            lo, hi = int(within[0]), int(within[1])
            if lo > hi:           
                return []
        gaps: List[Tuple[int, int]] = []
        prev = lo
        for seg_start, seg_end_excl, _ in self.iter_segments():
            if seg_end_excl - 1 < lo:
                continue
            if seg_start > hi:
                break
            seg_lo = max(seg_start, lo)
            seg_hi = min(seg_end_excl - 1, hi)
            if seg_lo <= seg_hi:
                if prev < seg_lo:
                    gaps.append((prev, seg_lo - 1))
                prev = seg_hi + 1
        if prev <= hi:
            gaps.append((prev, hi))
        return gaps

#########################################################################################

    def fill_gaps(self, *, fill: int, within: Optional[Tuple[int, int]] = None) -> int:
        # Fill every gap (unwritten address) with the given one-byte value.
        if not (0 <= int(fill) <= 0xFF):
            raise ValueError("fill must be a single byte (0..255)")
        if len(self) == 0 and within is None:
            return 0
        total = 0
        gaps = self.gap_ranges(within=within)
        if not gaps:
            return 0
        b = bytes([int(fill)])
        for start, end_incl in gaps:
            n = end_incl - start + 1
            self.write_bytes(start, b * n)
            total += n
        return total

#########################################################################################

    def move_window(self, *, to: int, start: Optional[int] = None, end: Optional[int] = None, overwrite: bool = True, shift_entry: bool = True) -> int:
        # Move a window of bytes [start, end) to base address 'to', preserving sparsity.

        if len(self) == 0:
            return 0

        if start is None or end is None:
            if self.min_addr is None or self.max_addr is None:
                return 0
            if start is None:
                start = int(self.min_addr)
            if end is None:
                end = int(self.max_addr) + 1

        start = int(start); end = int(end); to = int(to)
        if start >= end:
            return 0

        src_keys = [k for k in self._mem.keys() if start <= k < end]
        if not src_keys:
            return 0
        src_keys.sort()

        if not overwrite:
            for k in src_keys:
                dst_addr = to + (k - start)
                if dst_addr in self._mem:
                    raise ImageError(f"Destination address already occupied: 0x{dst_addr:X}")

        payload = [(to + (k - start), self._mem[k]) for k in src_keys]

        for k in src_keys:
            self._mem.pop(k)
        for addr, b in payload:
            self._mem[addr] = b
        if self._mem:
            self.min_addr = min(self._mem.keys())
            self.max_addr = max(self._mem.keys())
        else:
            self.min_addr = self.max_addr = None

        if shift_entry:
            if self.entry.linear is not None:
                lin = int(self.entry.linear)
                if start <= lin < end:
                    self.entry.linear = to + (lin - start)

            if self.entry.segmented is not None:
                cs, ip = self.entry.segmented
                lin = (int(cs) << 4) + int(ip)
                if start <= lin < end:
                    new_lin = to + (lin - start)
                    new_cs, new_ip = (new_lin >> 4) & 0xFFFF, new_lin & 0xF
                    self.entry.segmented = (new_cs, new_ip)

        return len(src_keys)
    
#########################################################################################

    def __len__(self) -> int:
        # Return number of stored addresses (not span length).
        return len(self._mem)

#########################################################################################
#########################################################################################

class IntelHexCodec:

#########################################################################################
    
    @staticmethod
    def _csum(payload: bytes) -> int:
        # Compute Intel HEX checksum byte.
        return (-sum(payload)) & 0xFF

#########################################################################################

    @staticmethod
    def parse_lines(lines: Iterable[str]) -> MemoryImage:
        # Parse Intel HEX lines into a MemoryImage.
        img = MemoryImage()
        base_linear = 0
        base_segment = 0
        for i, raw in enumerate(lines, 1):
            s = raw.strip()
            if not s:
                continue
            if not s.startswith(":"):
                raise ImageError(f"(line {i}) Intel HEX line: missing ':' -> {s!r}")
            try:
                rec = bytes.fromhex(s[1:])
            except ValueError:
                raise ImageError(f"(line {i}) Intel HEX non-hex chars -> {s!r}")
            if len(rec) < 5:
                raise ImageError(f"(line {i}) Intel HEX too short -> {s!r}")
            count = rec[0]
            if len(rec) != 5 + count:
                raise ImageError(f"(line {i}) Intel HEX length mismatch -> {s!r}")
            addr = int.from_bytes(rec[1:3], "big")
            rtype = rec[3]
            data = rec[4:4 + count]
            csum = rec[-1]
            if ((sum(rec[:-1]) + csum) & 0xFF) != 0:
                raise ImageError(f"(line {i}) Intel HEX checksum error -> {s!r}")
            if rtype == 0x00:
                base = (base_linear << 16) if base_linear else ((base_segment << 4) if base_segment else 0)
                a0 = base + addr
                for j, b in enumerate(data):
                    img.set_byte(a0 + j, b)
            elif rtype == 0x01:  # EOF
                pass
            elif rtype == 0x02:  # ESA
                if count != 2: raise ImageError(f"(line {i}) ESA length != 2")
                base_segment = int.from_bytes(data, "big")
                base_linear = 0
            elif rtype == 0x04:  # ELA
                if count != 2: raise ImageError(f"(line {i}) ELA length != 2")
                base_linear = int.from_bytes(data, "big")
                base_segment = 0
            elif rtype == 0x03:  # Start Segment
                if count != 4: raise ImageError(f"(line {i}) Start Segment length != 4")
                cs = int.from_bytes(data[0:2], "big")
                ip = int.from_bytes(data[2:4], "big")
                img.entry.segmented = (cs, ip)
            elif rtype == 0x05:  # Start Linear
                if count != 4: raise ImageError(f"(line {i}) Start Linear length != 4")
                img.entry.linear = int.from_bytes(data, "big")
            else:
                raise ImageError(f"(line {i}) Intel HEX unsupported record type {rtype:02X}")
        return img

#########################################################################################

    @staticmethod
    def to_lines(img: MemoryImage, *, record_size: int = 16) -> List[str]:
        # Emit Intel HEX lines from a MemoryImage.
        if record_size <= 0 or record_size > 255:
            raise ValueError("record_size must be 1..255")
        lines: List[str] = []
        if len(img) == 0:
            lines.append(":00000001FF")
            return lines
        # Suppress initial ELA=0000 emission; emit only on change from 0.
        current_ela: Optional[int] = 0
        for start, end, data in img.iter_segments():
            pos = start
            off = 0
            while off < len(data):
                ela = (pos >> 16) & 0xFFFF
                if current_ela != ela and ela != 0:
                    payload = bytes([2]) + (0).to_bytes(2, "big") + bytes([0x04]) + ela.to_bytes(2, "big")
                    lines.append(":" + payload.hex().upper() + f"{IntelHexCodec._csum(payload):02X}")
                    current_ela = ela
                room = min(record_size, len(data) - off, 0x10000 - (pos & 0xFFFF))
                chunk = data[off: off + room]
                payload = bytes([len(chunk)]) + (pos & 0xFFFF).to_bytes(2, "big") + bytes([0x00]) + chunk
                lines.append(":" + payload.hex().upper() + f"{IntelHexCodec._csum(payload):02X}")
                pos += len(chunk); off += len(chunk)
        if img.entry.segmented is not None:
            cs, ip = img.entry.segmented
            payload = bytes([4]) + (0).to_bytes(2, "big") + bytes([0x03]) + cs.to_bytes(2, "big") + ip.to_bytes(2, "big")
            lines.append(":" + payload.hex().upper() + f"{IntelHexCodec._csum(payload):02X}")
        if img.entry.linear is not None:
            payload = bytes([4]) + (0).to_bytes(2, "big") + bytes([0x05]) + img.entry.linear.to_bytes(4, "big")
            lines.append(":" + payload.hex().upper() + f"{IntelHexCodec._csum(payload):02X}")
        lines.append(":00000001FF")
        return lines

#########################################################################################
#########################################################################################

class SrecCodec:

#########################################################################################

    def __init__(self) -> None:
        # Namespace for S-Record helpers.
        pass

#########################################################################################

    @staticmethod
    def parse_lines(lines: Iterable[str]) -> MemoryImage:
        # Parse S-Records into a MemoryImage.
        img = MemoryImage()
        for i, raw in enumerate(lines, 1):
            s = raw.strip()
            if not s:
                continue
            if not s.startswith("S"):
                raise ImageError(f"(line {i}) SREC missing 'S' -> {s!r}")
            typ = s[1]
            try:
                rawb = bytes.fromhex(s[2:])
            except ValueError:
                raise ImageError(f"(line {i}) SREC non-hex -> {s!r}")
            if len(rawb) < 3:
                raise ImageError(f"(line {i}) SREC too short -> {s!r}")
            count = rawb[0]
            if count != len(rawb) - 1:
                raise ImageError(f"(line {i}) SREC length mismatch -> {s!r}")
            if typ in ("0", "1", "5", "9"): addr_len = 2
            elif typ in ("2", "8"): addr_len = 3
            elif typ in ("3", "7"): addr_len = 4
            else:
                raise ImageError(f"(line {i}) SREC unknown type S{typ} -> {s!r}")
            if len(rawb) < 1 + addr_len + 1:
                raise ImageError(f"(line {i}) SREC too short for address -> {s!r}")
            addr = int.from_bytes(rawb[1:1 + addr_len], "big")
            data = rawb[1 + addr_len:-1]
            if ((sum(rawb) & 0xFF) != 0xFF):
                raise ImageError(f"(line {i}) SREC checksum error -> {s!r}")
            if typ == "0":
                continue
            elif typ in ("1", "2", "3"):
                for j, b in enumerate(data):
                    img.set_byte(addr + j, b)
            elif typ == "5":
                continue
            elif typ in ("7", "8", "9"):
                img.entry.linear = addr
            else:
                raise ImageError(f"(line {i}) SREC unsupported type S{typ}")
        return img

#########################################################################################

    @staticmethod
    def _csum_bytes(bs: bytes) -> int:
        # Compute S-Record checksum byte.
        return (0xFF - (sum(bs) & 0xFF)) & 0xFF

#########################################################################################

    @staticmethod
    def to_lines(img: MemoryImage, *, record_size: int = 16, addr_width: Optional[int] = None, header: str = "ihexsrec") -> List[str]:
        # Emit S-Record lines from a MemoryImage.
        lines: List[str] = []
        hdr_bytes = header.encode("ascii", errors="replace")
        # S0 header (addr width fixed to 2 bytes per spec)
        addr_len = 2
        count = addr_len + len(hdr_bytes) + 1
        rec = bytes([count]) + (0).to_bytes(addr_len, "big") + hdr_bytes
        lines.append("S0" + rec.hex().upper() + f"{SrecCodec._csum_bytes(rec):02X}")

        if len(img) == 0:
            rec = bytes([2 + 1]) + (0).to_bytes(2, "big")
            lines.append("S9" + rec.hex().upper() + f"{SrecCodec._csum_bytes(rec):02X}")
            return lines

        max_addr = img.max_addr or 0
        if addr_width is None:
            addr_width = 2 if max_addr <= 0xFFFF else (3 if max_addr <= 0xFFFFFF else 4)
        if addr_width not in (2, 3, 4):
            raise ValueError("addr_width must be 2,3,4 (bytes)")

        # Validate record_size against SREC count field limit (<=255)
        # count = addr_width + len(data) + 1  => len(data) <= 255 - addr_width - 1
        max_payload = 255 - addr_width - 1
        if record_size <= 0 or record_size > max_payload:
            raise ValueError(f"record_size must be 1..{max_payload} for addr_width={addr_width}")

        data_type = {2: "1", 3: "2", 4: "3"}[addr_width]

        for start, end, data in img.iter_segments():
            pos = start; off = 0
            while off < len(data):
                chunk = data[off: off + record_size]
                addr_bytes = pos.to_bytes(addr_width, "big")
                count = addr_width + len(chunk) + 1
                rec = bytes([count]) + addr_bytes + chunk
                lines.append(f"S{data_type}" + rec.hex().upper() + f"{SrecCodec._csum_bytes(rec):02X}")
                pos += len(chunk); off += len(chunk)

        if img.entry.linear is not None:
            addr = img.entry.linear
            if addr <= 0xFFFF:
                typ = "9"; e_len = 2
            elif addr <= 0xFFFFFF:
                typ = "8"; e_len = 3
            else:
                typ = "7"; e_len = 4
        else:
            typ = "9"; e_len = 2; addr = 0

        rec = bytes([e_len + 1]) + addr.to_bytes(e_len, "big")
        lines.append(f"S{typ}" + rec.hex().upper() + f"{SrecCodec._csum_bytes(rec):02X}")
        return lines

#########################################################################################
#########################################################################################

class IHEXSREC:

#########################################################################################
    
    def __init__(self, image: Optional[MemoryImage] = None) -> None:
        # Provide a simple façade around MemoryImage and codecs.
        self.image = image or MemoryImage()

#########################################################################################

    @staticmethod
    def _sniff_format(first_nonempty_line: str) -> str:
        # Detect file format by the first non-empty line.
        if first_nonempty_line.startswith(":"):
            return "hex"
        if first_nonempty_line.startswith("S"):
            return "srec"
        raise ImageError("Unknown file format (not Intel HEX, not S-Record)")

#########################################################################################

    @classmethod
    def load(cls, lines_or_path: Union[Iterable[str], str], *, guess: Optional[str] = None, encoding: str = "utf-8") -> "IHEXSREC":
        # Load from text lines or a path and return a document.
        if isinstance(lines_or_path, str):
            with open(lines_or_path, "r", encoding=encoding) as f:
                lines = f.read().splitlines()
        else:
            lines = list(lines_or_path)
        first = next((ln.strip() for ln in lines if ln.strip()), "")
        fmt = guess or cls._sniff_format(first)
        if fmt == "hex":
            img = IntelHexCodec.parse_lines(lines)
        elif fmt == "srec":
            img = SrecCodec.parse_lines(lines)
        else:
            raise ImageError("Unsupported input format")
        return cls(img)

#########################################################################################

    def write(self, addr: int, data: Union[bytes, bytearray]) -> "IHEXSREC":
        # Overwrite bytes at address and return self.
        self.image.write_bytes(addr, data)
        return self

#########################################################################################

    def insert(self, addr: int, data: Union[bytes, bytearray], *, shift_entry: bool = False) -> "IHEXSREC":
        # Insert bytes at address (optionally shift entry) and return self.
        self.image.insert_bytes(addr, data, shift_entry=shift_entry)
        return self

#########################################################################################

    def delete(self, addr: int, length: int, *, shift_entry: bool = False) -> "IHEXSREC":
        # Delete a range (optionally shift entry) and return self.
        self.image.delete_bytes(addr, length, shift_entry=shift_entry)
        return self

#########################################################################################

    def set_entry_linear(self, addr: Optional[int]) -> "IHEXSREC":
        # Set or clear the linear entry point.
        self.image.entry.linear = addr
        return self

#########################################################################################

    def set_entry_segmented(self, cs: int, ip: int) -> "IHEXSREC":
        # Set the segmented entry point (CS:IP).
        self.image.entry.segmented = (cs, ip)
        return self

#########################################################################################

    def to_intel_hex(self, *, record_size: int = 16) -> List[str]:
        # Convert to Intel HEX lines.
        return IntelHexCodec.to_lines(self.image, record_size=record_size)

#########################################################################################

    def to_srec(self, *, record_size: int = 16, addr_width: Optional[int] = None, header: str = "ihexsrec") -> List[str]:
        # Convert to Motorola S-Record lines.
        return SrecCodec.to_lines(self.image, record_size=record_size, addr_width=addr_width, header=header)

#########################################################################################

    def save_as_hex(self, path: str, *, record_size: int = 16, encoding: str = "utf-8") -> None:
        # Write Intel HEX to a file.
        with open(path, "w", encoding=encoding) as f:
            for ln in self.to_intel_hex(record_size=record_size):
                f.write(ln + "\n")

#########################################################################################

    def save_as_srec(self, path: str, *, record_size: int = 16, addr_width: Optional[int] = None, header: str = "ihexsrec", encoding: str = "utf-8") -> None:
        # Write S-Record to a file.
        with open(path, "w", encoding=encoding) as f:
            for ln in self.to_srec(record_size=record_size, addr_width=addr_width, header=header):
                f.write(ln + "\n")

#########################################################################################

    def to_bin(self, *, start: int | None = None, end: int | None = None, fill: int = 0xFF) -> bytes:
        # Export a binary slice of the image.
        return self.image.export_bin(start=start, end=end, fill=fill)

#########################################################################################

    def save_as_bin(self, path: str, *, start: int | None = None, end: int | None = None, fill: int = 0xFF) -> None:
        # Write a binary slice to a file.
        data = self.to_bin(start=start, end=end, fill=fill)
        with open(path, "wb") as f:
            f.write(data)

#########################################################################################

    def first_address(self) -> Optional[int]:
        return self.image.first_address()

#########################################################################################

    def last_address(self) -> Optional[int]:
        return self.image.last_address()

#########################################################################################

    def occupied_ranges(self) -> List[Tuple[int, int]]:
        return self.image.occupied_ranges()
        
#########################################################################################

    def gap_ranges(self, *, within: Optional[Tuple[int, int]] = None) -> List[Tuple[int, int]]:
        return self.image.gap_ranges(within=within)

#########################################################################################
   
    def fill_gaps(self, *, fill: int, within: Optional[Tuple[int, int]] = None) -> int:
        # Proxy to MemoryImage.fill_gaps(). Returns number of bytes written.
        return self.image.fill_gaps(fill=fill, within=within)
      
#########################################################################################

    def move(self, *, to: int, start: Optional[int] = None, until: Optional[int] = None, overwrite: bool = True, shift_entry: bool = True) -> int:
        # Move [start, until) to 'to'. If start/until are omitted, move the whole image.
        return self.image.move_window(
            to=to,
            start=start,
            end=until,
            overwrite=overwrite,
            shift_entry=shift_entry,
        )  

#########################################################################################
   
    @classmethod
    def convert(cls, input_lines_or_path: Union[Iterable[str], str], to: str, **kwargs) -> List[str]:
        # Convert from one text format to another.
        to = (to or "").lower()
        if to not in ("hex", "srec"):
            raise ValueError("to must be 'hex' or 'srec'")
        doc = cls.load(input_lines_or_path)
        if to == "hex":
            return doc.to_intel_hex(**{k: v for k, v in kwargs.items() if k in ("record_size",)})
        elif to == "srec":
            return doc.to_srec(**{k: v for k, v in kwargs.items() if k in ("record_size", "addr_width", "header")})
        else:
            raise ValueError("to must be 'hex' or 'srec'")

#########################################################################################
#########################################################################################