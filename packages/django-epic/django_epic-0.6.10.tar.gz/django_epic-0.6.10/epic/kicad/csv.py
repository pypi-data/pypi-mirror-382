#
#   Copyright (c) 2021, 2025 eGauge Systems LLC
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
"""This module provides helper functions outputting the BOM as a CSV
file."""

from dataclasses import dataclass, fields
from pathlib import Path
from types import SimpleNamespace
from typing import Mapping, Sequence

import tablib

from epic.base import Enum, format_part_number

from .bom import BOM, Component
from .parts_cache import PartsCache
from .vendors_cache import VendorParts, VendorsCache


def _is_orderable(vp: SimpleNamespace) -> bool:
    """A vendor part is orderable only if itself and the corresponding
    part are orderable.

    Positional arguments:

    vp -- The vendor part to check whether its orderable.

    """
    if vp.status not in Enum.STATUS_ORDERABLE:
        return False
    part = PartsCache.get(vp.part)
    if part.status not in Enum.STATUS_ORDERABLE:
        return False
    return True


@dataclass
class BOMRow:
    qty: int | str | None = None
    value: str | None = None
    footprint: str | None = None
    pn: str | None = None
    mfg: str | None = None
    mfg_pn: str | None = None
    substitutes: str | None = None
    refdes: str | None = None  # colon-separated list of reference designators
    vendor_pns: list[str] | None = None

    def as_list(self) -> list:
        ret = []
        for f in fields(self.__class__):
            v = getattr(self, f.name)
            if isinstance(v, list):
                ret += v
            else:
                ret.append(v or "")
        return ret


class CSVBOM:
    def __init__(
        self,
        bom: BOM,
        vendors: None | Sequence[SimpleNamespace] = None,
    ):
        """Create a CSV version of the BOM.

        Positional arguments:

        bom -- The BOM to convert to CSV.

        vendors -- The list of vendors whose vendor part info to
                include in the CSV.  If `None`, no vendor part info
                at all is included.  If an empty list, vendor part info
                is included for all vendors that can supply at least one
                part for this BOM.  If a list of vendors, vendor part info
                for all of those vendors is included.

        """
        if vendors is None:
            self.vendors = tuple()
        elif vendors:
            self.vendors = vendors  # use select list of vendors
        else:
            # use all vendors that at least one part for this BOM:
            self.vendors = tuple(VendorsCache())

        self.vendor_parts = VendorParts(list(bom.comps.keys()), self.vendors)

        if vendors is not None and len(vendors) == 0:
            # only keep vendors which have at least one part for this BOM:
            self.vendors = tuple(
                v
                for v in VendorsCache()
                if self.vendor_parts.vendor_has_parts(v)
            )

        self.dataset = tablib.Dataset()
        self.dataset.headers = [
            "Qty",
            "Value",
            "Footprint",
            f"{bom.manufacturer} PN",
            "Mfg",
            "Mfg PN",
            "Approved Substitutes",
            "Refdes",
        ] + [f"{v.name} PN" for v in self.vendors]

        comp_list = self._bom_sort(bom.comps)
        self._output_list(comp_list)

        dnp_list = self._bom_sort(bom.dnps)
        if dnp_list:
            self.dataset.append(
                BOMRow(
                    qty="DO NOT PLACE parts:",
                    vendor_pns=len(self.vendors) * [""],
                ).as_list()
            )
            self._output_list(dnp_list)

    def save(self, filename: Path):
        """Save the CSV BOM in a file.

        Positional arguments:

        filename -- The path in which to save the CSV BOM.

        """
        with open(filename, "w") as f:
            f.write(self.dataset.export("csv"))

    def _bom_sort(
        self, comps: Mapping[int, Sequence[Component]]
    ) -> Sequence[Sequence[Component]]:
        return sorted(
            [comps for comps in comps.values() if comps],
            key=lambda comps: comps[0].part_id,
        )

    def _best_vendor_pn(
        self, part: SimpleNamespace, vendor: SimpleNamespace
    ) -> str:
        best_vp = None
        for pn in part.equivalents:
            vp = self.vendor_parts.get(pn, vendor)
            if not vp:
                continue

            if best_vp is None:
                best_vp = vp
                continue

            best_orderable = _is_orderable(best_vp)
            vp_orderable = _is_orderable(vp)

            if vp_orderable and (
                not best_orderable or vp.price < best_vp.price
            ):
                best_vp = vp
        if not best_vp:
            return ""
        return best_vp.vendor_pn

    def _output_list(self, bom_list: Sequence[Sequence[Component]]):
        """Append the components in a BOM list to the CSV BOM.

        Positional arguments:

        bom_list -- The list of components to append to the CSV.

        """
        for components in bom_list:
            c = components[0]
            if c.part:
                for sub_id in c.part.equivalents:
                    PartsCache.prefetch(sub_id)

        for components in bom_list:
            qty = len(components)
            refdes = ":".join(sorted([c.refdes for c in components]))
            c = components[0]

            substitutes = []
            vendor_pns = len(self.vendors) * [""]
            if c.part:
                for sub_id in c.part.equivalents:
                    if sub_id == c.part_id:
                        continue
                    sub = PartsCache.get(sub_id)
                    substitutes.append(
                        f"{format_part_number(sub.id)} ({sub.mfg} {sub.mfg_pn})"
                    )

                    vendor_pns = [
                        self._best_vendor_pn(c.part, v) for v in self.vendors
                    ]

            row = BOMRow(
                qty=qty,
                value=c.value,
                footprint=c.footprint,
                pn=format_part_number(c.part_id),
                mfg=c.mfg,
                mfg_pn=c.mfg_pn,
                substitutes=":".join(substitutes),
                refdes=refdes,
                vendor_pns=vendor_pns,
            )
            self.dataset.append(row.as_list())
