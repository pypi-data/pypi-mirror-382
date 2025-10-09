from netbox.api.routers import NetBoxRouter

from . import views

from ..constants import APP_LABEL

app_name = APP_LABEL

#link the view to an api route
router = NetBoxRouter()
router.register('bfd-configs', views.BFDConfigViewSet)
router.register('bgp-global-configs', views.BGPGlobalConfigViewSet)
router.register('bgp-session-configs', views.BGPSessionConfigViewSet)
router.register('bgp-peers', views.BGPPeerViewSet)
router.register('bgp-peer-groups', views.BGPPeerGroupViewSet)
router.register('vnis', views.VNIViewSet)
router.register('vxlans', views.VXLANViewSet)
router.register('isis-configs', views.ISISConfigViewSet)
router.register('static-routes', views.StaticRouteViewSet)

urlpatterns = router.urls