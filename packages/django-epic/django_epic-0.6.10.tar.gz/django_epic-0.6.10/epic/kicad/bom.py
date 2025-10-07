#
#   Copyright (c) 2014-2022, 2025 eGauge Systems LLC
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
"""This module handles parsing of KiCAD BOM files (XML files) and
translating them to an EPIC assembly and/or CSV output file.

"""

import logging
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

from egauge import webapi

from epic.base import Enum, format_part_number, strchoice

from .epic_client import EPICAPIClient
from .error import Error, UnknownFlavorsError
from .parts_cache import PartsCache
from .vendors_cache import VendorsCache

EP_PAT = re.compile(r"EP(-(.*))?")
INST_PAT = re.compile(r"Installation(-(.*))?")
VALUE_PAT = re.compile(r"Value(-(.*))?")

log = logging.getLogger(__name__)


def _update(res, field, desired_flavors, detected_flavors: set[str]):
    """Process object RES by matching FIELD.attrib['name'] against
    RES.pattern.  If there is a match M, M.group(2) must evaluate to
    the name of the flavor of the field.  If this flavor matches the
    specified flavor, we have an exact match and RES.value is set to
    field.text, RES.name is set to field.attrib['name'].  If the
    flavor of the field is empty and RES.value is None we have a
    default match and RES is updated like for an exact match.
    DETECTED_FLAVOR is a set of flavors found.

    """
    m = res.pattern.match(field.attrib["name"])
    if m is None:
        return

    this_flavor = None
    if m.lastindex is not None:
        this_flavor = m.group(2)
        detected_flavors |= {this_flavor}  # update set of all detected flavors

    if this_flavor in desired_flavors or (
        this_flavor is None and res.value is None
    ):
        res.name = field.attrib["name"]
        res.value = field.text


class Component:
    # dictionary of components that first referenced a particular best part:
    first_reference = {}

    def __init__(self, part_id, refdes, value, footprint):
        self.part_id = part_id
        self.part = None
        self.refdes = refdes
        self.value = value
        self.footprint = footprint
        self.mfg = None
        self.mfg_pn = None
        PartsCache.prefetch(part_id)

    def load_from_epic(self):
        self.part = PartsCache.get(self.part_id)

        if self.value != self.part.val:
            log.warning(
                '%s has value "%s" but part %s has value "%s"',
                self.refdes,
                self.value,
                self,
                self.part.val,
            )

        if self.footprint != self.part.footprint:
            if self.footprint:
                msg = "changed from %s" % self.footprint
            else:
                msg = "set"
            if self.part.footprint:
                log.warning(
                    "%s footprint should be %s to %s."
                    % (self.refdes, msg, self.part.footprint)
                )
            else:
                log.warning(
                    "%s footprint %s should be removed."
                    % (self.refdes, self.footprint)
                )

        best_part = self.part.best_part
        first_ref = self.__class__.first_reference.get(best_part)
        if first_ref is None:
            self.__class__.first_reference[best_part] = self
        else:
            if self.part_id != first_ref.part_id:
                log.warning(
                    "%s uses %s instead of equivalent %s used by %s",
                    self.refdes,
                    self,
                    first_ref,
                    first_ref.refdes,
                )

        self.mfg = self.part.mfg
        self.mfg_pn = self.part.mfg_pn

    def __str__(self):
        return format_part_number(self.part_id)


def _bom_append(bom: dict[int, list[Component]], component: Component):
    if component.part_id not in bom:
        bom[component.part_id] = []
    bom[component.part_id].append(component)


class BOM:
    """A BOM object is a bill-of-material for a given PCB."""

    def __init__(
        self,
        epic_api: EPICAPIClient,
        xml_filename: Path,
        manufacturer: str,
        flavors: set[str] | None = None,
        toolname="kicad-to-epic-bom",
    ):
        """Create a BOM object that represents the KiCad intermediate XML
        netlist stored in file XML_FILENAME.

        EPIC_API must be an instance of EPICAPIClient which provides
        access to the EPIC JSON API.

        MANUFACTURER is the name to use as the creator of the board.
        This is typically a short version of the company that designed
        the board.  For example, "eGauge" might be used by "eGauge
        Systems LLC".

        A single Eeschema schematic may define multiple flavors
        (versions) of a PCB.  Each flavor results in its own BOM.  The
        flavors to be used is selected with argument FLAVORS.  If this
        argument is not set, the default ("unflavored") BOM is
        generated.

        The part number and the installation of that part is
        determined based on various fields of the schematic component.
        Specifically, the following fields are used:

        Field Name:	Purpose:
        ------------	---------------------------------------------
        EP[-FLAVOR]	Specifies the EPIC part number to use for the
                        component.  If -FLAVOR is specified, the field
                        specifies the part number to use only for that
                        FLAVOR.

        Installation[-FLAVOR]
                        If the value of this field is "DNP" (Do Not Place),
                        then the component is omitted from the BOM.
                        If it is "P" (Place), then the component is included
                        in the BOM.
                        In the CSV output file, do-not-place components
                        are listed separately at the end of the file.
                        If -FLAVOR is specified, the field specifies the
                        installation-type of the component only for that
                        FLAVOR.

        Flavored field-names take precedence over unflavored fields.
        For example, if a component specified the fields:

                EP	123
                EP-lite	42

        then part number 42 would be used for flavor "lite" but 123
        would be used in all other cases.

        """
        self.manufacturer = manufacturer
        self.toolname = toolname
        self.schematic_name = "unknown"
        self._rev: str | None = None
        self.sources = []
        # dictionary of components in the BOM:
        self.comps: dict[int, list[Component]] = {}
        # dictionary of do-not-place components:
        self.dnps: dict[int, list[Component]] = {}
        self.epic_api = epic_api
        self._detected_flavors: set[str] = set()
        PartsCache.set_epic(epic_api)
        VendorsCache.set_epic(epic_api)

        if flavors is None:
            flavors = set()
        self._selected_flavors = flavors

        try:
            xml = ET.parse(xml_filename)
        except ET.ParseError as _:
            raise Error("Input file is not a valid XML file.", xml_filename)

        design = xml.find("design")
        if design is not None:
            source = design.findtext("source")
            if source is not None:
                path = Path(source)
                self.schematic_name = path.with_suffix("").name
            sheet = design.find("sheet")
            for sheet in design.iter("sheet"):
                title_block = sheet.find("title_block")
                if title_block is not None:
                    if self._rev is None:
                        rev = title_block.findtext("rev")
                        if rev:
                            self._rev = rev.lstrip().rstrip()
                    self.sources.append(title_block.findtext("source"))

        for comp in xml.find("components") or []:
            refdes = comp.attrib.get("ref")

            footprint = comp.findtext("footprint") or ""

            part = SimpleNamespace(name=None, value=None, pattern=EP_PAT)
            inst = SimpleNamespace(name=None, value=None, pattern=INST_PAT)
            value = SimpleNamespace(name=None, value=None, pattern=VALUE_PAT)
            fields = comp.find("fields")
            if fields is not None:
                for field in fields:
                    _update(part, field, flavors, self._detected_flavors)
                    _update(inst, field, flavors, self._detected_flavors)
                    _update(value, field, flavors, self._detected_flavors)

            do_not_place = inst.value == "DNP"

            if not part.value:
                if not do_not_place:
                    log.warning(
                        "%s skipped due to missing EPIC part number"
                        '(field "EP")',
                        refdes,
                    )
                continue

            if value.value is None:
                value.value = comp.findtext("value", default="n/a")

            if do_not_place:
                log.info(
                    '%s marked as do-not-place ("%s=DNP")', refdes, inst.name
                )

            try:
                part_id = int(part.value)
            except ValueError:
                log.warning(
                    '%s has invalid EPIC part number "%s"', refdes, part.value
                )
                continue

            c = Component(part_id, refdes, value.value, footprint)

            if do_not_place:
                _bom_append(self.dnps, c)
            else:
                _bom_append(self.comps, c)

        for l in self.comps.values():
            for c in l:
                c.load_from_epic()
        for l in self.dnps.values():
            for c in l:
                c.load_from_epic()

        if flavors:
            unknown_flavors = [
                f for f in flavors if f not in self._detected_flavors
            ]
            if unknown_flavors:
                raise UnknownFlavorsError(
                    unknown_flavors, self._detected_flavors
                )

    def save_as_epic_assembly(self, force_update=False):
        """Save the BOM as an EPIC assembly.  If an EPIC assembly with the
        same part-number already exists, it is updated unless the
        assembly indicates that it was last updated by a different
        tool or an interactive EPIC user.  This is dected based on the
        last update type and the toolname set when the BOM object was
        created (see argument TOOLNAME). If the assembly was last
        edited by a different tool or interactive user, a kicad.Error
        exception is raised, unless FORCE_UPDATE is True.

        If an EPIC assembly item is created, its manufacturer is set
        to the MANUFACTURER specified when creating the BOM object and
        its part number will have the form bom:SCHEMATIC_NAME[-FLAVOR],
        where SCHEMATIC_NAME is the name of the schematic and FLAVOR is
        the name of the selected flavor (if any).

        Returns a pair containing the EPIC assembly part that was
        created/updated for the BOM and a boolean which is True if the
        assembly part created (False if it was updated).

        """
        assembly_name = f"bom:{self.schematic_name}{self.tags_str}"

        # see if the assembly exists already:
        old_assy: SimpleNamespace | None = None
        try:
            reply = self.epic_api.get(
                "part/?mfg=%s&mfg_pn=%s" % (self.manufacturer, assembly_name)
            )
            if (
                isinstance(reply, list)
                and reply
                and isinstance(reply[0], dict)
            ):
                old_assy = SimpleNamespace(**reply[0])
        except webapi.Error:
            pass

        if old_assy:
            if (
                old_assy.last_bom_mod_type != Enum.LAST_MOD_TYPE_TOOL
                or old_assy.last_bom_mod_name != self.toolname
            ):
                last_editor = "%s %s" % (
                    strchoice(
                        Enum.LAST_MOD_CHOICES, old_assy.last_bom_mod_type
                    ),
                    old_assy.last_bom_mod_name,
                )
                if force_update:
                    log.info(
                        "overwriting part %s %s last modified by %s",
                        self.manufacturer,
                        assembly_name,
                        last_editor,
                    )
                else:
                    raise Error(
                        "Refusing to overwrite part last modified "
                        "by %s %s."
                        % (last_editor, format_part_number(old_assy.id))
                    )

        desc = "BOM %s" % self.schematic_name
        if self._selected_flavors:
            desc += "-" + "-".join(sorted(list(self._selected_flavors)))
        assembly_part = SimpleNamespace(
            descr=desc,
            mfg=self.manufacturer,
            mfg_pn=assembly_name,
            mounting=Enum.MOUNTING_CHASSIS,
            target_price=1000,
            overage=1,
            spq=1,
            lead_time=4,
            status=Enum.STATUS_PREVIEW,
            last_bom_mod_type=Enum.LAST_MOD_TYPE_TOOL,
            last_bom_mod_name=self.toolname,
        )

        try:
            if old_assy:
                reply = self.epic_api.put(
                    "part/%d/" % old_assy.id, assembly_part
                )
            else:
                reply = self.epic_api.post("part/", assembly_part)
            reply = cast(dict[str, Any], reply)
            assembly_part = SimpleNamespace(**reply)
        except webapi.Error as e:
            raise Error(
                "Failed to create assembly part.", assembly_part
            ) from e

        # create assembly-items for the components in the BOM:
        assy_items = []
        for components in self.comps.values():
            comp = components[0]
            refdes = ",".join(sorted([c.refdes for c in components]))
            assy_item = SimpleNamespace(
                assy=assembly_part.id,
                comp=comp.part_id,
                qty=len(components),
                refdes=refdes,
            )
            assy_items.append(assy_item.__dict__)
        try:
            reply = self.epic_api.post("assembly_item/", assy_items)
        except webapi.Error as e:
            raise Error("Failed to save assembly items.", assy_items) from e

        return (assembly_part, not old_assy)

    @property
    def flavors(self) -> set[str]:
        """Return the set of flavors available in this BOM."""
        return self._detected_flavors

    @property
    def rev(self) -> str | None:
        """Return the hardware revision string (e.g., "5B") or `None`
        if unknown.

        """
        return self._rev

    @property
    def tags(self) -> list[str]:
        """Return a list of tags (if any) that uniquely identifies the
        BOM.  This typically consists of the hardware revision and the
        selected flavors.

        """
        tags = []
        if self._rev:
            tags.append(f"rev{self._rev}")
        if self._selected_flavors:
            tags += sorted(list(self._selected_flavors))
        return tags

    @property
    def tags_str(self) -> str:
        """Returns a string of dash-separated tags.  If there are no
        tags, the empty string is returned.  If there are some tags,
        the returned string starts with a dash.

        """
        tags = self.tags
        if not tags:
            return ""
        return "-" + "-".join(tags)
