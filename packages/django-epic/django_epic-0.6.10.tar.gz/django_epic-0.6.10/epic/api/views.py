#
#   Copyright (c) 2021 eGauge Systems LLC
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
# pylint: disable=too-few-public-methods, no-member, too-many-ancestors
# pylint: disable=no-self-use
import django_filters.rest_framework
from rest_framework import permissions, serializers, viewsets

from epic.models import Assembly_Item, Part, Vendor, Vendor_Part
from epic.perms import EDIT, VIEW

#
# Django query-ops supported when filtering based on object fields.
# For example:
#
# 	api/assembly_item/?refdes__icontains=102
#
# returns all assembly-items whose refdes string includes "102".
#
INT_OPS = ["exact", "lte", "gte"]
STRING_OPS = ["exact", "startswith", "istartswith", "contains", "icontains"]


def get_bulk_update_serializer(self, *args, **kwargs):
    """This method enables bulk-updating of models by setting the
    serializer's MANY argument to True when a JSON list is sent to the
    server.

    """
    if "data" in kwargs:
        data = kwargs["data"]
        if isinstance(data, list):
            kwargs["many"] = True
    return super(viewsets.ModelViewSet, self).get_serializer(*args, **kwargs)


def expand_range(r):
    """Convert a number-range string R to the corresponding set of numbers
    and return that set.  The range string must have the syntax:

      RANGE = DECIMAL ['-' DECIMAL].
      DECIMAL = DIGIT { DIGIT }.
      DIGIT = '0'-'9'.

    An empty set is returned if the R has invalid syntax.

    """
    limits = r.split("-")
    try:
        if len(limits) == 1:
            return set([int(limits[0])])
        if len(limits) == 2:
            return set(range(int(limits[0]), int(limits[1]) + 1))
    except (TypeError, ValueError):
        pass
    return set()


def range_list_filter(fieldname, queryset, request):
    """Filter QUERYSET according to a query-parameter called FIELDNAME.
    The query-parameters are taken from REQUEST, which must be the
    HTTP request that triggered this call.

    The query-parameter value specifies a set of numbers to be
    selected as a numeric range-list with syntax:

      RANGE_LIST = RANGE { ',' RANGE }.

    See method expand_range() for the RANGE syntax.

    For example, "id=13,20-22,99" would return the set containing
    numbers 13, 20, 21, 22, and 99.

    The queryset is then filtered to objects whose FIELDNAME value is
    in the specified set of numbers.

    """
    range_list = request.query_params.get(fieldname)
    if range_list is not None:
        selected = set()
        for r in range_list.split(","):
            selected |= expand_range(r)
        params = {}
        params[fieldname + "__in"] = selected
        queryset = queryset.filter(**params)
    return queryset


class IsAuthorized(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.has_perms((VIEW,))
        return request.user.has_perms((EDIT,))


class PartSerializer(serializers.ModelSerializer):
    best_part = serializers.SerializerMethodField()
    equivalents = serializers.SerializerMethodField()

    class Meta:
        model = Part
        fields = "__all__"

    def get_best_part(self, obj):
        return obj.best_part().id

    def get_equivalents(self, obj):
        return [p.id for p in obj.equivalent_parts()]


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = "__all__"


class VendorPartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor_Part
        fields = "__all__"


class AssemblyItemPartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assembly_Item
        fields = "__all__"


class PartViewSet(viewsets.ModelViewSet):
    """API endpoint for viewing and editing parts."""

    serializer_class = PartSerializer
    permission_classes = [IsAuthorized]
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_fields = {
        "val": INT_OPS,
        "mfg": STRING_OPS,
        "mfg_pn": STRING_OPS,
        "mounting": INT_OPS,
        "status": INT_OPS,
    }
    pagination_class = None

    get_serializer = get_bulk_update_serializer

    def get_queryset(self):
        return range_list_filter("id", Part.objects.all(), self.request)

    def update(self, request, pk=None):
        # delete assembly items associated with this part, if any:
        Assembly_Item.objects.filter(assy_id=pk).delete()
        return super().update(request, pk)


class VendorViewSet(viewsets.ModelViewSet):
    """API endpoint for viewing and editing vendors."""

    serializer_class = VendorSerializer
    permission_classes = [IsAuthorized]
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = {"name": STRING_OPS}
    pagination_class = None

    get_serializer = get_bulk_update_serializer

    def get_queryset(self):
        return range_list_filter("id", Vendor.objects.all(), self.request)


class VendorPartViewSet(viewsets.ModelViewSet):
    """API endpoint for viewing and editing vendor parts."""

    serializer_class = VendorPartSerializer
    permission_classes = [IsAuthorized]
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = {
        "part": INT_OPS,
        "vendor": INT_OPS,
        "vendor_pn": STRING_OPS,
        "status": INT_OPS,
    }
    pagination_class = None

    get_serializer = get_bulk_update_serializer

    def get_queryset(self):
        qs = range_list_filter("id", Vendor_Part.objects.all(), self.request)
        return range_list_filter("part_id", qs, self.request)


class AssemblyItemViewSet(viewsets.ModelViewSet):
    """API endpoint for viewing and editing assembly items."""

    serializer_class = AssemblyItemPartSerializer
    permission_classes = [IsAuthorized]
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = {
        "assy": INT_OPS,
        "comp": INT_OPS,
        "qty": INT_OPS,
        "refdes": STRING_OPS,
    }
    pagination_class = None

    get_serializer = get_bulk_update_serializer

    def get_queryset(self):
        return range_list_filter(
            "id", Assembly_Item.objects.all(), self.request
        )
