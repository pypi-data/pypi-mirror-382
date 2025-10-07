#
#   Copyright (c) 2019 eGauge Systems LLC
# 	1644 Conestoga St, Suite 2
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
"""Helper class for managing stock cache records."""

from django.utils import timezone

from epic.models import Delta, Part_Inventory, Stock_Cache_Entry


def _cache_ts(ts):
    """Given the point in time `ts', return the timestamp of the nearest
    cache record that is not younger than `ts'.

    """
    if ts is None:
        ts = timezone.now()
    # round down to beginning of day:
    return ts.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


class Stock_Cache:
    @classmethod
    def get(cls, as_of_ts):
        """Get most recent part inventory from the cache.  The inventory is
        for a time that is not newer than `as_of_ts'.  If `as_of_ts'
        is None, the most recent part inventory is returned.
        Generally, the returned inventory may be older than `as_of_ts'
        since cache entries are created only at a certain granularity
        (e.g., at most one cache per day).  Consult the timestamp of
        the inventory to find out the actual time the returned
        inventory is for.

        """
        # find most recent stock cache entry, if any:
        qs = Stock_Cache_Entry.objects.all()
        if as_of_ts is not None:
            qs = qs.filter(ts__lte=as_of_ts)
        if qs.exists():
            stock_cache_entry = qs[0]
            inv = stock_cache_entry.inventory()
            # print('  STOCK_CACHE: found %s for %s' % (inv.ts, as_of_ts))
        else:
            inv = Part_Inventory()

        cache_ts = _cache_ts(as_of_ts)
        if inv.ts is None or inv.ts < cache_ts:
            # apply all deltas for transactions between inv.ts and cache_ts:
            qs = Delta.objects.order_by("txtn__ts")
            if inv.ts is not None:
                qs = qs.filter(txtn__ts__gt=inv.ts)
            qs = qs.filter(txtn__ts__lte=cache_ts)
            for d in qs:
                inv.apply_delta(d)

            # create a new stock cache entry for cache_ts:
            inv.ts = cache_ts
            new_stock_cache_entry = Stock_Cache_Entry()
            new_stock_cache_entry.save(inventory=inv)
            # print('  STOCK_CACHE: created %s for %s' % (inv.ts, as_of_ts))
        return inv
