#
#   Copyright (c) 2014-2015, 2021 eGauge Systems LLC
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
# pylint: disable=import-outside-toplevel, unused-import
from django.apps import AppConfig


class EPIC_App_Config(AppConfig):
    name = "epic"
    verbose_name = "Electronic Parts Inventory Center"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        import epic.signals
