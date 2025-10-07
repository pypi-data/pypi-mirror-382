#
#   Copyright (c) 2014-2021, 2025 eGauge Systems LLC
# 	4805 Sterling Dr, Suite 1
# 	Boulder, CO 80301
# 	voice: 720-545-9767
# 	email: davidm@egauge.net
#
#   All rights reserved.
#
#   This code is the property of eGauge Systems LLC and may not be
#   copied, modified, or disclosed without any prior and written
#   permission from eGauge Systems LLC.
#
import logging
import os
import tempfile
from pathlib import Path

import sexpdata

from epic.base import Enum, format_part_number

from .error import Error
from .parts_cache import PartsCache

KICAD_FOOTPRINT = sexpdata.Symbol("footprint")
KICAD_PATH = sexpdata.Symbol("path")
KICAD_PROP = sexpdata.Symbol("property")
KICAD_PROP_EP = "EP"  # eGauge part number
KICAD_PROP_FOOTPRINT = "Footprint"
KICAD_PROP_REFDES = "Reference"
KICAD_PROP_SHEET_FILE = "Sheetfile"
KICAD_SHEET = sexpdata.Symbol("sheet")
KICAD_SYMBOL = sexpdata.Symbol("symbol")
KICAD_SYMBOL_INSTANCES = sexpdata.Symbol("symbol_instances")
KICAD_SYMBOL_ON_BOARD = sexpdata.Symbol("on_board")
KICAD_SYMBOL_YES = sexpdata.Symbol("yes")
KICAD_UUID = sexpdata.Symbol("uuid")

log = logging.getLogger(__name__)


def _prefetch_symbol(symbol):
    for sexp in symbol:
        if not isinstance(sexp, list):
            continue
        if sexp[0] == KICAD_PROP:
            if sexp[1] == KICAD_PROP_EP:
                try:
                    part_number = int(sexp[2])
                except ValueError:
                    log.warning('Invalid EPIC part number "%s".', sexp[2])
                else:
                    PartsCache.prefetch(part_number)


def _update_symbol(symbol, updated_syms):
    """Check the footprint of a schematic symbol and update it if
    necessary.  SYMBOL is the s-expression of the symbol to update.
    UPDATED_SYMS is a dictionary of all symbol UUIDs whose footprints
    have been updated.  The value of each entry is the new footprint
    for that symbol.  Returns True if the symbol was updated, False
    otherwise.

    """
    has_changed = False
    part_number = footprint_sexp = None
    refdes = ""
    on_board = True  # is the symbol on the PCB (board)?
    uuid = None
    for sexp in symbol:
        if not isinstance(sexp, list):
            continue
        if sexp[0] == KICAD_UUID:
            uuid = sexp[1]
        elif sexp[0] == KICAD_PROP:
            prop_name = sexp[1]
            if prop_name == KICAD_PROP_EP:
                try:
                    part_number = int(sexp[2])
                except ValueError:
                    log.warning('Invalid EPIC part number "%s".', sexp[2])
            elif prop_name == KICAD_PROP_FOOTPRINT:
                footprint_sexp = sexp
            elif prop_name == KICAD_PROP_REFDES:
                refdes = sexp[2] + " "
        elif sexp[0] == KICAD_SYMBOL_ON_BOARD:
            on_board = sexp[1] == KICAD_SYMBOL_YES

    if uuid is None:
        log.warning("Ignoring symbol without UUID: %s", str(symbol))
        return False

    if part_number is not None:
        try:
            part = PartsCache.get(part_number)
        except Error:
            log.warning(
                "Part %s does not exist.", format_part_number(part_number)
            )
            return False
        footprint = part.footprint
        if not footprint:
            footprint = ""
            if on_board and part.mounting not in [
                Enum.MOUNTING_CHASSIS,
                Enum.MOUNTING_FREE,
            ]:
                log.warning(
                    "Part %s has no footprint defined.",
                    format_part_number(part_number),
                )
            return False

        if footprint_sexp is None:
            log.warning("Footprint property missing in symbol.")
            return False

        old_footprint = footprint_sexp[2]
        if old_footprint != footprint:
            footprint_sexp[2] = footprint
            if not old_footprint:
                log.info("%sfootprint set to %s.", refdes, footprint)
            else:
                log.warning(
                    "%sfootprint changed from %s to %s.",
                    refdes,
                    old_footprint,
                    footprint,
                )
            updated_syms[uuid] = footprint
            has_changed = True
    return has_changed


def _update_symbol_instance(symbol, new_footprint):
    """Update a symbol instance whose footprint has changed.  SYMBOL is
    the s-expression of the symbol to update.  NEW_FOOTPRINT is the
    name of footprint to set for the symbol.

    """
    for sexp in symbol:
        if not isinstance(sexp, list):
            continue
        if sexp[0] == KICAD_FOOTPRINT:
            sexp[1] = new_footprint
            return
    symbol.append([KICAD_FOOTPRINT, new_footprint])


def _update_sheet(dirname, symbol, updated_syms):
    for sexp in symbol:
        if not isinstance(sexp, list):
            continue
        if sexp[0] == KICAD_PROP and sexp[1] == KICAD_PROP_SHEET_FILE:
            sheet_path = dirname / sexp[2]
            _update_schematic(sheet_path, updated_syms)


def _update_sheets_and_footprints(dirname, schematic, updated_syms):
    """Update the schematic symbol footprints in a schematic in modern
    format (post KiCad v5) as needed. PATH is the filename path of the
    schematic, OUT is a temporary output file to write the updated
    schematic file to.  UPDATED_SYMS is a dictionary of all symbol
    UUIDs whose footprints have been updated.  The value of each entry
    is the new footprint for that symbol.  Returns True if the
    schematic file changed, False otherwise.

    """
    # prefetch all EPIC parts:
    for sexp in schematic:
        if not isinstance(sexp, list):
            continue
        if sexp[0] == KICAD_SYMBOL:
            _prefetch_symbol(sexp)

    changed = False
    for sexp in schematic:
        if not isinstance(sexp, list):
            continue
        if sexp[0] == KICAD_SHEET:
            _update_sheet(dirname, sexp, updated_syms)
        elif sexp[0] == KICAD_SYMBOL:
            changed |= _update_symbol(sexp, updated_syms)
    return changed


def _update_symbol_instances(symbol, updated_syms):
    """Check SYMBOL's UUID is in UPDATED_SYMS and, if so, update its
    footprint with the name given as the value of the entry in
    UPDATED_SYMS.  Returns True if the symbol was updated, False
    otherwise.

    """
    changed = False
    for sexp in symbol:
        if not isinstance(sexp, list):
            continue
        if sexp[0] == KICAD_PATH:
            path = sexp[1].split("/")
            sym_path = path[-1]
            if sym_path in updated_syms:
                _update_symbol_instance(sexp, updated_syms[sym_path])
                changed = True
    return changed


def _update_sym_list(schematic, updated_syms):
    """Update the footprints in the symbol-instances list of the top-level
    schematic of a KiCad v6 or newer schematic file.  DIRNAME is the
    directory containing the schematic and FILENAME is the filename
    within that directory.  HAS_BACKUP is True if the schematic file
    already has been backed up (due to an earlier change).
    UPDATED_SYMS is a dictionary of all symbol UUIDs whose footprints
    have been updated.  The value of each entry is the new footprint
    for that symbol.

    """
    changed = False
    for sexp in schematic:
        if isinstance(sexp, list) and sexp[0] == KICAD_SYMBOL_INSTANCES:
            if _update_symbol_instances(sexp, updated_syms):
                changed = True
    return changed


def _update_schematic(path, updated_syms):
    """Update schematic FILENAME with footprints from the EPIC database.
    UPDATED_SYMS is a dictionary into which are entered the UUIDs of
    all the symbols whose footprints have been updated.  The value of
    each entry is the new footprint for that symbol.  Returns True if
    the FILENAME was updated (and hence a backup file was created),
    False otherwise.

    """
    dirname = path.parent
    with (
        tempfile.NamedTemporaryFile(
            dir=dirname, mode="w", encoding="utf-8"
        ) as out,
        open(path, encoding="utf-8") as schem_file,
    ):
        schematic = sexpdata.load(schem_file)
        has_changes = _update_sheets_and_footprints(
            dirname, schematic, updated_syms
        )
        has_changes |= _update_sym_list(schematic, updated_syms)
        if has_changes:
            sexpdata.dump(schematic, out)
            os.rename(path, path.with_name(path.name + "~"))
            os.link(out.name, path)
            log.info("%s updated.", path)
    return has_changes


def update_footprints(epic_api, filename):
    """Update KiCad schematic FILENAME with the footprints from the EPIC
    database.  Any sheets within the schematic are also updated.  The
    original schematic files are backed up with a filename that has
    tilde appended.

    This program should not be called while KiCad has the schematic
    file open as KiCad may otherwise overwrite the changes made here.

    FILENAME may be a string or a pathlib.Path object.

    """
    path = Path(filename)
    if path.suffix == "":
        path = path.with_suffix(".kicad_sch")

    PartsCache.set_epic(epic_api)

    updated_syms = {}
    _update_schematic(path, updated_syms)
