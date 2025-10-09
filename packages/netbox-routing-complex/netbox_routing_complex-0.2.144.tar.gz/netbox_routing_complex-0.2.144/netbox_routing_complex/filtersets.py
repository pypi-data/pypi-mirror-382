# netbox_routing_complex/filtersets.py

from netbox.filtersets import NetBoxModelFilterSet
from dcim.models import Device, Interface
from ipam.models import VLAN, IPAddress, Prefix, VRF
from django.db.models import Q
import django_filters

from .models import VNI, VXLAN, BGPGlobalConfig, ISISConfig, StaticRoute

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
    


    
class VNIFilterSet(NetBoxModelFilterSet):
    vlan_id = django_filters.ModelMultipleChoiceFilter(
        queryset=VLAN.objects.all(),
        field_name='vlan_id',
        label='VLAN (ID)',
    )

    vlan_vid = django_filters.ModelMultipleChoiceFilter(
        queryset=VLAN.objects.all(),
        field_name='vlan__vid',
        to_field_name='vid',
        label='VLAN (VID)',
    )

    class Meta:
        model = VNI
        fields = ('id', 'vnid', 'vlan_id', 'vlan_vid')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(vnid__icontains=value)
        )
    

class VXLANFilterSet(NetBoxModelFilterSet):
    vni_id = django_filters.ModelMultipleChoiceFilter(
        queryset=VNI.objects.all(),
        field_name='vni_id',
        label='VNI (ID)',
    )

    class Meta:
        model = VXLAN
        fields = ('id', 'vni_id')



class StaticRouteFilterSet(NetBoxModelFilterSet):
    """
    FilterSet for the StaticRoute model.
    """
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
    vrf = django_filters.ModelMultipleChoiceFilter(
        queryset=VRF.objects.all(),
        field_name='vrf__name',
        to_field_name='name',
        label='VRF (Name)',
    )
    subnet = django_filters.ModelMultipleChoiceFilter(
        queryset=Prefix.objects.all(),
        field_name='subnet__prefix',
        to_field_name='prefix',
        label='Subnet',
    )
    next_hop_ip = django_filters.ModelMultipleChoiceFilter(
        queryset=IPAddress.objects.all(),
        field_name='next_hop_ip__address',
        to_field_name='address',
        label='Next Hop IP',
    )


    class Meta:
        model = StaticRoute
        fields = ('id', 'device', 'vrf', 'subnet', 'next_hop_ip', 'description', 'administrative_distance')

    def search(self, queryset, name, value):
        """
        Custom search method for the 'q' query parameter.
        """
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(description__icontains=value)
        )