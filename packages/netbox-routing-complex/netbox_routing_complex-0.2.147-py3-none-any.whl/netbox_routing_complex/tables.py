import django_tables2 as tables

from netbox.tables import NetBoxTable, ChoiceFieldColumn
from .models import VNI, VXLAN, BFDConfig, BGPGlobalConfig, BGPPeer, BGPPeerGroup, BGPSessionConfig, ISISConfig, StaticRoute

class BFDConfigTable(NetBoxTable):
    class Meta(NetBoxTable.Meta):
        model = BFDConfig
        fields = ('pk', 'id', 'hello_interval', 'multiplier', 'description')
        default_columns = ('hello_interval', 'multiplier', 'description')

class BGPGlobalConfigTable(NetBoxTable):
    device = tables.LinkColumn()
    router_id_override = tables.LinkColumn()
    cluster_id_override = tables.LinkColumn()

    class Meta(NetBoxTable.Meta):
        model = BGPGlobalConfig
        fields = ('pk', 'id', 'device', 'asn', 'use_cluster_id', 'router_id_override', 'cluster_id_override', 'graceful_restart', 'up_down_logging')
        default_columns = ('device', 'asn', 'use_cluster_id', 'graceful_restart', 'up_down_logging')

class BGPSessionConfigTable(NetBoxTable):
    bfd_config = tables.LinkColumn()
    class Meta(NetBoxTable.Meta):
        model = BGPSessionConfig
        fields = (
            'pk', 'id', 'name', 'address_families', 'peer_asn', 'import_policy', 'export_policy',
            'next_hop_self', 'hardcoded_description', 'hello_interval', 'keepalive_interval',
            'ebgp_multihop', 'source_interface', 'source_ip', 'local_asn', 'bfd_config', 'use_route_reflector_client'
        )
        default_columns = ('name', 'peer_asn', 'address_families', 'bfd_config', 'hardcoded_description', 'use_route_reflector_client')

class BGPPeerTable(NetBoxTable):
    device = tables.LinkColumn()
    remote_device = tables.Column(
        linkify=True,
        verbose_name='Remote Device'
    )
    session_config = tables.LinkColumn()
    peer_ip = tables.LinkColumn()

    class Meta(NetBoxTable.Meta):
        model = BGPPeer
        fields = ('pk', 'id', 'device', 'remote_device', 'name', 'peer_ip', 'session_config')
        default_columns = ('device', 'remote_device', 'name', 'peer_ip', 'session_config')

class BGPPeerGroupTable(NetBoxTable):
    device = tables.LinkColumn()
    session_config = tables.LinkColumn()
    peers = tables.ManyToManyColumn(
        linkify=True
    )
    class Meta(NetBoxTable.Meta):
        model = BGPPeerGroup
        fields = ('pk', 'id', 'device', 'name', 'description', 'session_config', 'peers')
        default_columns = ('device', 'name', 'description', 'session_config', 'peers')

class VNITable(NetBoxTable):
    vlan = tables.LinkColumn()
    tenant = tables.LinkColumn()
    class Meta(NetBoxTable.Meta):
        model = VNI
        fields = ('pk', 'id', 'vlan', 'vnid', 'tenant', 'description')
        default_columns = ('vlan', 'vnid', 'tenant', 'description')

class VXLANTable(NetBoxTable):
    vni = tables.LinkColumn()
    ipv4_gateway = tables.LinkColumn()
    ipv6_gateway = tables.LinkColumn()

    class Meta(NetBoxTable.Meta):
        model = VXLAN
        fields = ('pk', 'id', 'vni', 'ipv4_gateway', 'ipv6_gateway', 'l3mtu', 'ingress_replication')
        default_columns = ('vni', 'ipv4_gateway', 'ipv6_gateway', 'ingress_replication')

class ISISConfigTable(NetBoxTable):
    device = tables.LinkColumn()
    router_id = tables.LinkColumn()
    net = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = ISISConfig
        fields = ('pk', 'id', 'device', 'router_id', 'pid', 'area_id', 'net', 'default_link_metric')
        default_columns = ('device', 'router_id', 'net')

class StaticRouteTable(NetBoxTable):
    device = tables.LinkColumn()
    vrf = tables.LinkColumn()
    subnet = tables.Column()
    next_hop_ip = tables.LinkColumn()
    next_hop_int = tables.LinkColumn()
    bfd_config = tables.LinkColumn()

    class Meta(NetBoxTable.Meta):
        model = StaticRoute
        fields = (
            'pk', 'id', 'device', 'vrf', 'subnet', 'next_hop_ip',
            'next_hop_int', 'bfd_config', 'description', 'administrative_distance'
        )
        default_columns = ('device', 'vrf', 'subnet', 'next_hop_ip', 'description')