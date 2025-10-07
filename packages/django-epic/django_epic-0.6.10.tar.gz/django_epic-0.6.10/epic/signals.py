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
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from epic.models import (
    Datasheet,
    Delta,
    Part,
    Shipment,
    Stock_Cache_Entry,
    Stock_Cache_Item,
    Warehouse,
)


def flush_caches(sender, **kwargs):
    """Any model class that maintains caches should register a
    'flush_caches' class method.  That method will then automatically
    be called if any instances of that model class are saved or
    deleted.
    """
    if hasattr(sender, "flush_caches"):
        sender.flush_caches(sender, **kwargs)


@receiver(post_save, dispatch_uid="epic_signal_id")
def save_receiver(sender, **kwargs):
    flush_caches(sender, **kwargs)


@receiver(post_delete, dispatch_uid="epic_signal_id")
def delete_receiver(sender, **kwargs):
    flush_caches(sender, **kwargs)


@receiver(post_delete, sender=Datasheet)
def datasheet_delete(sender, instance, **kwargs):
    # pylint: disable=unused-argument
    instance.ds_file.delete(False)


@receiver(post_delete, sender=Shipment)
def shipment_delete(sender, instance, **kwargs):
    # pylint: disable=unused-argument
    instance.finalize()


@receiver(post_delete, sender=Part)
def part_delete(sender, instance, **kwargs):
    # pylint: disable=unused-argument
    if instance.id is not None:
        Stock_Cache_Item.objects.filter(part_id=instance.id).delete()


@receiver(post_delete, sender=Warehouse)
def warehouse_delete(sender, instance, **kwargs):
    # pylint: disable=unused-argument
    if instance.id is not None:
        Stock_Cache_Item.objects.filter(warehouse_id=instance.id).delete()


@receiver(post_delete, sender=Delta)
def delta_delete(sender, instance, **kwargs):
    # pylint: disable=unused-argument
    if instance.txtn is not None:
        Stock_Cache_Entry.invalidate(instance.txtn.ts)
