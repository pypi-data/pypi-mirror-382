#
#   Copyright (c) 2025 eGauge Systems LLC
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
"""This module implements a static cache of vendors."""

from types import SimpleNamespace
from typing import Sequence

from .epic_client import EPICAPIClient
from .error import Error
from .parts_cache import PartsCache


class VendorsCache:
    """A static cache of EPIC vendors."""

    cache: dict[int, SimpleNamespace] = {}
    _epic_api: EPICAPIClient | None = None

    @classmethod
    def set_epic(cls, epic_api: EPICAPIClient):
        """This method must be called before any other method in this
        class.

        Positional arguments:

        epic_api -- The API client to use to fetch information from
        EPIC.

        """
        if cls._epic_api != epic_api:
            cls.cache = {}
            cls._epic_api = epic_api

    @classmethod
    def get(cls, vendor_id: int) -> SimpleNamespace | None:
        """Get a vendor object by the vendor's id.

        Positional arguments:

        vendor_id -- The id of the vendor to return the vendor object
            for.

        """
        if not cls.cache:
            cls.load_cache()
        return cls.cache.get(vendor_id)

    @classmethod
    def find(cls, name: str, relaxed_match=False) -> SimpleNamespace | None:
        """Find a vendor object by name.

        Positional arguments:

        name -- The name of the vendor to find.

        relaxed_match -- If False, `name` must match the vendor name
                exactly.  Otherwise, the name is checked while
                ignoring upper vs lower case and the first vendor
                whose name starts with `name` will be returned.

        """
        if not cls.cache:
            cls.load_cache()
        for v in cls.cache.values():
            if v.name == name:
                return v
            if relaxed_match and v.name.lower().startswith(name.lower()):
                return v
        return None

    @classmethod
    def load_cache(cls):
        if cls._epic_api is None:
            raise Error("must call VendorsCache.set_epic() first")

        reply = cls._epic_api.get("vendor/")
        if not isinstance(reply, list):
            raise Error("Unable to get vendor list.")
        cls.cache = {v["id"]: SimpleNamespace(**v) for v in reply}

    def __iter__(self):
        if not self.__class__.cache:
            self.__class__.load_cache()
        self._iterator = self.__class__.cache.values().__iter__()
        return self._iterator

    def __next__(self):
        return self._iterator.__next__()

    @classmethod
    def get_vendor_parts(
        cls, pns: Sequence[int], vendor_ids: Sequence[int]
    ) -> Sequence[SimpleNamespace]:
        """Get the vendor part info for a list of parts and vendors.

        Positional arguments:

        pns -- The list of part numbers to return vendor part info
            for.

        vendor_ids -- The list of vendor ids to return vendor part info
            for.

        """
        if cls._epic_api is None:
            raise Error("must call VendorsCache.set_epic() first")

        reply = cls._epic_api.get(
            f"vendor_part/?part_id={pns}&vendor_id={vendor_ids}"
        )
        if not isinstance(reply, list):
            return []
        return [SimpleNamespace(**vpn) for vpn in reply]


class VendorParts:
    def __init__(
        self, parts: Sequence[int], vendors: Sequence[SimpleNamespace]
    ):
        """A cache of vendor parts.

        Positional arguments:

        parts -- The list of part numbers to cache vendor part info
            for.

        vendors -- The list of vendors to cache vendor part info for.

        """

        pns: list[int] = []
        for pn in parts:
            part = PartsCache.get(pn)
            pns += part.equivalents

        vids = [v.id for v in vendors]
        vendor_parts = VendorsCache.get_vendor_parts(pns, vids)

        self.parts: dict[int, dict[int, SimpleNamespace | None]] = {
            pn: {v.id: None for v in vendors} for pn in pns
        }

        for vp in vendor_parts:
            vendor = VendorsCache.get(vp.vendor)
            if vendor and vendor in vendors:
                self.parts[vp.part][vp.vendor] = vp

    def get(
        self, pn: int | None, vendor: SimpleNamespace | None
    ) -> SimpleNamespace | None:
        """Get a vendor part.

        Positional arguments:

        pn -- The part number to find the vendor part info for.  If
            `None`, `None` is returned.

        vendor -- The vendor for which to find the vendor part info
            for.  If `None`, `None` is returned.

        """
        if pn is None or vendor is None:
            return None
        return self.parts.get(pn, {}).get(vendor.id)

    def get_vpn(
        self, pn: int | None, vendor: SimpleNamespace | None
    ) -> str | None:
        """Get a vendor part number.

        Positional arguments:

        pn -- The part number to find the vendor part number for.  If
            `None`, `None` is returned.

        vendor -- The vendor for which to find the vendor part number
            for.  If `None`, `None` is returned.

        """
        vp = self.get(pn, vendor)
        return vp.vendor_pn if vp else None

    def vendor_has_parts(self, vendor: SimpleNamespace) -> bool:
        """Check if a vendor has any vendor parts cached.  Returns
        `True` if it does, `False` otherwise.

        Positional arguments:

        vendor -- The vendor to check.

        """
        return not all(
            self.get(pn, vendor) is None for pn in self.parts.keys()
        )
