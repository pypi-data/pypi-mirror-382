#
#   Copyright (c) 2014-2019, 2021-2022, 2025 eGauge Systems LLC
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
# pylint: disable=too-few-public-methods, no-member
from __future__ import print_function

import hashlib
import math
import re
from datetime import date, timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.humanize.templatetags.humanize import intcomma
from django.core.cache import caches
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.html import escape

from epic.base import Enum, format_part_number, strchoice

# pylint: disable=arguments-differ
# pylint: disable=too-many-lines

PART_PRICE_VALIDATORS = [MinValueValidator(Decimal("0.000001"))]
CACHE = caches["epic"]


def part_cost(line_cost, qty):
    if qty <= 0:
        return 0
    return Decimal("%.6f" % (float(line_cost) / qty))


def html_part_link(part):
    """Return an HTML link for PART.  PART may be either a Part object or
    a part number.
    """
    if isinstance(part, Part):
        pn = part.id
    else:
        pn = part
    name = format_part_number(pn)
    url = reverse("epic:part_detail", kwargs={"pk": pn})
    return '<a href="%s">%s</a>' % (url, name)


def html_list_or_none(l):
    """If L is empty, return 'none', otherwise, join the list using ','
    as a separator.
    """
    html = ", ".join(l)
    if html != "":
        return html
    return "<em>&mdash;None&mdash;</em>"


class Datasheet(models.Model):
    name = models.CharField(max_length=128, unique=True, blank=False)
    ds_file = models.FileField(
        upload_to=getattr(settings, "EPIC_DATASHEET_DIR", "epic/datasheets"),
        blank=False,
        verbose_name="Datasheet File",
    )
    notes = models.CharField(
        max_length=1024,
        help_text="For misc. information that may be useful "
        "along with the datasheet, such as website retrieved from.",
        blank=True,
    )
    md5sum = models.CharField(max_length=36, null=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return "%s" % self.name

    def html_link(self):
        url = reverse("epic:datasheet_detail", kwargs={"pk": self.id})
        return '<a href="%s">%s</a>' % (url, self.name)

    def save(self, *args, **kwargs):
        md5 = hashlib.md5()
        for chunk in self.ds_file.chunks():
            md5.update(chunk)
        self.md5sum = md5.hexdigest()
        super().save(*args, **kwargs)

    # See signals.datasheet_delete() for deletion cleanup.


class Part(models.Model):
    val = models.CharField(
        max_length=127,
        verbose_name="Value",
        blank=True,
        default="",
        help_text="The primary value of the part "
        "such as resistance for a resistor or "
        "capacitance for a capacitor.",
    )
    descr = models.CharField(
        max_length=127,
        verbose_name="Description",
        blank=True,
        default="",
        help_text="Brief listing of key parameters of "
        "the part, such as temperature range, drift, "
        "max. voltages, etc.",
    )
    footprint = models.CharField(
        max_length=127,
        blank=True,
        default="",
        help_text="The part's PCB footprint.",
    )
    mfg = models.CharField(
        max_length=127,
        verbose_name="Manufacturer",
        help_text="The name of the manufacturer of the part.",
    )
    mfg_pn = models.CharField(
        max_length=127, verbose_name="Manufacturer's Part #"
    )
    mounting = models.IntegerField(
        choices=Enum.MOUNTING_CHOICES,
        default=Enum.MOUNTING_SMD,
        blank=False,
        verbose_name="Mounting Type",
        help_text="How the part is mounted to a "
        "PCB (free if it's not mounted at all, "
        "such as a plug).",
    )
    target_price = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        validators=PART_PRICE_VALIDATORS,
        verbose_name="Target price [$]",
        help_text="The expected price of the part.",
    )
    overage = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        validators=[
            MinValueValidator(Decimal("0")),
            MaxValueValidator(Decimal("100")),
        ],
        verbose_name="Overage [%]",
        help_text="Worst-case percentage of parts "
        "we expect to lose due to attrition at the "
        "assembly-house.",
    )
    spq = models.IntegerField(
        default=1,
        verbose_name="Standard-Package Qty",
        help_text="The number of parts in "
        "a standard package.  For example, 10,000 "
        "pieces in a reel.",
    )
    lead_time = models.PositiveIntegerField(
        verbose_name="Lead-time [weeks]", help_text="Lead-time in weeks."
    )
    status = models.IntegerField(
        choices=Enum.STATUS_CHOICES,
        default=Enum.STATUS_PREVIEW,
        blank=False,
        verbose_name="Life-time Status",
        help_text="The life-time status of this "
        "part. Parts marked `preview' and "
        "`obsolete' are not considered orderable.",
    )
    substitute = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        verbose_name="Substitutes",
        help_text="List of other parts that are "
        "(identical) substitutes for this part.",
        on_delete=models.PROTECT,
    )
    last_bom_mod_type = models.IntegerField(
        choices=Enum.LAST_MOD_CHOICES,
        default=Enum.LAST_MOD_TYPE_USER,
        blank=False,
    )
    last_bom_mod_name = models.CharField(
        max_length=127,
        blank=True,
        default="",
        help_text="Name of entity which last modified this part.",
    )
    datasheet = models.ForeignKey(
        Datasheet, null=True, blank=True, on_delete=models.PROTECT
    )
    notes = models.TextField(
        blank=True, default="", help_text="Notes regarding this part."
    )

    class Meta:
        ordering = ["id"]
        unique_together = ("mfg", "mfg_pn")
        indexes = [models.Index(fields=["mfg", "mfg_pn"])]

    def __str__(self):
        return "%s" % (format_part_number(self.id))

    @classmethod
    def flush_caches(cls, sender, **kwargs):
        # pylint: disable=unused-argument
        """See signals.flush_caches()."""
        # clear the caches when a part changes:
        CACHE.clear()

    def equivalent_parts(self):
        """Return the set of equivalent parts for this part.  The set includes
        the part itself.  However, if the part doesn't have an id yet
        (newly created and not saved yet), the empty set is returned.

        """

        def get_set(equiv_parts, part):
            if part.id in equiv_parts:
                return equiv_parts[part.id]
            return frozenset([part.id])

        if self.id is None:
            # newly created parts don't have a valid id yet so they can't
            # be hashed, which also means nobody can be referring to it,
            # which means its equivalent-parts-set is empty.
            return frozenset([])

        equiv_parts = CACHE.get("equiv-parts")
        if equiv_parts is None:
            equiv_parts = {}
            for p in Part.objects.exclude(substitute__isnull=True):
                union = get_set(equiv_parts, p)
                union |= get_set(equiv_parts, p.substitute)
                for q_id in union:
                    equiv_parts[q_id] = union
            CACHE.set("equiv-parts", equiv_parts, timeout=None)
        return [Part.objects.get(pk=id) for id in get_set(equiv_parts, self)]

    def best_part(self):
        """Among the set of parts equivalent to this part, find orderable,
        preferred, or lowest-cost part.  Returns part itself if nothing
        better is available.

        """
        best_id = CACHE.get("best-part-" + str(self.id))
        if best_id is not None:
            return Part.objects.get(pk=best_id)

        best_part = self  # may not be orderable...
        for p in self.equivalent_parts():
            if p == self or not p.is_orderable():
                continue

            if (p.status == Enum.STATUS_PREFERRED) != (
                best_part.status == Enum.STATUS_PREFERRED
            ):
                if p.status == Enum.STATUS_PREFERRED:
                    best_part = p
                continue

            target_pr = p.target_price
            best_pr = best_part.target_price
            if (
                not best_part.is_orderable()
                or target_pr < best_pr
                or (target_pr == best_pr and p.id < best_part.id)
            ):
                best_part = p
        for p in self.equivalent_parts():
            CACHE.set("best-part-" + str(self.id), best_part.id, timeout=None)
        return best_part

    def best_vendor(self):
        """Return the vendor that has the lowest price for this part."""
        vps = Vendor_Part.objects.filter(part_id=self.id).order_by("price")
        for vp in vps:
            if vp.status in Enum.STATUS_ORDERABLE:
                return vp.vendor
        return None

    def is_orderable(self):
        return self.status in Enum.STATUS_ORDERABLE

    def assembly_items(self):
        return Assembly_Item.objects.filter(assy_id=self.id)

    def html_link(self):
        return html_part_link(self)

    def avg_cost(self):
        """Get average cost for a part, including any of its substitutes.  The
        average is calculated across orders with shipments within the past
        365 days.  If there is no shipment within 365, the cost is
        calculated based on the most recent shipment alone.  If there are
        no shipments at all, return the part's target price.
        """
        CACHE_ID = "total-costs"
        COST = 0
        QTY = 1
        total = CACHE.get(CACHE_ID)
        if total is None:
            total = {}
            cut_off_ts = timezone.now() - timedelta(days=365)

            deltas = (
                Delta.objects.filter(adj__gt=0)
                .filter(txtn__shipment__ts__gte=cut_off_ts)
                .order_by("txtn_id")
            )
            for d in deltas:
                cost = d.txtn.shipment.cost_details()
                overhead_ratio = 0
                if cost["parts"] > 0:
                    overhead_ratio = cost["overhead"] / cost["parts"]

                if d.part.id not in cost["part_detail"]:
                    continue
                pc = cost["part_detail"][d.part.id]

                if d.part.id not in total:
                    total[d.part.id] = [0, 0]
                if d.txtn.shipment.from_warehouse is None:
                    piece_cost = float(pc["cost"]) / pc["qty"]
                    total[d.part.id][COST] += (d.adj * piece_cost) * (
                        1 + float(overhead_ratio)
                    )
                    total[d.part.id][QTY] += d.adj
                elif cost["parts_target"] > 0:
                    # For inter-warehouse-shipments, allocate the
                    # shipping costs in proportion to the
                    # target-cost of the parts
                    part_ratio = (pc["qty"] * d.part.target_price) / cost[
                        "parts_target"
                    ]
                    total[d.part.id][COST] += float(
                        part_ratio * cost["overhead"]
                    )
            CACHE.set(CACHE_ID, total, timeout=None)

        cost = 0
        qty = 0
        for p in self.equivalent_parts():
            if p.id in total:
                cost += total[p.id][COST]
                qty += total[p.id][QTY]
        if qty <= 0:
            return self.target_price
        return part_cost(cost, qty)

    def best_vendor_part(self, preferred_vendors=None):
        """Find the best (lowest-cost and orderable) part from the specified
        list of preferred vendors (or any vendor if preferred_vendors
        is None).  If the part cannot be ordered from any of the
        preferred vendors, return the vendor part from the
        non-preferred vendor with the lowest cost.

        """
        best_vp_any = None
        best_vp_preferred = None
        for p in self.equivalent_parts():
            if not p.is_orderable():
                continue
            vps = Vendor_Part.objects.filter(part_id=p.id)
            for vp in vps:
                if not vp.is_orderable():
                    continue
                if best_vp_any is None or vp.price < best_vp_any.price:
                    best_vp_any = vp
                if (
                    preferred_vendors is None
                    or vp.vendor not in preferred_vendors
                ):
                    continue
                if (
                    best_vp_preferred is None
                    or vp.price < best_vp_preferred.price
                ):
                    best_vp_preferred = vp
        if best_vp_preferred:
            return best_vp_preferred
        return best_vp_any

    def strstatus(self):
        return strchoice(Enum.STATUS_CHOICES, self.status)

    def choice_label(self):
        return "%s: %s %s" % (self, self.mfg, self.mfg_pn)


class Vendor(models.Model):
    name = models.CharField(
        max_length=127, verbose_name="Vendor Name", unique=True
    )
    search_url = models.CharField(
        max_length=127,
        verbose_name="Search URL Pattern",
        default="",
        blank=True,
        help_text="This pattern defines how to "
        "search for a particular part on the "
        "vendor's website.  %(vendor_pn)s gets "
        "replaced by the vendor's part-number, "
        "%(mfg)s by the manufacturer's name, and "
        "%(mfg_pn)s by the manufacturer's "
        "part-number.",
    )

    def __str__(self):
        return "%s" % self.name

    def html_link(self):
        url = reverse("epic:vendor_detail", kwargs={"pk": self.id})
        return '<a href="%s">%s</a>' % (url, self.name)

    def is_vendor(self):
        # pylint: disable=no-self-use
        return True

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["name"])]


class Vendor_Part(models.Model):
    part = models.ForeignKey(
        Part, verbose_name="Part #", on_delete=models.CASCADE
    )
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    vendor_pn = models.CharField(
        max_length=127, verbose_name="Vendor's Part #"
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=6, validators=PART_PRICE_VALIDATORS
    )
    status = models.IntegerField(
        choices=Enum.STATUS_CHOICES,
        default=Enum.STATUS_ACTIVE,
        blank=False,
        verbose_name="Life-time Status",
        help_text="The life-time status of this vendor part.",
    )

    class Meta:
        unique_together = (("vendor", "part"), ("vendor", "vendor_pn"))

    def __str__(self):
        return "Vendor_Part %s: %s %s" % (
            format_part_number(self.part.id),
            self.vendor.name,
            self.vendor_pn,
        )

    def html_link(self):
        url =""
        if self.vendor.search_url:
            try:
                url = self.vendor.search_url % {
                    "mfg": escape(self.part.mfg),
                    "mfg_pn": escape(self.part.mfg_pn),
                    "vendor_pn": escape(self.vendor_pn),
                }
            except (KeyError, TypeError, ValueError):
                pass

        if not url:
            return escape(self.vendor_pn)

        return '<a href="%s" target="part_lookup">%s</a>' % (
            url,
            self.vendor_pn,
        )

    def strstatus(self):
        return strchoice(Enum.STATUS_CHOICES, self.status)

    def is_orderable(self):
        return self.status in Enum.STATUS_ORDERABLE

    @staticmethod
    def get(part_id, vendor_id):
        result = Vendor_Part.objects.filter(part_id=part_id).filter(
            vendor_id=vendor_id
        )
        if len(result) != 1:
            return None
        return result[0]


class Warehouse(models.Model):
    name = models.CharField(
        max_length=127, unique=True, help_text="The name of the warehouse."
    )
    address = models.TextField(
        blank=True,
        default="",
        help_text="The shipping address for the warehouse.",
    )

    def __str__(self):
        return "%s" % self.name

    def html_link(self):
        url = reverse("epic:warehouse_detail", kwargs={"pk": self.id})
        return '<a href="%s">%s</a>' % (url, self.name)

    def inventories(self):
        return Inventory.objects.filter(warehouse_id=self.id)

    @staticmethod
    def by_name(name):
        return Warehouse.objects.get(name=name)

    class Meta:
        ordering = ["name"]


class Delta(models.Model):
    """Deltas are used to track all quantity adjustments to a part at a
    given warehouse.  The adjustment may be relative to existing
    quantity or absolute.
    """

    part = models.ForeignKey(
        Part,
        verbose_name="Part #",
        help_text="The part whose quantity gets adjusted.",
        on_delete=models.PROTECT,
    )
    is_absolute = models.BooleanField(
        verbose_name="Absolute Adjustment",
        default=False,
        help_text="If set, the adjustment is "
        "absolute otherwise it is relative.",
    )
    adj = models.IntegerField(
        verbose_name="Adjustment Count",
        help_text="The amount by which the part "
        "quantity should be adjusted by.",
    )
    txtn = models.ForeignKey(
        "Transaction", verbose_name="Transaction #", on_delete=models.CASCADE
    )
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT)

    class Meta:
        indexes = [
            models.Index(fields=["txtn"]),
            models.Index(fields=["warehouse"]),
        ]

    def line_item(self):
        """For order or shipments items, return associated line-item."""
        line_items = Line_Item.objects.filter(txtn_id=self.txtn.id).filter(
            part_id=self.part_id
        )
        if len(line_items) != 1:
            return None
        return line_items[0]

    def line_cost(self):
        """For order or shipments items, return line-cost for this delta."""
        line_item = self.line_item()
        if line_item is None:
            return None
        return Decimal(
            "%.2f" % (self.adj * float(line_item.line_cost) / line_item.qty)
        )

    def __str__(self):
        return "Delta %s" % self.id


class Assembly_Item(models.Model):
    assy = models.ForeignKey(
        Part,
        related_name="assembly_item_part",
        verbose_name="Assembly Part #",
        help_text="The part number of the assembly this item belongs to.",
        on_delete=models.CASCADE,
    )
    comp = models.ForeignKey(
        Part,
        related_name="assembly_item_comp",
        verbose_name="Component Part #",
        help_text="The part number of the component of this item.",
        on_delete=models.PROTECT,
    )
    qty = models.PositiveIntegerField(
        help_text="The quantity of this component required by the assembly."
    )
    refdes = models.TextField(
        blank=True,
        default="",
        verbose_name="Refdes List",
        help_text="A list of comma-separated reference "
        'designators e.g., "R101,R304". '
        "The length of this list should match Quantity.",
    )

    class Meta:
        unique_together = ("assy", "comp")
        indexes = [models.Index(fields=["assy", "comp"])]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.assy is not None:
            qs = Stock_Cache_Entry.objects.filter(
                stock_cache_item__part_id=self.assy.id
            )
            if qs.exists():
                Stock_Cache_Entry.invalidate(qs.order_by("ts")[0].ts)

    def qty_with_overage(self, factor):
        q = math.ceil(abs(factor) * self.qty * (1 + self.comp.overage / 100))
        return int(math.copysign(q, factor))

    def __str__(self):
        return "Assembly_Item %s.%s" % (
            format_part_number(self.assy_id),
            format_part_number(self.comp_id),
        )

    def clean(self):
        refdes_list = re.findall(r"([^, ]+)", self.refdes)
        self.refdes = ",".join(refdes_list)


class Line_Item(models.Model):
    txtn = models.ForeignKey(
        "Transaction", verbose_name="Transaction #", on_delete=models.CASCADE
    )
    part = models.ForeignKey(
        Part, verbose_name="Part #", on_delete=models.PROTECT
    )
    qty = models.PositiveIntegerField(help_text="The quantity of this part.")
    line_cost = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        verbose_name="Amount",
        help_text="The total cost of this "
        "line-item.  Part-cost is line-item cost "
        "divided by quantity.",
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    index = models.PositiveIntegerField(
        help_text="Sequential and unchanging index of this line-item."
    )

    class Meta:
        ordering = ["index"]
        unique_together = (("txtn", "part"), ("txtn", "index"))
        indexes = [
            models.Index(fields=["txtn", "index"]),
            models.Index(fields=["txtn", "part"]),
        ]

    def vendor_part(self):
        result = Vendor_Part.objects.filter(part_id=self.part_id).filter(
            vendor_id=self.txtn.order.vendor.id
        )
        if len(result) != 1:
            return None
        return result[0]

    def part_cost(self):
        return part_cost(self.line_cost, self.qty)

    def order_line_item(self):
        """For shipment line-items, return associated order line-item."""
        line_items = Line_Item.objects.filter(
            txtn_id=self.txtn.shipment.ordr.id
        ).filter(part_id=self.part_id)
        if len(line_items) != 1:
            return None
        return line_items[0]

    def qty_remaining_to_ship(self):
        if not hasattr(self.txtn, "order"):
            return None

        shipment_ids = Shipment.objects.filter(
            ordr_id=self.txtn_id
        ).values_list("transaction_ptr_id", flat=True)
        already_shipped = sum(
            Line_Item.objects.filter(txtn_id__in=shipment_ids)
            .filter(part_id=self.part_id)
            .values_list("qty", flat=True)
        )
        return self.qty - already_shipped


class Transaction(models.Model):
    """Orders, shipments, and inventories are all transactions."""

    ts = models.DateTimeField(
        verbose_name="Creation Time",
        help_text="Date and time when this transaction was created.",
    )
    warehouse = models.ForeignKey(
        Warehouse,
        verbose_name="Warehouse",
        help_text="The (destination) warehouse this transaction applies to.",
        on_delete=models.PROTECT,
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Notes",
        help_text="Comments and notes for this transaction",
    )

    def __str__(self):
        return "Transaction %u" % (self.id)

    def save(self, *args, **kwargs):
        if self.id is not None:
            qs = Transaction.objects.filter(pk=self.id)
            if qs.exists():
                old = qs[0]

                if hasattr(self, "shipment"):
                    # delete all deltas for this transaction, if any;
                    # the new deltas will be created during the
                    # update_deltas() call
                    Delta.objects.filter(txtn_id=old.id).delete()

                # invalidate stock-cache entries not older than the minimum
                # old or new ts of this transaction:
                ts = min(self.ts, old.ts)
                Stock_Cache_Entry.invalidate(ts)
        super().save(*args, **kwargs)

    def first_available_index(self):
        max_index = 0
        for item in Line_Item.objects.filter(txtn_id=self.id):
            if item.index > max_index:
                max_index = item.index
        return max_index + 1

    def update_order_status(self):
        if hasattr(self, "order"):
            # transaction is an order...
            order = self.order
            # we ought to be able to check if the transaction is a
            # shipment by checking for hasattr(self, 'shipment').
            # However, that does not work if the shipment has been
            # deleted AND self.shipment has not been accessed before.
            # Fortunately, 'ordr' exists in all cases and is also
            # unique to a shipment:
        elif hasattr(self, "ordr"):
            # transaction is a shipment
            order = self.ordr
            if order is None:
                return  # inter-warehouse shipment
        else:
            return

        status = Enum.TXTN_STATUS_CLOSED
        for line_item in Line_Item.objects.filter(txtn_id=order.id):
            if line_item.qty_remaining_to_ship() > 0:
                status = Enum.TXTN_STATUS_OPEN
                break

        if status != order.status:
            order.status = status
            order.save()

    def update_deltas(self):
        if hasattr(self, "order") or hasattr(self, "inventory"):
            # orders never have deltas and inventories directly edit the deltas
            return

        if hasattr(self, "shipment"):
            # For shipments that have not been deleted yet, create a
            # delta for each line-item in the shipment:
            ship = self.shipment
            src_warehouse = ship.src_warehouse()

            for line_item in Line_Item.objects.filter(txtn_id=ship.id):
                d = Delta(
                    part_id=line_item.part_id,
                    is_absolute=False,
                    adj=line_item.qty,
                    txtn_id=self.id,
                    warehouse_id=ship.warehouse_id,
                )
                d.save()

                assy_items = d.part.assembly_items()
                if ship.ordr and assy_items.exists():
                    # assemblies ordered from an assembly-house are created
                    # from parts at the assembly-house:
                    for assy_item in assy_items:
                        qty = -assy_item.qty_with_overage(line_item.qty)
                        part = assy_item.comp.best_part()
                        d = Delta(
                            part_id=part.id,
                            is_absolute=False,
                            adj=qty,
                            txtn_id=self.id,
                            warehouse_id=src_warehouse.id,
                        )
                        d.save()
                elif ship.from_warehouse is not None:
                    d = Delta(
                        part_id=line_item.part_id,
                        is_absolute=False,
                        adj=-line_item.qty,
                        txtn_id=self.id,
                        warehouse_id=src_warehouse.id,
                    )
                    d.save()

    def finalize(self):
        self.update_order_status()
        self.update_deltas()

    def description(self):
        if hasattr(self, "order"):
            ttl = self.order.days_until_past_due()
            extra = ""
            if ttl and ttl <= 0:
                extra = " (expected %d days ago)" % -ttl
            desc = "%s PO %s shipping to %s%s." % (
                self.order.vendor.html_link(),
                self.order.html_link(),
                self.warehouse.html_link(),
                extra,
            )
        elif hasattr(self, "shipment"):
            ship = self.shipment
            if ship.ordr_id:
                desc = "Shipment %s to %s for %s PO %s." % (
                    ship.html_link(),
                    ship.warehouse.html_link(),
                    ship.ordr.vendor.html_link(),
                    ship.ordr.html_link(),
                )
            else:
                desc = "Shipment %s from %s to %s." % (
                    ship.html_link(),
                    ship.from_warehouse.html_link(),
                    ship.warehouse.html_link(),
                )
        elif hasattr(self, "inventory"):
            desc = "Inventory %s at %s." % (
                self.inventory.html_link(),
                self.warehouse.html_link(),
            )
        else:
            desc = "Unknown transaction %d." % self.id
        return desc

    def html_link(self):
        if hasattr(self, "order"):
            return "Order&nbsp;%s" % self.order.html_link()
        if hasattr(self, "shipment"):
            return "Shipment&nbsp;%s" % self.shipment.html_link()
        if hasattr(self, "inventory"):
            return "Inventory&nbsp;%s" % self.inventory.html_link()
        return "Transaction&nbsp;%d" % (self.id)


class Order(Transaction):
    expected_arrival_date = models.DateField(
        verbose_name="Expected Arrival Date",
        help_text="Date when the order is expected to arrive.",
    )
    status = models.IntegerField(
        choices=Enum.TXTN_STATUS_CHOICES,
        default=Enum.TXTN_STATUS_OPEN,
        blank=False,
        verbose_name="Order Status",
    )
    vendor = models.ForeignKey(
        Vendor,
        help_text="The name of the "
        "vendor (distributor) where the order "
        "was placed.",
        on_delete=models.PROTECT,
    )

    def __str__(self):
        return "%u" % (self.id)

    def total_cost(self):
        return sum(
            Line_Item.objects.filter(txtn_id=self.id).values_list(
                "line_cost", flat=True
            )
        )

    def is_open(self):
        return self.status == Enum.TXTN_STATUS_OPEN

    def days_until_past_due(self):
        if self.status != Enum.TXTN_STATUS_OPEN:
            return None
        return (self.expected_arrival_date - date.today()).days

    def assembly_line_items(self):
        """Returns the list of line-items that are assemblies."""
        assemblies = Assembly_Item.objects.values_list(
            "assy_id", flat=True
        ).distinct()
        return Line_Item.objects.filter(txtn_id=self.id).filter(
            part_id__in=assemblies
        )

    def html_link(self):
        url = reverse("epic:order_detail", kwargs={"pk": self.id})
        return '<a href="%s">%s</a>' % (url, self.id)

    def choice_label(self):
        return "%s: %s $%s" % (
            self.id,
            self.vendor.name,
            intcomma(self.total_cost()),
        )


class Shipment(Transaction):
    tracking = models.CharField(
        max_length=127,
        default="",
        blank=True,
        verbose_name="Tracking #s",
        help_text="Comma-separated list of tracking numbers.",
    )
    # order is a reserved word in django...
    ordr = models.ForeignKey(
        Order,
        verbose_name="Order #",
        null=True,
        blank=True,
        help_text="For an order shipment, the "
        "order that resulted in this shipment.",
        on_delete=models.PROTECT,
    )
    from_warehouse = models.ForeignKey(
        Warehouse,
        null=True,
        blank=True,
        help_text="For an inter-warehouse "
        "shipment, the warehouse "
        "the shipment originates from.",
        on_delete=models.PROTECT,
    )
    cost_freight = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        verbose_name="Freight Cost",
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    cost_other = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        verbose_name="Other Costs",
        help_text="Other costs assessed by the "
        "shipper, such as handling costs.",
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    cost_discount = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        verbose_name="Discount Given",
        help_text="Discounts given by the "
        "shipper, such as early payment "
        "discount.",
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    @classmethod
    def flush_caches(cls, sender, **kwargs):
        """See signals.flush_caches()."""
        # pylint: disable=unused-argument
        # cache of shipment costs, indexed by transaction id
        CACHE.clear()

    def __str__(self):
        return "Shipment %u" % self.id

    def clean(self):
        tracking_list = re.findall(r"([^, ]+)", self.tracking)
        self.tracking = ",".join(tracking_list)

    def html_link(self):
        url = reverse("epic:ship_detail", kwargs={"pk": self.id})
        return '<a href="%s">%s</a>' % (url, self.id)

    def html_tracking_links(self):
        trk_list = self.tracking.split(",")
        url_pattern = "https://pkge.net/parcel/%s"
        result = []
        for trk in trk_list:
            trk = trk.strip()
            url = url_pattern % trk
            result.append(
                '<a target="trk_lookup" href="%s">%s</a>' % (url, trk)
            )
        return html_list_or_none(result)

    def src_warehouse(self):
        if self.ordr is not None:
            try:
                return Warehouse.by_name(self.ordr.vendor)
            except Exception:
                return None
        else:
            return self.from_warehouse

    def overhead_cost(self):
        """Return the cost of overheads of this shipment."""
        return self.cost_freight + self.cost_other - self.cost_discount

    def cost_details(self):
        costs = CACHE.get("costs-" + str(self.id))
        if costs is None:
            parts_cost = 0
            parts_target_cost = 0
            part_detail = {}
            for line_item in Line_Item.objects.filter(txtn_id=self.id):
                part_detail[line_item.part_id] = {
                    "cost": line_item.line_cost,
                    "qty": line_item.qty,
                }
                if self.from_warehouse is None:
                    parts_cost += line_item.line_cost
                else:
                    # for inter-warehouse shipments, each line_item.line_cost
                    # is zero but we need an approximation of part cost so
                    # we can allocate the cost of the shipment properly
                    parts_target_cost += (
                        line_item.qty * line_item.part.target_price
                    )
            costs = {
                "overhead": self.overhead_cost(),
                "parts": parts_cost,
                "parts_target": parts_target_cost,
                "part_detail": part_detail,
            }
            CACHE.set("costs-" + str(self.id), costs, timeout=None)
        return costs

    def parts_cost(self):
        """Return the total cost of all parts in this shipment."""
        return self.cost_details()["parts"]

    def total_cost(self):
        return self.overhead_cost() + self.parts_cost()


class Inventory(Transaction):
    def __str__(self):
        return "Inventory %u" % self.id

    def html_link(self):
        url = reverse(
            "epic:warehouse_inventory_detail",
            kwargs={"warehouse": self.warehouse.id, "pk": self.id},
        )
        return '<a href="%s">%s</a>' % (url, self.id)


class Part_Count:
    # pylint: disable=too-few-public-methods
    def __init__(self, qty=0):
        self.qty = qty
        self.is_final = False


class Part_Inventory:
    def __init__(self, ts=None):
        self.warehouse = {}
        self.ts = ts

    def __str__(self):
        lines = []
        lines.append("Inventory as of %s:" % self.ts)
        for name, warehouse in self.warehouse.items():
            s = ""
            for p in warehouse:
                if warehouse[p].qty != 0:
                    s += " %s*%d" % (format_part_number(p), warehouse[p].qty)
            lines.append("  Warehouse %s:%s" % (name, s))
        return "\n".join(lines)

    def get_entry(self, warehouse_id, part_id):
        if warehouse_id in self.warehouse:
            entry = self.warehouse[warehouse_id]
        else:
            self.warehouse[warehouse_id] = entry = {}
        if part_id not in entry:
            entry[part_id] = Part_Count()
        return entry[part_id]

    def apply_assembly_item(self, warehouse_id, item, factor):
        # Note: Even though this component might be an assembly itself,
        #  there is no need to recurse down because parts do not
        #  spontaneously transform into assemblies.  That is, even if
        #  we had the pre-requisite sub-components, there still has to
        #  be an assembly order which is where we'd do the proper
        #  sub-component qty adjustments.
        part_id = item.comp.best_part().id
        qty = item.qty_with_overage(factor)
        entry = self.get_entry(warehouse_id, part_id)
        entry.qty += qty

    def apply_order_line_item(self, item):
        part_id = item.part_id
        order = item.txtn.order
        qty = item.qty_remaining_to_ship()
        if qty <= 0:
            return
        entry = self.get_entry(order.warehouse_id, part_id)
        entry.qty += qty

        assy_items = item.part.assembly_items()
        if assy_items.exists() > 0:
            vendor_id = Warehouse.by_name(order.vendor).id
            for assy_item in item.part.assembly_items():
                self.apply_assembly_item(vendor_id, assy_item, -qty)

    def apply_delta(self, delta, reverse_chronological_order=False):
        """Adjust inventory according to DELTA.  If applying deltas in reverse
        chronological order (newest first), you must set
        REVERSE_CHRONOLOGICAL_ORDER to True and stop processing deltas
        after as the first delta with "is_absolute==True" has been
        processed.

        """
        entry = self.get_entry(delta.warehouse_id, delta.part_id)
        if entry.is_final:
            return

        if delta.is_absolute:
            if reverse_chronological_order:
                entry.qty += delta.adj
                entry.is_final = True
            else:
                entry.qty = delta.adj
        elif not entry.is_final:
            entry.qty += delta.adj

    def get_qty(self, warehouse, part):
        if warehouse not in self.warehouse:
            return 0
        if part not in self.warehouse[warehouse]:
            return 0
        return self.warehouse[warehouse][part].qty

    def adj_qty(self, warehouse, part, adj):
        entry = self.get_entry(warehouse, part)
        entry.qty += adj


class Stock_Cache_Entry(models.Model):
    """A stock cache entry lists all part counts of all warehouses as of a
    given point in time.  In contrast to inventories, such entrys are
    automatically created as needed and deleted whenever a delta
    changes that could affect the entry.

    """

    ts = models.DateTimeField(
        verbose_name="Creation Time",
        help_text="Date and time when this transaction was created.",
    )

    class Meta:
        ordering = ["-ts"]
        indexes = [models.Index(fields=["ts"])]

    @classmethod
    def invalidate(cls, ts=None):
        """Invalidate all stock cache entries that are not older than the
        specified timestamp.  All entries are invalidated if the
        timestamp is None.

        """
        Stock_Cache_Entry.objects.filter(ts__gte=ts).delete()

    def __str__(self):
        return "Stock_Cache_Entry %u" % self.id

    def inventory(self):
        inv = Part_Inventory(ts=self.ts)
        qs = Stock_Cache_Item.objects.filter(stock_cache_entry_id=self.id)
        for item in qs:
            entry = inv.get_entry(item.warehouse.id, item.part.id)
            entry.qty = item.qty
        return inv

    def save(self, *args, **kwargs):
        inventory = None
        if "inventory" in kwargs:
            inventory = kwargs["inventory"]
            kwargs.pop("inventory")
            self.ts = inventory.ts

        super().save(*args, **kwargs)

        # Save part counts in Stock_Cache_Item:
        if inventory is not None:
            for warehouse in inventory.warehouse:
                for part_id in inventory.warehouse[warehouse]:
                    qty = inventory.warehouse[warehouse][part_id].qty
                    if qty != 0:
                        item = Stock_Cache_Item(
                            stock_cache_entry=self,
                            warehouse_id=warehouse,
                            part_id=part_id,
                            qty=qty,
                        )
                        item.save()


class Stock_Cache_Item(models.Model):
    stock_cache_entry = models.ForeignKey(
        Stock_Cache_Entry, on_delete=models.CASCADE
    )
    warehouse = models.ForeignKey(
        Warehouse,
        verbose_name="Warehouse",
        help_text="The warehouse stocking this part.",
        on_delete=models.PROTECT,
    )
    part = models.ForeignKey(
        Part, verbose_name="Part #", on_delete=models.PROTECT
    )
    qty = models.IntegerField(help_text="The quantity of this part.")

    class Meta:
        indexes = [models.Index(fields=["stock_cache_entry"])]

    def __str__(self):
        return "Stock_Cache_Item[%s]: %s*%s" % (
            self.warehouse.name,
            format_part_number(self.part.id),
            self.qty,
        )
