from netbox.api.viewsets import NetBoxModelViewSet

from .. import models
from ..filtersets import BGPGlobalConfigFilterSet, ISISConfigFilterSet, StaticRouteFilterSet, VNIFilterSet, VXLANFilterSet
from .serializers import (
    BFDConfigSerializer, BGPGlobalConfigSerializer, BGPPeerGroupSerializer, BGPPeerSerializer, 
    BGPSessionConfigSerializer, ISISConfigSerializer, StaticRouteSerializer, VNISerializer, VXLANSerializer
)

class BFDConfigViewSet(NetBoxModelViewSet):
    queryset = models.BFDConfig.objects.prefetch_related('tags')
    serializer_class = BFDConfigSerializer

class BGPGlobalConfigViewSet(NetBoxModelViewSet):
    queryset = models.BGPGlobalConfig.objects.prefetch_related('tags', 'device')
    serializer_class = BGPGlobalConfigSerializer
    filterset_class = BGPGlobalConfigFilterSet

class BGPSessionConfigViewSet(NetBoxModelViewSet):
    queryset = models.BGPSessionConfig.objects.prefetch_related('tags', 'bfd_config') #prefetch_related prevents n+1 querie problem by bulk querying these relations
    serializer_class = BGPSessionConfigSerializer

class BGPPeerViewSet(NetBoxModelViewSet):
    queryset = models.BGPPeer.objects.prefetch_related('tags', 'device', 'session_config')
    serializer_class = BGPPeerSerializer

class BGPPeerGroupViewSet(NetBoxModelViewSet):
    queryset = models.BGPPeerGroup.objects.prefetch_related('tags', 'device', 'session_config', 'peers')
    serializer_class = BGPPeerGroupSerializer

class VNIViewSet(NetBoxModelViewSet):
    queryset = models.VNI.objects.prefetch_related('tags', 'vlan')
    serializer_class = VNISerializer
    filterset_class = VNIFilterSet

class VXLANViewSet(NetBoxModelViewSet):
    queryset = models.VXLAN.objects.prefetch_related('tags', 'vni')
    serializer_class = VXLANSerializer
    filterset_class = VXLANFilterSet

class ISISConfigViewSet(NetBoxModelViewSet):
    queryset = models.ISISConfig.objects.prefetch_related('tags', 'device', 'router_id')
    serializer_class = ISISConfigSerializer
    filterset_class = ISISConfigFilterSet
    ordering = ('pk',)

class StaticRouteViewSet(NetBoxModelViewSet):
    queryset = models.StaticRoute.objects.prefetch_related('tags', 'device', 'vrf', 'next_hop_ip', 'next_hop_int', 'bfd_config')
    serializer_class = StaticRouteSerializer
    filterset_class = StaticRouteFilterSet