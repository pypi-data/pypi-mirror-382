from netbox.views import generic
from . import forms, models, tables, filtersets

#Create four view for each object
#1. Detail view for a single object
#2. List view for all existing instances of the model
#3. Edit view for adding/modifying objects
#4. Delete view for deleting objects

#detail view
class BFDConfigView(generic.ObjectView):
    queryset = models.BFDConfig.objects.all()

#list view
class BFDConfigListView(generic.ObjectListView):
    queryset = models.BFDConfig.objects.all()
    table = tables.BFDConfigTable

#edit/modification view
class BFDConfigEditView(generic.ObjectEditView):
    queryset = models.BFDConfig.objects.all()
    form = forms.BFDConfigForm

#delete view
class BFDConfigDeleteView(generic.ObjectDeleteView):
    queryset = models.BFDConfig.objects.all()



# BGP Session Config Views
class BGPSessionConfigView(generic.ObjectView):
    queryset = models.BGPSessionConfig.objects.all()

class BGPSessionConfigListView(generic.ObjectListView):
    queryset = models.BGPSessionConfig.objects.all()
    table = tables.BGPSessionConfigTable

class BGPSessionConfigEditView(generic.ObjectEditView):
    queryset = models.BGPSessionConfig.objects.all()
    form = forms.BGPSessionConfigForm

class BGPSessionConfigDeleteView(generic.ObjectDeleteView):
    queryset = models.BGPSessionConfig.objects.all()


# BGP Peer Views
class BGPPeerView(generic.ObjectView):
    queryset = models.BGPPeer.objects.all()

class BGPPeerListView(generic.ObjectListView):
    queryset = models.BGPPeer.objects.all()
    table = tables.BGPPeerTable

class BGPPeerEditView(generic.ObjectEditView):
    queryset = models.BGPPeer.objects.all()
    form = forms.BGPPeerForm

class BGPPeerDeleteView(generic.ObjectDeleteView):
    queryset = models.BGPPeer.objects.all()



# BGP Peer Group Views
class BGPPeerGroupView(generic.ObjectView):
    queryset = models.BGPPeerGroup.objects.all()

class BGPPeerGroupListView(generic.ObjectListView):
    queryset = models.BGPPeerGroup.objects.all()
    table = tables.BGPPeerGroupTable

class BGPPeerGroupEditView(generic.ObjectEditView):
    queryset = models.BGPPeerGroup.objects.all()
    form = forms.BGPPeerGroupForm

class BGPPeerGroupDeleteView(generic.ObjectDeleteView):
    queryset = models.BGPPeerGroup.objects.all()

# VNI Views
class VNIView(generic.ObjectView):
    queryset = models.VNI.objects.all()

class VNIListView(generic.ObjectListView):
    queryset = models.VNI.objects.all()
    table = tables.VNITable

class VNIEditView(generic.ObjectEditView):
    queryset = models.VNI.objects.all()
    form = forms.VNIForm

class VNIDeleteView(generic.ObjectDeleteView):
    queryset = models.VNI.objects.all()


# VXLAN Views
class VXLANView(generic.ObjectView):
    queryset = models.VXLAN.objects.all()

class VXLANListView(generic.ObjectListView):
    queryset = models.VXLAN.objects.all()
    table = tables.VXLANTable

class VXLANEditView(generic.ObjectEditView):
    queryset = models.VXLAN.objects.all()
    form = forms.VXLANForm

class VXLANDeleteView(generic.ObjectDeleteView):
    queryset = models.VXLAN.objects.all()


# ISIS Config Views
class ISISConfigView(generic.ObjectView):
    queryset = models.ISISConfig.objects.all()

class ISISConfigListView(generic.ObjectListView):
    queryset = models.ISISConfig.objects.all()
    table = tables.ISISConfigTable

class ISISConfigEditView(generic.ObjectEditView):
    queryset = models.ISISConfig.objects.all()
    form = forms.ISISConfigForm

class ISISConfigDeleteView(generic.ObjectDeleteView):
    queryset = models.ISISConfig.objects.all()



# BGP Global Config Views
class BGPGlobalConfigView(generic.ObjectView):
    queryset = models.BGPGlobalConfig.objects.all()

class BGPGlobalConfigListView(generic.ObjectListView):
    queryset = models.BGPGlobalConfig.objects.all()
    table = tables.BGPGlobalConfigTable

class BGPGlobalConfigEditView(generic.ObjectEditView):
    queryset = models.BGPGlobalConfig.objects.all()
    form = forms.BGPGlobalConfigForm

class BGPGlobalConfigDeleteView(generic.ObjectDeleteView):
    queryset = models.BGPGlobalConfig.objects.all()



# Static Route Views
class StaticRouteView(generic.ObjectView):
    queryset = models.StaticRoute.objects.all()

class StaticRouteListView(generic.ObjectListView):
    queryset = models.StaticRoute.objects.all()
    table = tables.StaticRouteTable
    filterset = filtersets.StaticRouteFilterSet
    filterset_form = forms.StaticRouteFilterForm

class StaticRouteEditView(generic.ObjectEditView):
    queryset = models.StaticRoute.objects.all()
    form = forms.StaticRouteForm

class StaticRouteDeleteView(generic.ObjectDeleteView):
    queryset = models.StaticRoute.objects.all()

