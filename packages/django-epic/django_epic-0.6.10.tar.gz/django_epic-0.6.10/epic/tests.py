#
#   Copyright (c) 2014-2015, 2018, 2021, 2024-2025 eGauge Systems LLC
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
# pylint: disable=invalid-name
"""Unit tests.  Run, e.g., from epic-sample with:

python3 manage.py test epic.tests
"""

import io
import os
import re
from datetime import datetime, timedelta
from datetime import timezone as tz
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth import models as auth_models
from django.test import TestCase
from django.urls import URLPattern, reverse
from django.utils import timezone

import epic
from epic import perms, urls
from epic.base import Enum
from epic.lib import get_stock
from epic.models import (
    Assembly_Item,
    Delta,
    Inventory,
    Line_Item,
    Order,
    Part,
    Shipment,
    Vendor,
    Vendor_Part,
    Warehouse,
)


def mktime(time_string):
    dt = datetime.strptime(time_string, "%b %d %Y %I:%M%p")
    return timezone.make_aware(dt, tz.utc)


class URL_Iterator:
    def __init__(self, urlpatterns):
        self.urlpattern_iterator = urlpatterns.__iter__()

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            pat = self.urlpattern_iterator.__next__()
            if isinstance(pat, URLPattern):
                break
        regex = re.compile(pat.pattern._regex)  # NOQA
        args = {}
        for key in regex.groupindex.keys():
            args[key] = 1
        url = reverse("epic:%s" % pat.name, kwargs=args)
        return url, pat.name


def create_part(pk):
    return Part(
        pk=pk,
        mfg="mfg",
        mfg_pn="mfg_pn%d" % pk,
        mounting=Enum.MOUNTING_SMD,
        target_price=1,
        overage=0,
        spq=1,
        status=Enum.STATUS_ACTIVE,
        lead_time=9,
    )


def create_warehouse(pk, name):
    return Warehouse(pk=pk, name=name)


def create_vendor(pk, name):
    return Vendor(pk=pk, name=name)


def create_vendor_part(part_id, vendor_id, vendor_pn, price):
    return Vendor_Part(
        part_id=part_id, vendor_id=vendor_id, vendor_pn=vendor_pn, price=price
    )


def create_order(pk, vendor_id, warehouse_id):
    now = timezone.now()
    then = now + timedelta(days=30)
    return Order(
        pk=pk,
        ts=now,
        warehouse_id=warehouse_id,
        expected_arrival_date=then,
        status=Enum.TXTN_STATUS_OPEN,
        vendor_id=vendor_id,
    )


def create_ship(
    pk,
    order_id,
    warehouse_id,
    tracking="1Z9AA10123456784",
    cost_freight=0,
    cost_other=0,
    cost_discount=0,
):
    return Shipment(
        pk=pk,
        ts=timezone.now(),
        tracking=tracking,
        ordr_id=order_id,
        warehouse_id=warehouse_id,
        cost_freight=cost_freight,
        cost_other=cost_other,
        cost_discount=cost_discount,
    )


def create_inventory(pk, warehouse_id):
    return Inventory(pk=pk, ts=timezone.now(), warehouse_id=warehouse_id)


def create_assembly_item(assy_id=None, comp_id=None, qty=1):
    return Assembly_Item(assy_id=assy_id, comp_id=comp_id, qty=qty)


def create_line_item(txtn_id, part_id, qty, line_cost, index):
    return Line_Item(
        txtn_id=txtn_id,
        part_id=part_id,
        qty=qty,
        line_cost=line_cost,
        index=index,
    )


class Stock_Cache_Tests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.p = []  # parts
        cls.w = []  # warehouses
        cls.v = []  # vendors

        for i in range(10):
            p = create_part(i)
            p.save()
            cls.p.append(p)

        for i in range(3):
            w = create_warehouse(i, "Warehouse%d" % i)
            w.save()
            cls.w.append(w)

        for i in range(5):
            v = create_vendor(i, "Vendor%d" % i)
            v.save()
            cls.v.append(v)

    def assertInventory(self, inv, expected):
        for w in inv.warehouse:
            if w not in expected:
                self.fail("Warehouse %d unexpectedly in inventory." % w)
            else:
                for p in inv.warehouse[w]:
                    if p not in expected[w]:
                        self.fail(
                            "Warehouse %d: part %d unexpectedly in "
                            "inventory." % (w, p)
                        )
                    else:
                        if inv.warehouse[w][p].qty != expected[w][p]:
                            self.fail(
                                "Warehouse %d, part %d: wrong qty %d; "
                                "expected %d!"
                                % (
                                    w,
                                    p,
                                    inv.warehouse[w][p].qty,
                                    expected[w][p],
                                )
                            )

                for p in expected[w]:
                    if p not in inv.warehouse[w]:
                        self.fail(
                            "Warehouse %d: part %d missing from "
                            "inventory." % (w, p)
                        )

        for w in expected:
            if w not in inv.warehouse:
                self.fail("Warehouse %d missing from inventory." % w)

    def test_basic(self):
        inv0 = create_inventory(0, 0)
        inv0.ts = mktime("Jan 1 2010 4:00pm")
        inv0.save()
        inv0.finalize()

        d = Delta(
            part=self.__class__.p[0],
            is_absolute=True,
            adj=10,
            txtn=inv0,
            warehouse=self.__class__.w[0],
        )
        d.save()
        d = Delta(
            part=self.__class__.p[5],
            is_absolute=True,
            adj=20,
            txtn=inv0,
            warehouse=self.__class__.w[0],
        )
        d.save()
        d = Delta(
            part=self.__class__.p[3],
            is_absolute=True,
            adj=1000,
            txtn=inv0,
            warehouse=self.__class__.w[2],
        )
        d.save()

        inv = get_stock()
        self.assertInventory(inv, {0: {0: 10, 5: 20}, 2: {3: 1000}})

        inv = get_stock(warehouses=[0])
        self.assertInventory(inv, {0: {0: 10, 5: 20}})

        inv = get_stock(warehouses=[1])
        self.assertInventory(inv, {})

        inv = get_stock(warehouses=[2])
        self.assertInventory(inv, {2: {3: 1000}})

        inv = get_stock(exclude_txtn_id=inv0.id)
        self.assertInventory(inv, {})

        inv = get_stock(as_of_ts=mktime("Jan 1 2010 3:59pm"))
        self.assertInventory(inv, {})
        inv = get_stock(as_of_date=mktime("Jan 1 2010 5:00pm"))
        self.assertInventory(inv, {})

    def test_shipment_timestamp_change(self):
        """Test shipment that moves between timestamps."""
        o = create_order(pk=0, vendor_id=0, warehouse_id=0)
        o.save()
        o.finalize()
        s = create_ship(pk=1, order_id=o.id, warehouse_id=0)
        s.ts = mktime("Jan 1 2010 4:00pm")
        s.save()
        l = create_line_item(
            txtn_id=s.id, part_id=1, qty=2, line_cost="2", index=1
        )
        l.save()
        s.finalize()

        inv = get_stock(as_of_date=mktime("Jan 1 2015 5:00pm"))
        self.assertInventory(inv, {0: {1: 2}})
        inv = get_stock(as_of_date=mktime("Jan 1 2001 5:00pm"))
        self.assertInventory(inv, {})

        s.ts = mktime("Jan 1 2017 5:00pm")
        s.save()
        s.finalize()

        inv = get_stock(as_of_date=mktime("Jan 1 2015 5:00pm"))
        self.assertInventory(inv, {})
        inv = get_stock(as_of_date=mktime("Jan 1 2001 5:00pm"))
        self.assertInventory(inv, {})

        s.ts = mktime("Jan 1 2010 4:00pm")
        s.save()
        s.finalize()

        inv = get_stock(as_of_date=mktime("Jan 1 2015 5:00pm"))
        self.assertInventory(inv, {0: {1: 2}})
        inv = get_stock(as_of_date=mktime("Jan 1 2001 5:00pm"))
        self.assertInventory(inv, {})

    def test_inventory_timestamp_change(self):
        """Test inventory that moves between timestamps."""
        inv0 = create_inventory(0, 0)
        inv0.ts = mktime("Jan 1 2010 4:00pm")
        inv0.save()
        inv0.finalize()

        d = Delta(
            part=self.__class__.p[0],
            is_absolute=True,
            adj=10,
            txtn=inv0,
            warehouse=self.__class__.w[0],
        )
        d.save()
        d = Delta(
            part=self.__class__.p[5],
            is_absolute=True,
            adj=20,
            txtn=inv0,
            warehouse=self.__class__.w[0],
        )
        d.save()
        d = Delta(
            part=self.__class__.p[3],
            is_absolute=True,
            adj=1000,
            txtn=inv0,
            warehouse=self.__class__.w[2],
        )
        d.save()

        inv = get_stock(as_of_date=mktime("Jan 1 2015 5:00pm"))
        self.assertInventory(inv, {0: {0: 10, 5: 20}, 2: {3: 1000}})
        inv = get_stock(as_of_date=mktime("Jan 1 2001 5:00pm"))
        self.assertInventory(inv, {})

        inv0.ts = mktime("Jan 1 2017 5:00pm")
        inv0.save()
        inv0.finalize()

        inv = get_stock(as_of_date=mktime("Jan 1 2015 5:00pm"))
        self.assertInventory(inv, {})
        inv = get_stock(as_of_date=mktime("Jan 1 2001 5:00pm"))
        self.assertInventory(inv, {})

        inv0.ts = mktime("Jan 1 2010 4:00pm")
        inv0.save()
        inv0.finalize()

        inv = get_stock(as_of_date=mktime("Jan 1 2015 5:00pm"))
        self.assertInventory(inv, {0: {0: 10, 5: 20}, 2: {3: 1000}})
        inv = get_stock(as_of_date=mktime("Jan 1 2001 5:00pm"))
        self.assertInventory(inv, {})

    def test_warehouse_delete(self):
        """Test warehouse delete effect on stock cache."""
        item = create_assembly_item(assy_id=3, comp_id=1, qty=10)
        item.save()

        inv0 = create_inventory(pk=0, warehouse_id=2)
        inv0.ts = mktime("Jan 1 2010 4:00pm")
        inv0.save()
        inv0.finalize()

        d = Delta(
            part=self.__class__.p[0],
            is_absolute=True,
            adj=10,
            txtn=inv0,
            warehouse=self.__class__.w[0],
        )
        d.save()
        d = Delta(
            part=self.__class__.p[5],
            is_absolute=True,
            adj=20,
            txtn=inv0,
            warehouse=self.__class__.w[0],
        )
        d.save()
        d = Delta(
            part=self.__class__.p[3],
            is_absolute=True,
            adj=1000,
            txtn=inv0,
            warehouse=self.__class__.w[2],
        )
        d.save()

        inv = get_stock()
        self.assertInventory(inv, {0: {0: 10, 5: 20}, 2: {3: 1000}})

        Delta.objects.filter(pk__lte=2).delete()
        Warehouse.objects.filter(pk=0).delete()

        inv = get_stock()
        self.assertInventory(inv, {2: {3: 1000}})


class Part_Method_Tests(TestCase):
    def test_is_orderable(self):
        p = Part(status=Enum.STATUS_PREVIEW)
        self.assertEqual(p.is_orderable(), False)

        p = Part(status=Enum.STATUS_ACTIVE)
        self.assertEqual(p.is_orderable(), True)

        p = Part(status=Enum.STATUS_DEPRECATED)
        self.assertEqual(p.is_orderable(), True)

        p = Part(status=Enum.STATUS_OBSOLETE)
        self.assertEqual(p.is_orderable(), False)

    def test_equivalent_parts(self):
        p1 = create_part(1)
        p1.save()
        p2 = create_part(2)
        p2.save()

        self.assertEqual(p1.equivalent_parts(), [p1])

        p1.substitute = p2
        p1.save()
        p2.save()
        self.assertEqual(p1.equivalent_parts(), [p1, p2])
        self.assertEqual(p2.equivalent_parts(), [p1, p2])

        p3 = create_part(3)
        p3.substitute = p2
        p3.save()
        self.assertEqual(p1.equivalent_parts(), [p1, p2, p3])
        self.assertEqual(p2.equivalent_parts(), [p1, p2, p3])
        self.assertEqual(p3.equivalent_parts(), [p1, p2, p3])

        p1.substitute = None
        p1.save()
        self.assertEqual(p1.equivalent_parts(), [p1])
        self.assertEqual(p2.equivalent_parts(), [p2, p3])
        self.assertEqual(p3.equivalent_parts(), [p2, p3])

        p3.delete()
        p1.delete()
        p2.delete()

    def test_best_parts(self):
        p1 = create_part(1)
        p1.status = Enum.STATUS_PREFERRED
        p1.save()

        p2 = create_part(2)
        p2.status = Enum.STATUS_PREFERRED
        p2.substitute = p1
        p2.save()

        # p1 has lower ID so it should be preferred:
        self.assertEqual(p1.best_part(), p1)
        self.assertEqual(p2.best_part(), p1)

        p2.target_price = p1.target_price - 1
        p2.save()

        # p2 has lower price so it should be preferred:
        self.assertEqual(p1.best_part(), p2)
        self.assertEqual(p2.best_part(), p2)

        p2.status = Enum.STATUS_ACTIVE
        p2.save()
        # p1 is preferred, even though it's higher price
        self.assertEqual(p1.best_part(), p1)
        self.assertEqual(p2.best_part(), p1)

        p1.status = Enum.STATUS_ACTIVE
        p1.save()
        # now p2 should win again due to lower price:
        self.assertEqual(p1.best_part(), p2)
        self.assertEqual(p2.best_part(), p2)

    def test_avg_cost(self):
        part = []
        for i in range(3):
            p = create_part(i)
            if i == 1:
                p.substitute = part[0]
            p.save()
            part.append(p)

        for i in range(3):
            w = create_warehouse(i, "Warehouse%d" % i)
            w.save()

        for i in range(5):
            v = create_vendor(i, "Vendor%d" % i)
            v.save()

        # create shipment with:
        # 	part 1 cost average = $1
        # 	part 2 cost average = $0.001
        o = create_order(pk=0, vendor_id=0, warehouse_id=0)
        o.save()
        o.finalize()
        s = create_ship(pk=1, order_id=o.id, warehouse_id=0)
        s.save()
        l = create_line_item(
            txtn_id=s.id, part_id=0, qty=1, line_cost="3", index=1
        )
        l.save()
        l = create_line_item(
            txtn_id=s.id, part_id=1, qty=1, line_cost="1", index=2
        )
        l.save()
        l = create_line_item(
            txtn_id=s.id, part_id=2, qty=1000, line_cost="1", index=3
        )
        l.save()
        s.finalize()

        # Create shipment over a year ago.  It should not affect average prices
        o = create_order(pk=2, vendor_id=0, warehouse_id=0)
        o.save()
        o.finalize()
        s = create_ship(pk=3, order_id=o.id, warehouse_id=0)
        s.ts = timezone.now() - timedelta(days=365)
        s.save()
        l = create_line_item(
            txtn_id=s.id, part_id=1, qty=1, line_cost="1000", index=1
        )
        l.save()
        l = create_line_item(
            txtn_id=s.id, part_id=2, qty=1, line_cost="1000", index=2
        )
        l.save()
        s.finalize()

        p = Part.objects.get(pk=0)
        self.assertEqual(p.avg_cost(), Decimal("2.000"))

        p = Part.objects.get(pk=1)
        self.assertEqual(p.avg_cost(), Decimal("2.000"))

        p = Part.objects.get(pk=2)
        self.assertEqual(p.avg_cost(), Decimal("0.001"))


class Vendor_Part_Method_Tests(TestCase):
    def test_html_link(self):
        v = Vendor(search_url="")

        p = Part()
        vp = Vendor_Part(vendor_pn="VP001", part=p, vendor=v)

        # empty_url patterns should yield the escaped vendor_pn:
        self.assertEqual(vp.html_link(), "VP001")

        # pattern causing KeyError should yield the escaped vendor_pn:
        v.search_url = "%(bogus)"
        self.assertEqual(vp.html_link(), "VP001")

        # pattern causing TypeError should yield the escaped vendor_pn:
        v.search_url = "%(vendor_pn)-cpn.html"
        self.assertEqual(vp.html_link(), "VP001")

        # pattern causing ValueError should yield the escaped vendor_pn:
        v.search_url = "%(vendor_pn)"
        self.assertEqual(vp.html_link(), "VP001")

        # valid pattern should be expanded:
        v.search_url = "https://host/%(vendor_pn)s.html"
        self.assertEqual(
            vp.html_link(),
            '<a href="https://host/VP001.html" target="part_lookup">VP001</a>'
        )


class Access_Tests(TestCase):
    @classmethod
    def setup_part(cls):
        p1 = create_part(1)
        p1.save()
        ai = create_assembly_item(assy_id=1, comp_id=2, qty=3)
        ai.refdes = "R1,R2,R3"
        ai.save()
        p = create_vendor_part(1, 2, "ASSY_HOUSE_VENDOR_PART_#1", 325.654321)
        p.save()

    @classmethod
    def setup_vendor(cls):
        v = create_vendor(1, "Vendor #1")
        v.save()
        p = create_vendor_part(1, 1, "VENDOR_PART_#1", 535.123456)
        p.save()

    @classmethod
    def setup_warehouse(cls):
        w = create_warehouse(1, "Warehouse #1")
        w.save()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        perms.add_custom_permissions(auth_models)
        u = get_user_model().objects.create_user(
            "test", "test@magic.com", "magic"
        )
        u.user_permissions.set([perms.VIEW_PERM, perms.EDIT_PERM])

        p2 = create_part(2)
        p2.save()

        p3 = create_part(3)
        p3.save()

        w = create_warehouse(2, "Assyhouse #1")
        w.save()
        v = create_vendor(2, "Assyhouse #1")
        v.save()

        Access_Tests.setup_part()
        Access_Tests.setup_vendor()
        Access_Tests.setup_warehouse()

    # def test_redirect_to_https(self):
    #     url = reverse('epic:epic_index')
    #     response = self.client.get(url, secure=False)
    #     self.assertEqual(response.status_code, 301)
    #     self.assertIsNotNone(re.match('https://', response.url))

    def test_unauthenticated_accesses(self):
        response = self.client.get(
            reverse("epic:part_info") + "?pid=1", secure=True
        )
        self.assertEqual(response.status_code, 302)

        for url, _ in URL_Iterator(urls.urlpatterns):
            m = re.match(r"/epic/dal/", url)
            # auto-completion URLs respond with 403 (Forbidden)
            # others return redirect to login page:
            if m:
                expected = 403
            else:
                expected = 302
            response = self.client.get(url, secure=True)
            if response.status_code != expected:
                print(
                    "Unauthenticated access to %s returned %s, expected %s"
                    % (url, response.status_code, expected)
                )
            self.assertEqual(response.status_code, expected)

    def test_authenticated_accesses(self):
        self.client.login(username="test", password="magic")

        for url, pattern_name in URL_Iterator(urls.urlpatterns):
            if re.match("order_", pattern_name):
                # order part 1 (an assembly) from vendor 'Assyhouse #1'
                o = create_order(1, 2, 1)
                o.save()
                l = create_line_item(1, 1, qty=13, line_cost="15.95", index=1)
                l.save()
            elif re.match("ship_", pattern_name):
                # order part 1(an assembly) from vendor 'Assyhouse #1'
                o = create_order(2, 2, 1)
                o.save()
                l = create_line_item(2, 1, qty=13, line_cost="15.95", index=1)
                l.save()
                s = create_ship(1, 2, 1, "1234,5678", 1.1, 2.2, 3.3)
                s.save()
                l = create_line_item(1, 1, qty=2, line_cost="2", index=1)
                l.save()
            elif re.match("warehouse_inventory_", pattern_name):
                i = create_inventory(1, 1)
                i.save()

            expect = 200
            expect_url = None
            post_action = []
            if pattern_name == "search_results":
                url += "?q=1"
                # with a unique result, search redirects to the detail page:
                expect = 302
                expect_url = reverse("epic:part_detail", kwargs={"pk": 1})
            elif pattern_name == "part_delete":
                expect = 302
                expect_url = reverse("epic:part_list")
                post_action.append(Access_Tests.setup_part)
            elif pattern_name == "ship_delete":
                expect = 302
                expect_url = reverse("epic:ship_list")
            elif pattern_name == "vendor_delete":
                expect = 302
                expect_url = reverse("epic:vendor_list")
                post_action.append(Access_Tests.setup_vendor)
            elif pattern_name == "warehouse_delete":
                expect = 302
                expect_url = reverse("epic:warehouse_list")
                post_action.append(Access_Tests.setup_warehouse)
            elif pattern_name == "warehouse_inventory_delete":
                expect = 302
                expect_url = reverse("epic:warehouse_detail", kwargs={"pk": 1})
            elif pattern_name == "order_delete":
                expect = 302
                expect_url = reverse("epic:order_list")
            elif pattern_name in [
                "datasheet_add_part",
                "datasheet_detail",
                "datasheet_edit",
                "datasheet_delete",
            ]:
                continue

            response = self.client.get(url, secure=True)

            # we can't only have one transaction with pk=1...
            Shipment.objects.all().delete()
            Order.objects.all().delete()
            Inventory.objects.all().delete()

            if response.status_code != expect:
                print("access to %s failed" % url)
                if hasattr(response, "url"):
                    print(" redirect URL: %s" % response.url)
            self.assertEqual(response.status_code, expect)
            if expect_url is not None:
                url = response.url
                if url[-1] == "/":
                    url = url[:-1]
                self.assertEqual(url, expect_url)

            for action in post_action:
                action()

    def test_form_upload(self):
        self.client.login(username="test", password="magic")

        # Verify that we can post item formset to an order:
        response = self.client.post(
            "/epic/order/add",
            {
                "ts": "2018-08-06",
                "vendor": 1,
                "warehouse": 2,
                "expected_arrival_date": "2018-08-06",
                "notes": "This is a note",
                "line_item_set-TOTAL_FORMS": 12,
                "line_item_set-INITIAL_FORMS": 0,
                "line_item_set-MIN_NUM_FORMS": 0,
                "line_item_set-MAX_NUM_FORMS": 1000,
                "line_item_set-0-qty": 8,
                "line_item_set-0-part": 3,
                "line_item_set-0-vendor_pn": "VPN #1",
                "line_item_set-0-part_cost": 1,
                "line_item_set-0-line_cost": 120,
                "line_item_set-1-qty": 18,
                "line_item_set-1-part": 2,
                "line_item_set-1-vendor_pn": "VPN #2",
                "line_item_set-1-part_cost": 1,
                "line_item_set-1-line_cost": 121,
            },
        )

        # response.request['wsgi.input']._FakePayload__content.seek(0)
        # print('REQUEST',
        #       response.request['wsgi.input']._FakePayload__content.read()
        #       .decode('utf-8'))
        if response.status_code != 302:
            for name in response.context.keys():
                if re.match(r"[^_]+_form$", name):
                    print("%s.errors:" % name, response.context[name].errors)

        self.assertEqual(response.status_code, 302)
        order = Order.objects.all()[0]
        line_items = Line_Item.objects.filter(txtn=order)
        self.assertEqual(line_items[0].qty, 8)
        self.assertEqual(line_items[0].part.id, 3)
        self.assertEqual(line_items[0].line_cost, 120)
        self.assertEqual(line_items[1].qty, 18)
        self.assertEqual(line_items[1].part.id, 2)
        self.assertEqual(line_items[1].line_cost, 121)

        # Verify that we can post an item formset to a shipment:
        response = self.client.post(
            "/epic/order/%d/add-shipment" % order.id,
            {
                "ts": "2018-08-06",
                "cost_freight": 10.0,
                "cost_other": 3.14,
                "cost_discount": 2.74,
                "vendor": 1,
                "warehouse": 2,
                "expected_arrival_date": "2018-08-06",
                "notes": "note 2",
                "line_item_set-TOTAL_FORMS": 12,
                "line_item_set-INITIAL_FORMS": 0,
                "line_item_set-MIN_NUM_FORMS": 0,
                "line_item_set-MAX_NUM_FORMS": 1000,
                "line_item_set-0-qty": 7,
                "line_item_set-0-part": 3,
                "line_item_set-0-vendor_pn": "VPN #1",
                "line_item_set-0-part_cost": 1,
                "line_item_set-0-line_cost": 120,
                "line_item_set-1-qty": 17,
                "line_item_set-1-part": 2,
                "line_item_set-1-vendor_pn": "VPN #2",
                "line_item_set-1-part_cost": 1,
                "line_item_set-1-line_cost": 121,
            },
        )
        self.assertEqual(response.status_code, 302)
        ship = Shipment.objects.all()[0]
        line_items = Line_Item.objects.filter(txtn=ship)
        self.assertEqual(line_items[0].qty, 7)
        self.assertEqual(line_items[0].part.id, 3)
        self.assertEqual(line_items[0].line_cost, 120)
        self.assertEqual(line_items[1].qty, 17)
        self.assertEqual(line_items[1].part.id, 2)
        self.assertEqual(line_items[1].line_cost, 121)

        # Verify that we can post a delta formset as an inventory:
        response = self.client.post(
            "/epic/warehouse/1/add-inventory",
            {
                "ts": "2018-08-06 08:15 AM",
                "notes": "Note #3",
                "delta_set-TOTAL_FORMS": 12,
                "delta_set-INITIAL_FORMS": 0,
                "delta_set-MIN_NUM_FORMS": 0,
                "delta_set-MAX_NUM_FORMS": 1000,
                "delta_set-0-adj": 6,
                "delta_set-0-part": 2,
                "delta_set-0-vendor_pn": "VPN #2",
                "delta_set-0-part_cost": 1,
                "delta_set-0-line_cost": 120,
                "delta_set-1-adj": 16,
                "delta_set-1-part": 3,
                "delta_set-1-vendor_pn": "VPN #3",
                "delta_set-1-part_cost": 1,
                "delta_set-1-line_cost": 121,
            },
        )
        self.assertEqual(response.status_code, 302)
        inv = Inventory.objects.all()[0]
        line_items = Delta.objects.filter(txtn=inv)
        self.assertEqual(line_items[0].part.id, 2)
        self.assertEqual(line_items[0].is_absolute, True)
        self.assertEqual(line_items[0].adj, 6)
        self.assertEqual(line_items[0].warehouse.id, 1)
        self.assertEqual(line_items[1].part.id, 3)
        self.assertEqual(line_items[1].is_absolute, True)
        self.assertEqual(line_items[1].adj, 16)
        self.assertEqual(line_items[1].warehouse.id, 1)

    def test_spreadsheet_upload(self):
        self.client.login(username="test", password="magic")

        # Verify invalid column names yield the expected errors:
        response = self.client.post(
            "/epic/order/add",
            {
                "ts": "2018-08-06",
                "vendor": 1,
                "warehouse": 2,
                "expected_arrival_date": "2018-08-06",
                "notes": "This is a note",
                "spreadsheet": io.BytesIO(
                    b"qty1,part1,extra,amount1\n10,3,5,99\n40,EP0002,,10\n"
                ),
                "line_item_set-TOTAL_FORMS": 0,
                "line_item_set-INITIAL_FORMS": 0,
            },
        )
        self.assertContains(
            response,
            "<strong>Column &quot;qty&quot; missing.  It may also be "
            "called one of: quantity, count.</strong></span> "
            '<span id="error_2_id_spreadsheet" class="help-block">'
            "<strong>Column &quot;part&quot; missing.  It may also be "
            "called one of: pn, ep.</strong></span> "
            '<span id="error_3_id_spreadsheet" class="help-block">'
            "<strong>Column &quot;amount&quot; missing.  It may also be "
            "called one of: cost, price.</strong>",
        )

        # Verify that we can post a CSV file to an order:
        response = self.client.post(
            "/epic/order/add",
            {
                "ts": "2018-08-06",
                "vendor": 1,
                "warehouse": 2,
                "expected_arrival_date": "2018-08-06",
                "notes": "This is a note",
                "spreadsheet": io.BytesIO(
                    b"qty,part,extra,amount\n10,3,5,99\n40,EP0002,,10\n"
                ),
                "line_item_set-TOTAL_FORMS": 0,
                "line_item_set-INITIAL_FORMS": 0,
            },
        )
        self.assertEqual(response.status_code, 302)
        order = Order.objects.all()[0]
        line_items = Line_Item.objects.filter(txtn=order)
        self.assertEqual(line_items[0].qty, 10)
        self.assertEqual(line_items[0].part.id, 3)
        self.assertEqual(line_items[0].line_cost, 99)
        self.assertEqual(line_items[1].qty, 40)
        self.assertEqual(line_items[1].part.id, 2)
        self.assertEqual(line_items[1].line_cost, 10)

        # Verify that we can post a CSV file to a shipment:
        response = self.client.post(
            "/epic/order/%d/add-shipment" % order.id,
            {
                "ts": "2018-08-06",
                "cost_freight": 10.0,
                "cost_other": 3.14,
                "cost_discount": 2.74,
                "vendor": 1,
                "warehouse": 2,
                "expected_arrival_date": "2018-08-06",
                "notes": "note 2",
                "spreadsheet": io.BytesIO(
                    b"qty,part,extra,amount\n5,3,5,99\n10,EP0002,,10\n"
                ),
            },
        )
        self.assertEqual(response.status_code, 302)
        ship = Shipment.objects.all()[0]
        line_items = Line_Item.objects.filter(txtn=ship)
        self.assertEqual(line_items[0].qty, 5)
        self.assertEqual(line_items[0].part.id, 3)
        self.assertEqual(line_items[0].line_cost, 99)
        self.assertEqual(line_items[1].qty, 10)
        self.assertEqual(line_items[1].part.id, 2)
        self.assertEqual(line_items[1].line_cost, 10)

        # Verify that we can post an Excel file as an inventory:
        excel_file = os.path.join(
            os.path.dirname(epic.__file__), "test-data", "inventory.xlsx"
        )
        with open(excel_file, "rb") as f:
            response = self.client.post(
                "/epic/warehouse/1/add-inventory",
                {"ts": "2018-08-06 08:15 AM", "spreadsheet": f},
            )
        self.assertEqual(response.status_code, 302)
        inv = Inventory.objects.all()[0]
        line_items = Delta.objects.filter(txtn=inv)
        self.assertEqual(line_items[0].part.id, 2)
        self.assertEqual(line_items[0].is_absolute, True)
        self.assertEqual(line_items[0].adj, 1234)
        self.assertEqual(line_items[0].warehouse.id, 1)
        self.assertEqual(line_items[1].part.id, 3)
        self.assertEqual(line_items[1].is_absolute, True)
        self.assertEqual(line_items[1].adj, 5678)
        self.assertEqual(line_items[1].warehouse.id, 1)

    def test_order_status(self):
        """Confirm that deleting a shipment for completed order will mark
        order as OPEN again.

        """
        self.client.login(username="test", password="magic")
        # create order from Vendor #1:
        o = create_order(pk=4, vendor_id=1, warehouse_id=1)
        o.save()
        l = create_line_item(o.pk, 2, qty=1000, line_cost="256.35", index=1)
        l.save()

        # order should be open now
        self.assertEqual(o.status, Enum.TXTN_STATUS_OPEN)

        # create two shipments that should complete the order:
        s = create_ship(2, o.pk, 1, "1Z1345", 1.23, 2.34, 3.45)
        s.save()
        l = create_line_item(s.pk, 2, 900, line_cost="230.05", index=1)
        l.save()

        s = create_ship(3, o.pk, 1, "1Z1356", 1.23, 2.34, 3.45)
        s.save()
        l = create_line_item(s.pk, 2, 100, line_cost="230.05", index=1)
        l.save()

        s.finalize()

        # order should be closed now:
        o = Order.objects.get(pk=4)
        self.assertEqual(o.status, Enum.TXTN_STATUS_CLOSED)

        # delete the first shipment:
        url = reverse("epic:ship_delete", kwargs={"pk": 2})
        response = self.client.get(url, secure=True)
        self.assertEqual(response.status_code, 302)

        # order should be open again:
        o = Order.objects.get(pk=4)
        self.assertEqual(o.status, Enum.TXTN_STATUS_OPEN)
