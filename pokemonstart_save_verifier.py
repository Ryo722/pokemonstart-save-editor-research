#!/usr/bin/env python3
"""Read-only verifier for the observed PokemonStart/CFRU-JP save layout.

This module never writes to the input path. It recognizes only 128 KiB flash
images, optionally followed by a 16-byte opaque emulator footer, validates
both 14-sector save slots, chooses a unique newest valid slot using the
CFRU-JP counter rule, and decodes the supported 100-byte party records.
"""

from __future__ import annotations

import argparse
import hashlib
import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

FLASH_SIZE = 0x20000
RTC_FOOTER_SIZE = 0x10
SECTOR_SIZE = 0x1000
SLOT_SECTORS = 14
FILE_SIGNATURE = 0x08012025
SECTION_ID_OFFSET = 0xFF4
SECTION_CHECKSUM_OFFSET = 0xFF6
SECTION_SIGNATURE_OFFSET = 0xFF8
SECTION_COUNTER_OFFSET = 0xFFC
PARTY_COUNT_OFFSET = 0x34
PARTY_OFFSET = 0x38
PARTY_SIZE = 6
POKEMON_SIZE = 100

# CFRU-JP main e24a16fe39e27ae162faf5b78596d1f3df18489d, src/save.c.
SECTION_LENGTHS = (
    0xF24,
    0xFF0,
    0xFF0,
    0xFF0,
    0xD98,
    0xFF0,
    0xFF0,
    0xFF0,
    0xFF0,
    0xFF0,
    0xFF0,
    0xFF0,
    0xFF0,
    0x450,
)


class VerificationError(ValueError):
    """Raised when an input must be rejected rather than guessed about."""


@dataclass(frozen=True)
class SectionInfo:
    physical_sector: int
    section_id: int
    checksum_stored: int
    checksum_calculated: int
    signature: int
    counter: int
    data: bytes


@dataclass(frozen=True)
class SlotInfo:
    slot_index: int
    state: str
    counter: int | None
    sections: tuple[SectionInfo, ...]

    def section(self, section_id: int) -> SectionInfo:
        for section in self.sections:
            if section.section_id == section_id:
                return section
        raise VerificationError(
            f"slot {self.slot_index}: missing logical section {section_id}"
        )


@dataclass(frozen=True)
class PartyRecord:
    index: int
    personality: int
    ot_id: int
    nickname_hex: str
    nature_mint: int
    hyper_training: int
    tera_type: int
    language: int
    sanity: int
    ot_name_hex: str
    markings: int
    backup_species: int
    species: int
    held_item: int
    experience: int
    pp_bonuses: int
    friendship: int
    ball: int
    moves: tuple[int, int, int, int]
    pp: tuple[int, int, int, int]
    evs: tuple[int, int, int, int, int, int]
    ivs: tuple[int, int, int, int, int, int]
    condition: int
    level: int
    pokerus_timer: int
    hp: int
    max_hp: int
    attack: int
    defense: int
    speed: int
    sp_attack: int
    sp_defense: int


@dataclass(frozen=True)
class VerificationResult:
    file_size: int
    file_sha256: str
    flash_sha256: str
    footer: bytes
    slots: tuple[SlotInfo, SlotInfo]
    active_slot: int
    party_count: int
    party: tuple[PartyRecord, ...]
    sector30: bytes
    sector31: bytes


def _u16(data: bytes, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def _u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def calculate_save_checksum(data: bytes) -> int:
    """Return the Gen III folded u32-word checksum for a section payload."""
    if len(data) % 4 != 0:
        raise ValueError("checksum payload length must be divisible by 4")
    total = 0
    for offset in range(0, len(data), 4):
        total = (total + _u32(data, offset)) & 0xFFFFFFFF
    return ((total >> 16) + (total & 0xFFFF)) & 0xFFFF


def _is_erased_sector(sector: bytes) -> bool:
    return sector == b"\xFF" * SECTOR_SIZE


def _parse_slot(flash: bytes, slot_index: int) -> SlotInfo:
    start_sector = slot_index * SLOT_SECTORS
    raw_sectors = tuple(
        flash[(start_sector + i) * SECTOR_SIZE : (start_sector + i + 1) * SECTOR_SIZE]
        for i in range(SLOT_SECTORS)
    )
    erased = tuple(_is_erased_sector(sector) for sector in raw_sectors)
    if all(erased):
        return SlotInfo(slot_index, "empty", None, ())
    if any(erased):
        physical = start_sector + erased.index(True)
        raise VerificationError(
            f"slot {slot_index}: partially erased slot (physical sector {physical})"
        )

    parsed: list[SectionInfo] = []
    ids: list[int] = []
    counters: list[int] = []

    for local_index, sector in enumerate(raw_sectors):
        physical = start_sector + local_index
        section_id = _u16(sector, SECTION_ID_OFFSET)
        checksum_stored = _u16(sector, SECTION_CHECKSUM_OFFSET)
        signature = _u32(sector, SECTION_SIGNATURE_OFFSET)
        counter = _u32(sector, SECTION_COUNTER_OFFSET)

        if section_id >= SLOT_SECTORS:
            raise VerificationError(
                f"slot {slot_index}: physical sector {physical} has unsupported section id {section_id}"
            )
        if signature != FILE_SIGNATURE:
            raise VerificationError(
                f"slot {slot_index}: physical sector {physical} section {section_id} "
                f"has invalid signature 0x{signature:08X}"
            )

        checksum_calculated = calculate_save_checksum(
            sector[: SECTION_LENGTHS[section_id]]
        )
        if checksum_stored != checksum_calculated:
            raise VerificationError(
                f"slot {slot_index}: physical sector {physical} section {section_id} "
                f"checksum mismatch stored=0x{checksum_stored:04X} "
                f"calculated=0x{checksum_calculated:04X}"
            )

        ids.append(section_id)
        counters.append(counter)
        parsed.append(
            SectionInfo(
                physical_sector=physical,
                section_id=section_id,
                checksum_stored=checksum_stored,
                checksum_calculated=checksum_calculated,
                signature=signature,
                counter=counter,
                data=sector[:0xFF4],
            )
        )

    if sorted(ids) != list(range(SLOT_SECTORS)):
        duplicates = sorted({section_id for section_id in ids if ids.count(section_id) > 1})
        missing = sorted(set(range(SLOT_SECTORS)) - set(ids))
        raise VerificationError(
            f"slot {slot_index}: section id set is invalid; duplicates={duplicates} missing={missing}"
        )
    if len(set(counters)) != 1:
        unique = ",".join(f"0x{counter:08X}" for counter in sorted(set(counters)))
        raise VerificationError(
            f"slot {slot_index}: inconsistent section counters [{unique}]"
        )

    parsed.sort(key=lambda item: item.section_id)
    return SlotInfo(slot_index, "valid", counters[0], tuple(parsed))


def _as_signed_u32(value: int) -> int:
    return value if value < 0x80000000 else value - 0x100000000


def _choose_active_slot(slot0: SlotInfo, slot1: SlotInfo) -> int:
    if slot0.state == "empty" and slot1.state == "empty":
        raise VerificationError("no valid save slot: both slots are erased")
    if slot0.state == "valid" and slot1.state == "empty":
        return 0
    if slot0.state == "empty" and slot1.state == "valid":
        return 1
    if slot0.state != "valid" or slot1.state != "valid":
        raise VerificationError("unable to choose a valid slot without guessing")

    assert slot0.counter is not None and slot1.counter is not None
    if slot0.counter == slot1.counter:
        raise VerificationError(
            f"ambiguous save slots: equal counters 0x{slot0.counter:08X}"
        )

    # Match CFRU-JP GetSaveValidStatus. It special-cases the u32 wrap from
    # 0xFFFFFFFF to 0, then otherwise compares the counters as signed s32.
    pair = {slot0.counter, slot1.counter}
    if pair == {0xFFFFFFFF, 0x00000000}:
        return 0 if slot0.counter == 0 else 1

    signed0 = _as_signed_u32(slot0.counter)
    signed1 = _as_signed_u32(slot1.counter)
    return 1 if signed0 < signed1 else 0


def _decode_party_record(record: bytes, index: int) -> PartyRecord:
    if len(record) != POKEMON_SIZE:
        raise VerificationError(
            f"party record {index}: expected {POKEMON_SIZE} bytes, got {len(record)}"
        )

    iv_word = _u32(record, 72)
    ivs = tuple((iv_word >> (5 * i)) & 0x1F for i in range(6))
    moves = tuple(_u16(record, 44 + 2 * i) for i in range(4))
    pp = tuple(record[52 + i] for i in range(4))
    evs = tuple(record[56 + i] for i in range(6))

    return PartyRecord(
        index=index,
        personality=_u32(record, 0),
        ot_id=_u32(record, 4),
        nickname_hex=record[8:15].hex().upper(),
        nature_mint=record[15],
        hyper_training=record[16],
        tera_type=record[17],
        language=record[18],
        sanity=record[19],
        ot_name_hex=record[20:27].hex().upper(),
        markings=record[27],
        backup_species=_u16(record, 28),
        species=_u16(record, 32),
        held_item=_u16(record, 34),
        experience=_u32(record, 36),
        pp_bonuses=record[40],
        friendship=record[41],
        ball=record[42],
        moves=moves,  # type: ignore[arg-type]
        pp=pp,  # type: ignore[arg-type]
        evs=evs,  # type: ignore[arg-type]
        ivs=ivs,  # type: ignore[arg-type]
        condition=_u32(record, 80),
        level=record[84],
        pokerus_timer=record[85],
        hp=_u16(record, 86),
        max_hp=_u16(record, 88),
        attack=_u16(record, 90),
        defense=_u16(record, 92),
        speed=_u16(record, 94),
        sp_attack=_u16(record, 96),
        sp_defense=_u16(record, 98),
    )


def verify_bytes(raw: bytes) -> VerificationResult:
    if len(raw) == FLASH_SIZE:
        flash = raw
        footer = b""
    elif len(raw) == FLASH_SIZE + RTC_FOOTER_SIZE:
        flash = raw[:FLASH_SIZE]
        footer = raw[FLASH_SIZE:]
    else:
        raise VerificationError(
            f"unsupported file size {len(raw)} bytes; expected {FLASH_SIZE} or "
            f"{FLASH_SIZE + RTC_FOOTER_SIZE}"
        )

    slot0 = _parse_slot(flash, 0)
    slot1 = _parse_slot(flash, 1)
    active_slot = _choose_active_slot(slot0, slot1)
    selected = (slot0, slot1)[active_slot]

    saveblock1 = selected.section(1).data
    party_count = saveblock1[PARTY_COUNT_OFFSET]
    if party_count > PARTY_SIZE:
        raise VerificationError(
            f"active slot {active_slot}: unsupported party count {party_count}; maximum is {PARTY_SIZE}"
        )

    party = tuple(
        _decode_party_record(
            saveblock1[
                PARTY_OFFSET + i * POKEMON_SIZE : PARTY_OFFSET + (i + 1) * POKEMON_SIZE
            ],
            i,
        )
        for i in range(party_count)
    )

    sector30 = flash[30 * SECTOR_SIZE : 31 * SECTOR_SIZE]
    sector31 = flash[31 * SECTOR_SIZE : 32 * SECTOR_SIZE]

    return VerificationResult(
        file_size=len(raw),
        file_sha256=hashlib.sha256(raw).hexdigest(),
        flash_sha256=hashlib.sha256(flash).hexdigest(),
        footer=footer,
        slots=(slot0, slot1),
        active_slot=active_slot,
        party_count=party_count,
        party=party,
        sector30=sector30,
        sector31=sector31,
    )


def verify_file(path: str | Path) -> VerificationResult:
    # read_bytes opens the path read-only; this verifier exposes no write path.
    return verify_bytes(Path(path).read_bytes())


def _sector_summary(label: str, data: bytes) -> str:
    return (
        f"{label}: sha256={hashlib.sha256(data).hexdigest()} "
        f"nonzero={sum(byte != 0 for byte in data)} "
        f"non_ff={sum(byte != 0xFF for byte in data)}"
    )


def _csv(values: Iterable[int]) -> str:
    return ",".join(str(value) for value in values)


def format_report(result: VerificationResult) -> str:
    lines = [
        "status: ACCEPTED",
        f"file_size: {result.file_size}",
        f"file_sha256: {result.file_sha256}",
        f"flash_size: {FLASH_SIZE}",
        f"flash_sha256: {result.flash_sha256}",
    ]

    if result.footer:
        lines.extend(
            [
                "emulator_footer: present-16-byte-opaque",
                f"emulator_footer_hex: {result.footer.hex().upper()}",
                f"emulator_footer_sha256: {hashlib.sha256(result.footer).hexdigest()}",
            ]
        )
    else:
        lines.append("emulator_footer: absent")

    for slot in result.slots:
        if slot.state == "empty":
            lines.append(f"slot{slot.slot_index}: empty")
            continue
        assert slot.counter is not None
        lines.append(f"slot{slot.slot_index}: valid counter=0x{slot.counter:08X}")
        for section in slot.sections:
            lines.append(
                f"slot{slot.slot_index}.section{section.section_id}: "
                f"physical={section.physical_sector} signature=0x{section.signature:08X} "
                f"checksum=0x{section.checksum_stored:04X} length=0x{SECTION_LENGTHS[section.section_id]:X}"
            )

    lines.extend(
        [
            f"active_slot: {result.active_slot}",
            f"party_count: {result.party_count}",
        ]
    )

    for mon in result.party:
        prefix = f"party[{mon.index}]"
        lines.extend(
            [
                f"{prefix}: species={mon.species} backup_species={mon.backup_species} level={mon.level} "
                f"exp={mon.experience} friendship={mon.friendship} ball={mon.ball} held_item={mon.held_item}",
                f"{prefix}.nickname_hex: {mon.nickname_hex}",
                f"{prefix}.ot_name_hex: {mon.ot_name_hex}",
                f"{prefix}.personality: 0x{mon.personality:08X}",
                f"{prefix}.ot_id: 0x{mon.ot_id:08X}",
                f"{prefix}.extended: nature_mint={mon.nature_mint} hyper_training=0x{mon.hyper_training:02X} "
                f"tera_type={mon.tera_type} language={mon.language} sanity=0x{mon.sanity:02X} markings=0x{mon.markings:02X}",
                f"{prefix}.pp_bonuses: 0x{mon.pp_bonuses:02X}",
                f"{prefix}.moves: {_csv(mon.moves)}",
                f"{prefix}.pp: {_csv(mon.pp)}",
                f"{prefix}.evs_hp_atk_def_spe_spa_spd: {_csv(mon.evs)}",
                f"{prefix}.ivs_hp_atk_def_spe_spa_spd: {_csv(mon.ivs)}",
                f"{prefix}.battle: condition=0x{mon.condition:08X} pokerus_timer={mon.pokerus_timer} "
                f"hp={mon.hp}/{mon.max_hp} atk={mon.attack} def={mon.defense} "
                f"spe={mon.speed} spa={mon.sp_attack} spd={mon.sp_defense}",
            ]
        )

    lines.append(_sector_summary("sector30", result.sector30))
    lines.append(_sector_summary("sector31", result.sector31))
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Read-only verifier for the supported PokemonStart/CFRU-JP save layout."
    )
    parser.add_argument("save", help="path to a 0x20000 or 0x20010-byte save")
    args = parser.parse_args(argv)

    try:
        result = verify_file(args.save)
    except (OSError, VerificationError) as exc:
        print("status: REJECTED")
        print(f"reason: {exc}")
        return 2

    print(format_report(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
