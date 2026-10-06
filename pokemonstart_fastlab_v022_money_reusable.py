"""Preregistered key0/two-valid-slot/fixed-target Money qualification candidate."""
from __future__ import annotations

import struct

import pokemonstart_money_reusable_audit as independent
import pokemonstart_save_verifier as verifier


def qualify(raw: bytes) -> dict:
    parsed = independent.parse(raw)
    verified = verifier.verify_bytes(raw)
    if parsed['active_slot'] != verified.active_slot:
        raise ValueError('independent/verifier active selection mismatch')
    if parsed['slots'][parsed['active_slot']]['money'] == independent.TARGET:
        raise ValueError('noop rejected: Money already equals fixed target')
    return parsed


def derive(raw: bytes, request: dict) -> tuple[bytes, dict]:
    if (not isinstance(request, dict) or set(request) != {'money'}
            or type(request['money']) is not int or request['money'] != independent.TARGET):
        raise ValueError('Money request must be exactly integer money=7654321')
    parsed = qualify(raw)
    base = parsed['slots'][parsed['active_slot']]['sections'][1]
    output = bytearray(raw)
    struct.pack_into('<I', output, base + 0x290, independent.TARGET)
    struct.pack_into('<H', output, base + verifier.SECTION_CHECKSUM_OFFSET,
                     verifier.calculate_save_checksum(bytes(output[base:base + verifier.SECTION_LENGTHS[1]])))
    candidate = bytes(output)
    receipt = independent.audit(raw, candidate)
    verifier.verify_bytes(candidate)
    return candidate, receipt
