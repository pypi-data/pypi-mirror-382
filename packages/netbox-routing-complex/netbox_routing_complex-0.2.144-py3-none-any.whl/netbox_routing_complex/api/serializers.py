from rest_framework import serializers

from netbox.api.serializers import NetBoxModelSerializer
from dcim.api.serializers import DeviceSerializer, InterfaceSerializer
from ipam.api.serializers import IPAddressSerializer, VLANSerializer, PrefixSerializer, VRFSerializer

from ..models import VNI, VXLAN, BFDConfig, BGPGlobalConfig, BGPPeer, BGPPeerGroup, BGPSessionConfig, ISISConfig, StaticRoute
from ..constants import APP_LABEL

class BFDConfigSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name=f'plugins-api:{APP_LABEL}-api:bfdconfig-detail' #this is the name of an api view that we have to write and link to in urls
    )

    class Meta:
        model = BFDConfig
        fields = (
            #the order of these fields is how the JSON/API representation of the object will be structured
            'id', 'hello_interval', 'multiplier', 'description', 'tags', 'custom_fields', 'created', 'last_updated'
        )
        brief_fields = ('id', 'hello_interval', 'multiplier', 'description') #the shorthand serializer

class BGPGlobalConfigSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name=f'plugins-api:{APP_LABEL}-api:bgpglobalconfig-detail'
    )
    device = DeviceSerializer(nested=True)

    class Meta:
        model = BGPGlobalConfig
        fields = (
            'id', 'device', 'asn', 'use_cluster_id', 'router_id_override', 'cluster_id_override', 'graceful_restart', 'up_down_logging', 'tags', 'custom_fields', 'created', 'last_updated'
        )
        brief_fields = ('id', 'device', 'asn')




class BGPSessionConfigSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name=f'plugins-api:{APP_LABEL}-api:bgpsessionconfig-detail'
    )

    class Meta:
        model = BGPSessionConfig
        fields = (
            'id', 'name', 'address_families', 'peer_asn', 'import_policy', 'export_policy',
            'next_hop_self', 'hardcoded_description', 'hello_interval', 'keepalive_interval',
            'ebgp_multihop', 'unencrypted_password', 'encrypted_password', 'source_interface',
            'source_ip', 'local_asn', 'bfd_config', 'use_route_reflector_client', 'tags', 'custom_fields', 'created', 'last_updated'
        )
        brief_fields = ('id', 'name', 'description')

class BGPPeerSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name=f'plugins-api:{APP_LABEL}-api:bgppeer-detail'
    )
    device = DeviceSerializer(nested=True) #nested=True return the brief serialized version of the object reference
    peer_ip = IPAddressSerializer(nested=True) #nested=True return the brief serialized version of the object reference

    class Meta:
        model = BGPPeer
        fields = (
            'id', 'device', 'name', 'peer_ip', 'session_config', 'tags', 'custom_fields', 'created', 'last_updated'
        )
        brief_fields = ('id', 'device', 'name', 'peer_ip', 'session_config')

class BGPPeerGroupSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name=f'plugins-api:{APP_LABEL}-api:bgppeergroup-detail'
    )
    device = DeviceSerializer(nested=True) #nested=True return the brief serialized version of the object reference

    class Meta:
        model = BGPPeerGroup
        fields = (
            'id', 'device', 'name', 'description', 'session_config', 'peers', 'tags', 'custom_fields', 'created', 'last_updated'
        )
        brief_fields = ('id', 'name', 'description')

class VNISerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name=f'plugins-api:{APP_LABEL}-api:vni-detail'
    )
    vlan = VLANSerializer(nested=True)

    class Meta:
        model = VNI
        fields = (
            'id', 'vnid', 'vlan', 'tenant', 'description', 'tags', 'custom_fields', 'created', 'last_updated'
        )
        brief_fields = ('id', 'vnid', 'vlan', 'description')

class VXLANSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name=f'plugins-api:{APP_LABEL}-api:vxlan-detail'
    )
    ipv4_gateway=IPAddressSerializer(nested=True)
    ipv6_gateway=IPAddressSerializer(nested=True)
    vni=VNISerializer(nested=True)

    class Meta:
        model = VXLAN
        fields = (
            'id', 'ipv4_gateway', 'ipv6_gateway', 'vni', 'l3mtu', 'ingress_replication', 'tags', 'custom_fields', 'created', 'last_updated'
        )
        brief_fields = ('id', 'vni', 'ipv4_gateway', 'ipv6_gateway')

class ISISConfigSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name=f'plugins-api:{APP_LABEL}-api:isisconfig-detail'
    )
    net = serializers.CharField(read_only=True) #this is a property and should never be hit on a create operation
    device = DeviceSerializer(nested=True) #nested=True return the brief serialized version of the object reference

    class Meta:
        model = ISISConfig
        fields = (
            'id', 'device', 'router_id', 'pid', 'afi', 'area_id', 'network_selector', 'net_hardcoded', 'net', 'default_link_metric', 'tags', 'custom_fields', 'created', 'last_updated'
        )
        brief_fields = ('id', 'device', 'router_id', 'net')

class StaticRouteSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name=f'plugins-api:{APP_LABEL}-api:staticroute-detail'
    )
    device = DeviceSerializer(nested=True)
    vrf = VRFSerializer(nested=True)
    subnet = PrefixSerializer(nested=True)
    next_hop_ip = IPAddressSerializer(nested=True)
    next_hop_int = InterfaceSerializer(nested=True)
    bfd_config = BFDConfigSerializer(nested=True)

    class Meta:
        model = StaticRoute
        fields = (
            'id', 'device', 'vrf', 'subnet', 'next_hop_ip', 'next_hop_int', 'bfd_config', 'description', 'administrative_distance', 'tags', 'custom_fields', 'created', 'last_updated'
        )
        brief_fields = ('id', 'device', 'vrf', 'subnet', 'next_hop_ip', 'next_hop_int', 'description', 'administrative_distance')