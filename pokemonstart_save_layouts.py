#!/usr/bin/env python3
"""Read-only save-layout families for PokemonStart saves. No write path.

Two structural families are recognised:

* ``legacy_v022_14_section`` -- delegated unchanged to the canonical
  ``pokemonstart_save_verifier`` (exact-v0.22 behaviour is not reinterpreted).
* ``v023plus_shel_pages`` -- 2 x 5-section slots plus 17 Box pages addressed
  through the SaveBlock1 ``SHEL`` page-sector table.

A family describes structure only. Recognising a family never implies that a
build is qualified for writing, or even for semantic reads; that binding lives
in ``pokemonstart_read_profiles``. Every malformed, ambiguous or unqualified
state raises ``LayoutError`` instead of being guessed about or repaired.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import struct

import pokemonstart_save_verifier as verifier

LEGACY = "legacy_v022_14_section"
V023PLUS = "v023plus_shel_pages"

SECTOR = verifier.SECTOR_SIZE
PAGE_DATA = 0xFF0
SLOT_SECTIONS = 5
SHEL_MAGIC = 0x4C454853  # "SHEL"
SHEL_SB1_OFFSET = 0x1400
# SaveBlock1 +0x1400 lies in logical section 2 at 0x1400 - 0xFF0.
SHEL_SECTION_OFFSET = SHEL_SB1_OFFSET - 0xFF0
PAGE_COUNT = 17
PAGE_FIRST_ID = 0x40
PAGE_SECTOR_MIN = 2 * SLOT_SECTIONS
PAGE_SECTOR_MAX = 31
MAX_UNWRAPPED_COUNTER = 0x7FFFFFFE

# RAM fragments serialised outside SaveBlock1/2 (Inventory and related state).
# (RAM start, length, legacy source, v0.23+ source); a source is
# (kind, ident, offset) with kind in {"section", "sector", "page"}.
FRAGMENTS = (
    (0x0203B0E8, 0xCC, ("section", 0, 0xF24), ("section", 0, 0xF24)),
    (0x0203B1B4, 0x258, ("section", 4, 0xD98), ("section", 4, 0xD98)),
    (0x0203B40C, 0xBA0, ("section", 13, 0x450), ("page", 0, 0x18B)),
    (0x0203BFAC, 0xFF0, ("sector", 30, 0), ("page", 15, 0)),
    (0x0203CF9C, 0xFF0, ("sector", 31, 0), ("page", 16, 0)),
)


class LayoutError(ValueError):
    """Raised when an input must be rejected rather than guessed about."""


@dataclass(frozen=True)
class PageInfo:
    page_index: int
    page_id: int
    physical_sector: int
    counter: int
    checksum: int
    data: bytes


@dataclass(frozen=True)
class Fragment:
    ram_start: int
    length: int
    source: str
    # checksum_covered: inside the range a stored section/page checksum covers.
    # epoch_bound: stored in a sector that belongs to the selected save epoch
    # (active slot section, or a page referenced by the active SHEL table).
    # Section tails past SECTION_LENGTHS are epoch-bound but NOT checksum-covered.
    checksum_covered: bool
    epoch_bound: bool
    data: bytes


@dataclass(frozen=True)
class SaveView:
    """Structural, read-only view of the active save epoch."""

    layout: str
    file_size: int
    file_sha256: str
    footer: bytes
    slots: tuple[verifier.SlotInfo, verifier.SlotInfo]
    active_slot: int
    counter: int
    rotations: tuple[int | None, int | None]
    shel_counter: int | None
    page_table: tuple[int, ...] | None
    inactive_page_table: tuple[int, ...] | None
    pages: tuple[PageInfo, ...]
    fragments: tuple[Fragment, ...]
    legacy_result: verifier.VerificationResult | None = None

    @property
    def active(self) -> verifier.SlotInfo:
        return self.slots[self.active_slot]

    def section(self, section_id: int) -> bytes:
        return self.active.section(section_id).data

    def ram(self, address: int, length: int) -> bytes:
        for fragment in self.fragments:
            if fragment.ram_start <= address and address + length <= fragment.ram_start + fragment.length:
                offset = address - fragment.ram_start
                return fragment.data[offset:offset + length]
        raise LayoutError(f"RAM range 0x{address:08X}+{length} is not serialised in one fragment")

    @property
    def party_count(self) -> int:
        count = self.section(1)[verifier.PARTY_COUNT_OFFSET]
        if count > verifier.PARTY_SIZE:
            raise LayoutError(f"unsupported party count {count}")
        return count

    def party(self) -> tuple[verifier.PartyRecord, ...]:
        sb1 = self.section(1)
        size = verifier.POKEMON_SIZE
        return tuple(
            verifier._decode_party_record(
                sb1[verifier.PARTY_OFFSET + i * size:verifier.PARTY_OFFSET + (i + 1) * size], i)
            for i in range(self.party_count))

    def money(self) -> tuple[int, int]:
        """Return (key, decoded money): SB1+0x290 XOR SB2+0xF20."""
        key = _u32(self.section(0), 0xF20)
        return key, _u32(self.section(1), 0x290) ^ key


def _u16(data: bytes, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def _u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def split_file(raw: bytes) -> tuple[bytes, bytes]:
    if len(raw) == verifier.FLASH_SIZE:
        return raw, b""
    if len(raw) == verifier.FLASH_SIZE + verifier.RTC_FOOTER_SIZE:
        return raw[:verifier.FLASH_SIZE], raw[verifier.FLASH_SIZE:]
    raise LayoutError(f"unsupported file size {len(raw)} bytes")


def _sector(flash: bytes, number: int) -> bytes:
    return flash[number * SECTOR:(number + 1) * SECTOR]


def _parse_v023_slot(flash: bytes, slot_index: int) -> tuple[verifier.SlotInfo, int | None]:
    first = slot_index * SLOT_SECTIONS
    raw = [_sector(flash, first + i) for i in range(SLOT_SECTIONS)]
    erased = [s == b"\xFF" * SECTOR for s in raw]
    if all(erased):
        return verifier.SlotInfo(slot_index, "empty", None, ()), None
    if any(erased):
        raise LayoutError(f"slot {slot_index}: partially erased slot")
    sections, rotation = [], None
    for local, sector in enumerate(raw):
        physical = first + local
        section_id = _u16(sector, verifier.SECTION_ID_OFFSET)
        stored = _u16(sector, verifier.SECTION_CHECKSUM_OFFSET)
        signature = _u32(sector, verifier.SECTION_SIGNATURE_OFFSET)
        if section_id >= SLOT_SECTIONS:
            raise LayoutError(f"slot {slot_index}: sector {physical} has unsupported section id {section_id}")
        if signature != verifier.FILE_SIGNATURE:
            raise LayoutError(f"slot {slot_index}: sector {physical} has invalid signature")
        calculated = verifier.calculate_save_checksum(sector[:verifier.SECTION_LENGTHS[section_id]])
        if stored != calculated:
            raise LayoutError(f"slot {slot_index}: sector {physical} section {section_id} checksum mismatch")
        this_rotation = (local - section_id) % SLOT_SECTIONS
        if rotation is None:
            rotation = this_rotation
        elif rotation != this_rotation:
            raise LayoutError(f"slot {slot_index}: section placement is not a cyclic rotation "
                               "(duplicate, missing or permuted logical sections)")
        sections.append(verifier.SectionInfo(physical, section_id, stored, calculated, signature,
                                             _u32(sector, verifier.SECTION_COUNTER_OFFSET), sector[:0xFF4]))
    ids = [s.section_id for s in sections]
    if sorted(ids) != list(range(SLOT_SECTIONS)):
        raise LayoutError(f"slot {slot_index}: duplicate or missing logical sections")
    counters = {s.counter for s in sections}
    if len(counters) != 1:
        raise LayoutError(f"slot {slot_index}: mixed section counters")
    sections.sort(key=lambda s: s.section_id)
    slot = verifier.SlotInfo(slot_index, "valid", counters.pop(), tuple(sections))
    if _u32(slot.section(2).data, SHEL_SECTION_OFFSET) != SHEL_MAGIC:
        raise LayoutError(f"slot {slot_index}: 5-section slot without SHEL magic")
    return slot, rotation


def _shel(slot: verifier.SlotInfo) -> tuple[int, tuple[int, ...]]:
    section2 = slot.section(2).data
    counter = _u32(section2, SHEL_SECTION_OFFSET + 4)
    table = tuple(section2[SHEL_SECTION_OFFSET + 8:SHEL_SECTION_OFFSET + 8 + PAGE_COUNT])
    if counter != slot.counter:
        raise LayoutError(f"slot {slot.slot_index}: SHEL counter differs from slot counter")
    if any(not PAGE_SECTOR_MIN <= n <= PAGE_SECTOR_MAX for n in table):
        raise LayoutError(f"slot {slot.slot_index}: page-sector index out of range")
    if len(set(table)) != PAGE_COUNT:
        raise LayoutError(f"slot {slot.slot_index}: duplicate page-sector mapping")
    return counter, table


def _pages(flash: bytes, slot: verifier.SlotInfo, table: tuple[int, ...]) -> tuple[PageInfo, ...]:
    pages = []
    for index, number in enumerate(table):
        sector = _sector(flash, number)
        page_id = _u16(sector, verifier.SECTION_ID_OFFSET)
        if sector == b"\xFF" * SECTOR:
            raise LayoutError(f"slot {slot.slot_index}: page {index} missing (sector {number} erased)")
        if _u32(sector, verifier.SECTION_SIGNATURE_OFFSET) != verifier.FILE_SIGNATURE:
            raise LayoutError(f"slot {slot.slot_index}: page {index} has invalid signature")
        if page_id != PAGE_FIRST_ID + index:
            raise LayoutError(f"slot {slot.slot_index}: page {index} has wrong page id 0x{page_id:02X}")
        stored = _u16(sector, verifier.SECTION_CHECKSUM_OFFSET)
        if stored != verifier.calculate_save_checksum(sector[:PAGE_DATA]):
            raise LayoutError(f"slot {slot.slot_index}: page {index} checksum mismatch")
        counter = _u32(sector, verifier.SECTION_COUNTER_OFFSET)
        # A page counter records the save that last wrote the page; after
        # copy-on-write it may legitimately be older than the slot counter.
        # A page newer than the slot that references it has no owner.
        if counter > slot.counter:
            raise LayoutError(f"slot {slot.slot_index}: page {index} is newer than its slot")
        pages.append(PageInfo(index, page_id, number, counter, stored, sector[:PAGE_DATA]))
    return tuple(pages)


def parse_v023plus(raw: bytes) -> SaveView:
    flash, footer = split_file(raw)
    parsed = [_parse_v023_slot(flash, k) for k in (0, 1)]
    slots = (parsed[0][0], parsed[1][0])
    try:
        active_index = verifier._choose_active_slot(*slots)
    except verifier.VerificationError as exc:
        raise LayoutError(str(exc)) from exc
    active = slots[active_index]
    for slot in slots:
        if slot.state == "valid" and not 0 <= slot.counter <= MAX_UNWRAPPED_COUNTER:
            raise LayoutError("counter wrap is unqualified for page epochs")
    tables, pages = {}, {}
    for slot in slots:
        if slot.state == "valid":
            _, tables[slot.slot_index] = _shel(slot)
            pages[slot.slot_index] = _pages(flash, slot, tables[slot.slot_index])
    inactive_index = 1 - active_index
    if inactive_index in tables:
        owner = {n: p for p, n in enumerate(tables[active_index])}
        # Per-slot page validation already rejects a sector whose page id does
        # not match; this cross-check is kept as defence in depth.
        for page, number in enumerate(tables[inactive_index]):
            if number in owner and owner[number] != page:
                raise LayoutError("page sector shared by different pages across slots (ambiguous ownership)")
    page_data = {p.page_index: p.data for p in pages[active_index]}
    fragments = []
    for start, length, _, (kind, ident, offset) in FRAGMENTS:
        if kind == "section":
            data = active.section(ident).data[offset:offset + length]
            source = f"section {ident} +0x{offset:X}"
            covered = offset + length <= verifier.SECTION_LENGTHS[ident]
        else:
            data = page_data[ident][offset:offset + length]
            source = f"page {ident} +0x{offset:X}"
            covered = offset + length <= PAGE_DATA
        if len(data) != length:
            raise LayoutError("fragment truncated")
        fragments.append(Fragment(start, length, source, covered, True, data))
    return SaveView(V023PLUS, len(raw), hashlib.sha256(raw).hexdigest(), footer, slots, active_index,
                    active.counter, (parsed[0][1], parsed[1][1]), active.counter,
                    tables[active_index], tables.get(inactive_index), pages[active_index], tuple(fragments))


def parse_legacy(raw: bytes) -> SaveView:
    try:
        result = verifier.verify_bytes(raw)
    except verifier.VerificationError as exc:
        raise LayoutError(str(exc)) from exc
    flash, _ = split_file(raw)
    active = result.slots[result.active_slot]
    fragments = []
    for start, length, (kind, ident, offset), _ in FRAGMENTS:
        if kind == "section":
            data = active.section(ident).data[offset:offset + length]
            covered = offset + length <= verifier.SECTION_LENGTHS[ident]
            fragments.append(Fragment(start, length, f"section {ident} +0x{offset:X}", covered, True, data))
        else:
            # Legacy extra sectors are global, unsigned and not epoch-bound.
            data = _sector(flash, ident)[offset:offset + length]
            fragments.append(Fragment(start, length, f"sector {ident} +0x{offset:X}", False, False, data))
    return SaveView(LEGACY, result.file_size, result.file_sha256, result.footer, result.slots,
                    result.active_slot, active.counter, (None, None), None, None, None, (),
                    tuple(fragments), result)


PARSERS = {LEGACY: parse_legacy, V023PLUS: parse_v023plus}


def detect(raw: bytes) -> SaveView:
    """Return the unique family that parses ``raw``; otherwise fail closed."""
    split_file(raw)
    accepted, reasons = [], {}
    for name, parser in PARSERS.items():
        try:
            accepted.append(parser(raw))
        except LayoutError as exc:
            reasons[name] = str(exc)
    if len(accepted) == 1:
        return accepted[0]
    if accepted:
        raise LayoutError("ambiguous layout: more than one family parses")
    raise LayoutError("unknown layout: " + "; ".join(f"{k}: {v}" for k, v in reasons.items()))
