from netbox.plugins import PluginMenu, PluginMenuItem, PluginMenuButton
#^this doesn't match the tutorial because the latest api has rearranged things into the netbox namespace per below
#https://netboxlabs.com/docs/netbox/plugins/development/navigation/

#simply add a new plugin menu item to this file per endpoint that you want to be accessible via the left panel; these use the view names from urls.py for their link
bfdconfig_menu_with_add_button = PluginMenuItem(
    link = 'plugins:netbox_routing_complex:bfdconfig_list',
    link_text = 'BFD Configs',
    buttons = (
            PluginMenuButton(
                link='plugins:netbox_routing_complex:bfdconfig_add',
                title='Add',
                icon_class='mdi mdi-plus-thick',
                ),
            )
)

bgpglobalconfig_menu_with_add_button = PluginMenuItem(
    link = 'plugins:netbox_routing_complex:bgpglobalconfig_list',
    link_text = 'BGP Global Configs',
    buttons = (
            PluginMenuButton(
                link='plugins:netbox_routing_complex:bgpglobalconfig_add',
                title='Add',
                icon_class='mdi mdi-plus-thick',
                ),
            )
)

bgpsessionconfig_menu_with_add_button = PluginMenuItem(
    link = 'plugins:netbox_routing_complex:bgpsessionconfig_list',
    link_text = 'BGP Session Configs',
    buttons = (
            PluginMenuButton(
                link='plugins:netbox_routing_complex:bgpsessionconfig_add',
                title='Add',
                icon_class='mdi mdi-plus-thick',
                ),
            )
)

bgppeer_menu_with_add_button = PluginMenuItem(
    link = 'plugins:netbox_routing_complex:bgppeer_list',
    link_text = 'BGP Peers',
    buttons = (
            PluginMenuButton(
                link='plugins:netbox_routing_complex:bgppeer_add',
                title='Add',
                icon_class='mdi mdi-plus-thick',
                ),
            )
)

bgppeergroup_menu_with_add_button = PluginMenuItem(
    link = 'plugins:netbox_routing_complex:bgppeergroup_list',
    link_text = 'BGP Peer Groups',
    buttons = (
            PluginMenuButton(
                link='plugins:netbox_routing_complex:bgppeergroup_add',
                title='Add',
                icon_class='mdi mdi-plus-thick',
                ),
            )
)

vni_menu_with_add_button = PluginMenuItem(
    link = 'plugins:netbox_routing_complex:vni_list',
    link_text = 'VNIs',
    buttons = (
            PluginMenuButton(
                link='plugins:netbox_routing_complex:vni_add',
                title='Add',
                icon_class='mdi mdi-plus-thick',
                ),
            )
)

vxlan_menu_with_add_button = PluginMenuItem(
    link = 'plugins:netbox_routing_complex:vxlan_list',
    link_text = 'VXLANs',
    buttons = (
            PluginMenuButton(
                link='plugins:netbox_routing_complex:vxlan_add',
                title='Add',
                icon_class='mdi mdi-plus-thick',
                ),
            )
)

isisconfig_menu_with_add_button = PluginMenuItem(
    link = 'plugins:netbox_routing_complex:isisconfig_list',
    link_text = 'ISIS Configs',
    buttons = (
            PluginMenuButton(
                link='plugins:netbox_routing_complex:isisconfig_add',
                title='Add',
                icon_class='mdi mdi-plus-thick',
                ),
            )
)

staticroute_menu_with_add_button = PluginMenuItem(
    link = 'plugins:netbox_routing_complex:staticroute_list',
    link_text = 'Static Routes',
    buttons = (
            PluginMenuButton(
                link='plugins:netbox_routing_complex:staticroute_add',
                title='Add',
                icon_class='mdi mdi-plus-thick',
                ),
            )
)

menu = PluginMenu(
    label='Complex Routing',
    groups = (
        ('ISIS', (isisconfig_menu_with_add_button,)),
        ('BGP', (bgpglobalconfig_menu_with_add_button, bgpsessionconfig_menu_with_add_button, bgppeer_menu_with_add_button, bgppeergroup_menu_with_add_button,)),
        ('VXLAN', (vni_menu_with_add_button, vxlan_menu_with_add_button,)),
        ('Misc', (staticroute_menu_with_add_button, bfdconfig_menu_with_add_button,)), #Misc is the subcategory name in the left panel, note that each subpanel is a tuple where the second value is also a tuple of PluginMenuItem instances
    ),
    icon_class='mdi mdi-router'
)

