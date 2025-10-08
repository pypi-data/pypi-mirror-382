# netbox_routing_complex/filtersets.py

from netbox.filtersets import NetBoxModelFilterSet
from dcim.models import Device
from django.db.models import Q
import django_filters

from .models import BGPGlobalConfig, ISISConfig

class ISISConfigFilterSet(NetBoxModelFilterSet):
    """
    FilterSet for the ISISConfig model.

    This class defines the filterable fields for the ISISConfig model via the API.
    """
    # Allow filtering by device ID or name
    device = django_filters.ModelMultipleChoiceFilter(
        queryset=Device.objects.all(),
        field_name='device__name',
        to_field_name='name',
        label='Device (name)',
    )
    device_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Device.objects.all(),
        field_name='device_id',
        to_field_name='id',
        label='Device (ID)',
    )

    class Meta:
        model = ISISConfig
        # These are the fields you can filter on. Add any other model fields here.
        fields = ('id', 'pid', 'afi', 'area_id', 'default_link_metric')

    def search(self, queryset, name, value):
        """
        Custom search method. This allows for a general 'q' query parameter
        to search across multiple text fields.
        """
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(pid__icontains=value) |
            Q(area_id__icontains=value) |
            Q(net_hardcoded__icontains=value)
        )
    
class BGPGlobalConfigFilterSet(NetBoxModelFilterSet):
    device = django_filters.ModelMultipleChoiceFilter(
        queryset=Device.objects.all(),
        field_name='device__name',
        to_field_name='name',
        label='Device (name)',
    )
    device_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Device.objects.all(),
        field_name='device_id',
        to_field_name='id',
        label='Device (ID)',
    )

    class Meta:
        model = BGPGlobalConfig
        fields = ('id', 'asn', 'use_cluster_id', 'graceful_restart', 'up_down_logging')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(asn__icontains=value)
        )