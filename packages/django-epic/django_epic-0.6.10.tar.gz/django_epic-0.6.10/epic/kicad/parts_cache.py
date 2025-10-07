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
"""This module implements a static cache of EPIC parts."""

from types import SimpleNamespace

from egauge import webapi

from .epic_client import EPICAPIClient
from .error import Error


def _append_range(ranges, start, end):
    """If START is None, do nothing.  Otherwise, append a new range to
    RANGES.  If END > START, the range "START-END" is added, with
    START and END being decimal integers.  If END == START, the
    decimal "START" is added to RANGES.

    """
    if start is not None:
        r = "%d" % start
        if end > start:
            r += "-%d" % end
        ranges.append(r)


def _range_list_from_set(s):
    """Return a string that concisely represents the set S as a list for
    ranges.  Each range is either a decimal number or two decimal
    numbers separated by '-'.  The ranges themselves are separated by
    commas.

    """
    l = sorted(list(s))
    ranges = []
    start = end = None
    for n in l:
        if start is None or end is None:
            start = end = n
        elif n == end + 1:
            end = n
        else:
            _append_range(ranges, start, end)
            start = end = n
    _append_range(ranges, start, end)
    return ",".join(ranges)


class PartsCache:
    """A static cache of EPIC parts."""

    needed = set()
    cache: dict[int, SimpleNamespace] = {}
    epic_api = None

    @classmethod
    def set_epic(cls, epic_api: EPICAPIClient):
        """Establishes EPIC_API as the EPIC API to use for fetching parts
        info.  This must be called prior to the first call of
        PartsCache.get().  If the EPIC API used changes, the cache is
        cleared.

        """
        if cls.epic_api != epic_api:
            cls.cache = {}
            cls.epic_api = epic_api

    @classmethod
    def prefetch(cls, part_number: int):
        """Prefetch the part with number PART_NUMBER.  This current
        implementation simply records the part number internall and
        does not actually cause any calls to the EPIC API.

        """
        if part_number in cls.cache or part_number in cls.needed:
            return
        cls.needed.add(part_number)

    @classmethod
    def get(cls, part_number: int):
        """Get the part with number PART_NUMBER.  If the part is already in
        the cache, the part will be returned immediately.  Otherwise,
        the part will be fetched through the EPIC API, along with any
        other parts that have been prefetched since the most recent
        call to thos method.  Once that info is received, the cache is
        updated and the requested part returned.

        """
        if cls.epic_api is None:
            raise Error("must call Parts.set_epic() first")

        if part_number not in cls.cache:
            if part_number not in cls.needed:
                cls.prefetch(part_number)
            r = _range_list_from_set(cls.needed)
            try:
                reply = cls.epic_api.get("part/?id=%s" % r)
            except webapi.Error as e:
                raise Error("Failed to get part.", r) from e
            if not isinstance(reply, list):
                raise Error("Invalid server response while getting parts.", r)
            for p in reply:
                part = SimpleNamespace(**p)
                cls.cache[part.id] = part
        return cls.cache[part_number]
