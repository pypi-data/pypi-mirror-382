from django.urls import path
from netbox.views.generic import ObjectChangeLogView

from .constants import APP_LABEL
from . import models, views

urlpatterns = [
    # BFD Config URLs
    path('bfd-configs/',                 views.BFDConfigListView.as_view(),   name='bfdconfig_list'),
    path('bfd-configs/add/',             views.BFDConfigEditView.as_view(),   name='bfdconfig_add'),
    path('bfd-configs/<int:pk>/',        views.BFDConfigView.as_view(),       name='bfdconfig'),
    path('bfd-configs/<int:pk>/edit/',   views.BFDConfigEditView.as_view(),   name='bfdconfig_edit'),
    path('bfd-configs/<int:pk>/delete/', views.BFDConfigDeleteView.as_view(), name='bfdconfig_delete'),
    path('bfd-configs/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='bfdconfig_changelog', kwargs={
        'model': models.BFDConfig
    }),

    # BGP Global Config URLs
    path('bgp-global-configs/',                 views.BGPGlobalConfigListView.as_view(),   name='bgpglobalconfig_list'),
    path('bgp-global-configs/add/',             views.BGPGlobalConfigEditView.as_view(),   name='bgpglobalconfig_add'),
    path('bgp-global-configs/<int:pk>/',        views.BGPGlobalConfigView.as_view(),       name='bgpglobalconfig'),
    path('bgp-global-configs/<int:pk>/edit/',   views.BGPGlobalConfigEditView.as_view(),   name='bgpglobalconfig_edit'),
    path('bgp-global-configs/<int:pk>/delete/', views.BGPGlobalConfigDeleteView.as_view(), name='bgpglobalconfig_delete'),
    path('bgp-global-configs/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='bgpglobalconfig_changelog', kwargs={
        'model': models.BGPGlobalConfig
    }),

    # BGP Session Config URLs
    path('bgp-session-configs/',                 views.BGPSessionConfigListView.as_view(),   name='bgpsessionconfig_list'),
    path('bgp-session-configs/add/',             views.BGPSessionConfigEditView.as_view(),   name='bgpsessionconfig_add'),
    path('bgp-session-configs/<int:pk>/',        views.BGPSessionConfigView.as_view(),       name='bgpsessionconfig'),
    path('bgp-session-configs/<int:pk>/edit/',   views.BGPSessionConfigEditView.as_view(),   name='bgpsessionconfig_edit'),
    path('bgp-session-configs/<int:pk>/delete/', views.BGPSessionConfigDeleteView.as_view(), name='bgpsessionconfig_delete'),
    path('bgp-session-configs/<int:pk>/changelog/', ObjectChangeLogView.as_view(),           name='bgpsessionconfig_changelog', kwargs={
        'model': models.BGPSessionConfig
    }),

    # BGP Peer URLs
    path('bgp-peers/',                 views.BGPPeerListView.as_view(),   name='bgppeer_list'),
    path('bgp-peers/add/',             views.BGPPeerEditView.as_view(),   name='bgppeer_add'),
    path('bgp-peers/<int:pk>/',        views.BGPPeerView.as_view(),       name='bgppeer'),
    path('bgp-peers/<int:pk>/edit/',   views.BGPPeerEditView.as_view(),   name='bgppeer_edit'),
    path('bgp-peers/<int:pk>/delete/', views.BGPPeerDeleteView.as_view(), name='bgppeer_delete'),
    path('bgp-peers/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='bgppeer_changelog', kwargs={
        'model': models.BGPPeer
    }),

    # BGP Peer Group URLs
    path('bgp-peer-groups/',                 views.BGPPeerGroupListView.as_view(),   name='bgppeergroup_list'),
    path('bgp-peer-groups/add/',             views.BGPPeerGroupEditView.as_view(),   name='bgppeergroup_add'),
    path('bgp-peer-groups/<int:pk>/',        views.BGPPeerGroupView.as_view(),       name='bgppeergroup'),
    path('bgp-peer-groups/<int:pk>/edit/',   views.BGPPeerGroupEditView.as_view(),   name='bgppeergroup_edit'),
    path('bgp-peer-groups/<int:pk>/delete/', views.BGPPeerGroupDeleteView.as_view(), name='bgppeergroup_delete'),
    path('bgp-peer-groups/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='bgppeergroup_changelog', kwargs={
        'model': models.BGPPeerGroup
    }),

    # VNI URLs
    path('vnis/',                 views.VNIListView.as_view(),   name='vni_list'),
    path('vnis/add/',             views.VNIEditView.as_view(),   name='vni_add'),
    path('vnis/<int:pk>/',        views.VNIView.as_view(),       name='vni'),
    path('vnis/<int:pk>/edit/',   views.VNIEditView.as_view(),   name='vni_edit'),
    path('vnis/<int:pk>/delete/', views.VNIDeleteView.as_view(), name='vni_delete'),
    path('vnis/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='vni_changelog', kwargs={
        'model': models.VNI
    }),

    # VXLAN URLs
    path('vxlans/',                 views.VXLANListView.as_view(),   name='vxlan_list'),
    path('vxlans/add/',             views.VXLANEditView.as_view(),   name='vxlan_add'),
    path('vxlans/<int:pk>/',        views.VXLANView.as_view(),       name='vxlan'),
    path('vxlans/<int:pk>/edit/',   views.VXLANEditView.as_view(),   name='vxlan_edit'),
    path('vxlans/<int:pk>/delete/', views.VXLANDeleteView.as_view(), name='vxlan_delete'),
    path('vxlans/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='vxlan_changelog', kwargs={
        'model': models.VXLAN
    }),

    # ISIS Config URLs
    path('isis-configs/',                 views.ISISConfigListView.as_view(),   name='isisconfig_list'),
    path('isis-configs/add/',             views.ISISConfigEditView.as_view(),   name='isisconfig_add'),
    path('isis-configs/<int:pk>/',        views.ISISConfigView.as_view(),       name='isisconfig'),
    path('isis-configs/<int:pk>/edit/',   views.ISISConfigEditView.as_view(),   name='isisconfig_edit'),
    path('isis-configs/<int:pk>/delete/', views.ISISConfigDeleteView.as_view(), name='isisconfig_delete'),
    path('isis-configs/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='isisconfig_changelog', kwargs={
        'model': models.ISISConfig
    }),

    # Static Route URLs
    path('static-routes/',                 views.StaticRouteListView.as_view(),   name='staticroute_list'),
    path('static-routes/add/',             views.StaticRouteEditView.as_view(),   name='staticroute_add'),
    path('static-routes/<int:pk>/',        views.StaticRouteView.as_view(),       name='staticroute'),
    path('static-routes/<int:pk>/edit/',   views.StaticRouteEditView.as_view(),   name='staticroute_edit'),
    path('static-routes/<int:pk>/delete/', views.StaticRouteDeleteView.as_view(), name='staticroute_delete'),
    path('static-routes/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='staticroute_changelog', kwargs={
        'model': models.StaticRoute
    }),
]

#this is where we link views to URLs
#<int:pk> is a path converter which allows the user to enter an integer to get a specific object from the database by its id



