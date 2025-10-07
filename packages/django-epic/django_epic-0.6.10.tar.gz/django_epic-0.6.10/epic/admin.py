#
#   Copyright (c) 2014-2015, 2019 eGauge Systems LLC
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
from django.contrib import admin

from epic import models

admin.site.register(models.Part)
admin.site.register(models.Datasheet)
admin.site.register(models.Vendor)
admin.site.register(models.Warehouse)
admin.site.register(models.Order)
admin.site.register(models.Shipment)
admin.site.register(models.Inventory)
admin.site.register(models.Stock_Cache_Entry)
admin.site.register(models.Stock_Cache_Item)
