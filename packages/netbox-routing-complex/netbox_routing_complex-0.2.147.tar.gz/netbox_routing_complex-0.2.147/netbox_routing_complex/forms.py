from django import forms
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from utilities.forms.fields import CommentField, DynamicModelMultipleChoiceField
from ipam.models import VRF, Prefix, IPAddress
from dcim.models import Device

from .models import VNI, VXLAN, AddressFamilyChoices, BFDConfig, BGPGlobalConfig, BGPPeer, BGPPeerGroup, BGPSessionConfig, ISISConfig, StaticRoute


class BFDConfigForm(NetBoxModelForm):
    comments = CommentField()

    class Meta:
        model = BFDConfig
        fields = ('hello_interval', 'multiplier', 'description', 'comments', 'tags')

class BGPGlobalConfigForm(NetBoxModelForm):
    comments = CommentField()

    class Meta:
        model = BGPGlobalConfig
        fields = (
            'device', 'asn', 'use_cluster_id', 'router_id_override', 'cluster_id_override', 'graceful_restart', 'up_down_logging', 'comments', 'tags'
        )

class BGPSessionConfigForm(NetBoxModelForm):
    comments = CommentField()
    #address_families should be a dropdown in the GUI
    address_families = forms.MultipleChoiceField(
        choices=AddressFamilyChoices,
        required=False
    )

    class Meta:
        model = BGPSessionConfig
        fields = (
            'name', 'address_families', 'peer_asn', 'import_policy', 'export_policy',
            'next_hop_self', 'hardcoded_description', 'hello_interval', 'keepalive_interval',
            'ebgp_multihop', 'unencrypted_password', 'encrypted_password', 'source_interface',
            'source_ip', 'local_asn', 'bfd_config', 'use_route_reflector_client', 'comments', 'tags'
        )

class BGPPeerForm(NetBoxModelForm):
    comments = CommentField()

    class Meta:
        model = BGPPeer
        fields = ('device', 'name', 'peer_ip', 'session_config', 'comments', 'tags')

class BGPPeerGroupForm(NetBoxModelForm):
    comments = CommentField()

    class Meta:
        model = BGPPeerGroup
        fields = ('device', 'name', 'description', 'session_config', 'peers', 'comments', 'tags')

class VNIForm(NetBoxModelForm):
    comments = CommentField()

    class Meta:
        model = VNI
        fields = ('vlan', 'vnid', 'tenant', 'description', 'comments', 'tags')

class VXLANForm(NetBoxModelForm):
    comments = CommentField()

    class Meta:
        model = VXLAN
        fields = (
            'ipv4_gateway', 'ipv6_gateway', 'vni', 'l3mtu', 'ingress_replication', 'comments', 'tags'
        )

class ISISConfigForm(NetBoxModelForm):
    comments = CommentField()

    class Meta:
        model = ISISConfig
        fields = (
            'device', 'router_id', 'pid', 'afi', 'area_id', 'network_selector', 'net_hardcoded', 'default_link_metric', 'comments', 'tags'
        )

class StaticRouteForm(NetBoxModelForm):
    comments = CommentField()

    class Meta:
        model = StaticRoute
        fields = (
            'device', 'vrf', 'subnet', 'next_hop_ip', 'next_hop_int',
            'bfd_config', 'description', 'administrative_distance', 'comments', 'tags'
        )

class StaticRouteFilterForm(NetBoxModelFilterSetForm):
    model = StaticRoute

    device = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False
    )
    
    vrf = DynamicModelMultipleChoiceField(
        queryset=VRF.objects.all(),
        required=False
    )

    subnet = forms.CharField(
        required=False,
        label='Subnet'
    )

    next_hop_ip = DynamicModelMultipleChoiceField(
        queryset=IPAddress.objects.all(),
        required=False,
        label='Next Hop IP'
    )