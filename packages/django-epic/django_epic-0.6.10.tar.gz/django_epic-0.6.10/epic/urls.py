#
#   Copyright (c) 2014-2016, 2018, 2021-2022 eGauge Systems LLC
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
from django.urls import include, re_path

from epic import exports, views

urlpatterns = [
    re_path(r"^$", views.epic_index, name="epic_index"),
    re_path(r"^search-results$", views.search_results, name="search_results"),
    re_path(r"^api/", include("epic.api.urls")),
    re_path(r"^part/?$", views.part_list, name="part_list"),
    re_path(r"^part/add$", views.part_add, name="part_add"),
    re_path(r"^part/info$", views.part_info, name="part_info"),
    re_path(r"^part/(?P<pk>\d+)/?$", views.part_detail, name="part_detail"),
    re_path(r"^part/(?P<pk>\d+)/edit$", views.part_edit, name="part_edit"),
    re_path(
        r"^part/(?P<pk>\d+)/delete$", views.part_delete, name="part_delete"
    ),
    re_path(
        r"^part/(?P<pk>\d+)/bom/?$",
        views.part_bom_detail,
        name="part_bom_detail",
    ),
    re_path(
        r"^part/(?P<pk>\d+)/bom/edit$",
        views.part_bom_edit,
        name="part_bom_edit",
    ),
    re_path(
        r"^part/(?P<pk>\d+)/bom/export$",
        exports.part_bom_export,
        name="part_bom_export",
    ),
    re_path(
        r"^part/(?P<pk>\d+)/bom/compare/?$",
        views.part_bom_compare,
        name="part_bom_compare",
    ),
    re_path(
        r"^part/(?P<pk>\d+)/bom/compare/(?P<other_pk>\d+)/?$",
        views.part_bom_compare_qty,
        name="part_bom_compare_qty",
    ),
    re_path(
        r"^part/(?P<pk>\d+)/bom/compare/(?P<other_pk>\d+)/refdes$",
        views.part_bom_compare_refdes,
        name="part_bom_compare_refdes",
    ),
    re_path(
        r"^part/datasheet/?$", views.datasheet_list, name="datasheet_list"
    ),
    re_path(
        r"^part/datasheet/add$", views.datasheet_add, name="datasheet_add"
    ),
    re_path(
        r"^part/datasheet/add/(?P<pk>\d+)$",
        views.datasheet_add_part,
        name="datasheet_add_part",
    ),
    re_path(
        r"^part/datasheet/(?P<pk>\d+)/?$",
        views.datasheet_detail,
        name="datasheet_detail",
    ),
    re_path(
        r"^part/datasheet/(?P<pk>\d+)/edit$",
        views.datasheet_edit,
        name="datasheet_edit",
    ),
    re_path(
        r"^part/datasheet/(?P<pk>\d+)/delete$",
        views.datasheet_delete,
        name="datasheet_delete",
    ),
    re_path(r"^vendor/?$", views.vendor_list, name="vendor_list"),
    re_path(r"^vendor/add$", views.vendor_add, name="vendor_add"),
    re_path(
        r"^vendor/(?P<pk>\d+)/?$", views.vendor_detail, name="vendor_detail"
    ),
    re_path(
        r"^vendor/(?P<pk>\d+)/edit$", views.vendor_edit, name="vendor_edit"
    ),
    re_path(
        r"^vendor/(?P<pk>\d+)/delete$",
        views.vendor_delete,
        name="vendor_delete",
    ),
    re_path(r"^warehouse/?$", views.warehouse_list, name="warehouse_list"),
    re_path(
        r"^warehouse/stock$",
        views.warehouse_stock_all,
        name="warehouse_stock_all",
    ),
    re_path(
        r"^warehouse/stock/export$",
        exports.warehouse_stock_all_export,
        name="warehouse_stock_all_export",
    ),
    re_path(r"^warehouse/add$", views.warehouse_add, name="warehouse_add"),
    re_path(
        r"^warehouse/(?P<pk>\d+)/?$",
        views.warehouse_detail,
        name="warehouse_detail",
    ),
    # this is simply an alias since the warehouse_detail already lists
    # the inventories associated with that warehouse:
    re_path(
        r"^warehouse/(?P<pk>\d+)/inventory/?$",
        views.warehouse_inventory,
        name="warehouse_inventory",
    ),
    re_path(
        r"^warehouse/(?P<pk>\d+)/edit$",
        views.warehouse_edit,
        name="warehouse_edit",
    ),
    re_path(
        r"^warehouse/(?P<pk>\d+)/add-shipment$",
        views.warehouse_add_shipment,
        name="warehouse_add_shipment",
    ),
    re_path(
        r"^warehouse/(?P<pk>\d+)/add-inventory$",
        views.warehouse_add_inventory,
        name="warehouse_add_inventory",
    ),
    re_path(
        r"^warehouse/(?P<pk>\d+)/stock$",
        views.warehouse_stock,
        name="warehouse_stock",
    ),
    re_path(
        r"^warehouse/(?P<pk>\d+)/stock/export$",
        exports.warehouse_stock_export,
        name="warehouse_stock_export",
    ),
    re_path(
        r"^warehouse/(?P<pk>\d+)/delete$",
        views.warehouse_delete,
        name="warehouse_delete",
    ),
    re_path(
        r"^warehouse/(?P<warehouse>\d+)/inventory/(?P<pk>\d+)/?$",
        views.warehouse_inv_detail,
        name="warehouse_inventory_detail",
    ),
    re_path(
        r"^warehouse/(?P<warehouse>\d+)/inventory/(?P<pk>\d+)/export$",
        exports.warehouse_inv_export,
        name="warehouse_inventory_export",
    ),
    re_path(
        r"^warehouse/(?P<warehouse>\d+)/inventory/(?P<pk>\d+)/edit$",
        views.inventory_edit,
        name="warehouse_inventory_edit",
    ),
    re_path(
        r"^warehouse/(?P<warehouse>\d+)/inventory/(?P<pk>\d+)/delete$",
        views.inventory_delete,
        name="warehouse_inventory_delete",
    ),
    re_path(r"^order/?$", views.order_list, name="order_list"),
    re_path(r"^order/add$", views.order_add, name="order_add"),
    re_path(r"^order/(?P<pk>\d+)/?$", views.order_detail, name="order_detail"),
    re_path(
        r"^order/(?P<pk>\d+)/export$",
        exports.order_export,
        name="order_export",
    ),
    re_path(r"^order/(?P<pk>\d+)/edit$", views.order_edit, name="order_edit"),
    re_path(
        r"^order/(?P<pk>\d+)/check-stock$",
        views.order_check_stock,
        name="order_check_stock",
    ),
    re_path(
        r"^order/(?P<pk>\d+)/add-shipment$",
        views.order_add_shipment,
        name="order_add_shipment",
    ),
    re_path(
        r"^order/(?P<pk>\d+)/delete$", views.order_delete, name="order_delete"
    ),
    re_path(r"^ship/?$", views.ship_list, name="ship_list"),
    re_path(r"^ship/add$", views.ship_add, name="ship_add"),
    re_path(r"^ship/(?P<pk>\d+)/?$", views.ship_detail, name="ship_detail"),
    re_path(
        r"^ship/(?P<pk>\d+)/export$", exports.ship_export, name="ship_export"
    ),
    re_path(r"^ship/(?P<pk>\d+)/edit$", views.ship_edit, name="ship_edit"),
    re_path(
        r"^ship/(?P<pk>\d+)/delete$", views.ship_delete, name="ship_delete"
    ),
    re_path(
        r"^dal/part/?$", views.Part_Autocomplete.as_view(), name="part-dal"
    ),
    re_path(
        r"^dal/assy/?$",
        views.Assembly_Autocomplete.as_view(),
        name="assembly-dal",
    ),
    re_path(
        r"^dal/order/?$", views.Order_Autocomplete.as_view(), name="order-dal"
    ),
    re_path(r"^dal/mfg/?$", views.Mfg_Autocomplete.as_view(), name="mfg-dal"),
    re_path(
        r"^dal/footprint/?$",
        views.Footprint_Autocomplete.as_view(),
        name="footprint-dal",
    ),
]
