from netbox.plugins import PluginConfig

class NetBoxRoutingComplexConfig(PluginConfig):
    name = 'netbox_routing_complex'
    verbose_name = 'Complex Routing'
    description = 'Manage complex routing in Netbox'
    version = '0.2'
    base_url = 'netbox-routing-complex'
    min_version = "4.4.0"

config = NetBoxRoutingComplexConfig