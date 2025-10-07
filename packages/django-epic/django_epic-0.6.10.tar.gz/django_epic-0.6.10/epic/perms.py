#
#   Copyright (c) 2014-2015, 2018 eGauge Systems LLC
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
from django.contrib.auth import models as auth_models
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_migrate

from epic.apps import EPIC_App_Config as app

VIEW_NAME = "view"
EDIT_NAME = "edit"

VIEW = "%s.%s" % (app.name, VIEW_NAME)
EDIT = "%s.%s" % (app.name, EDIT_NAME)

VIEW_PERM = None
EDIT_PERM = None


def add_custom_permissions(sender, **kwargs):
    # pylint: disable=unused-argument, global-statement
    global VIEW_PERM, EDIT_PERM

    ct, _ = ContentType.objects.get_or_create(app_label=app.name, model="")
    p, _ = Permission.objects.get_or_create(
        codename=VIEW_NAME, name="can view", content_type=ct
    )
    VIEW_PERM = p
    p, _ = Permission.objects.get_or_create(
        codename=EDIT_NAME, name="can edit/delete", content_type=ct
    )
    EDIT_PERM = p


post_migrate.connect(add_custom_permissions, sender=auth_models)
