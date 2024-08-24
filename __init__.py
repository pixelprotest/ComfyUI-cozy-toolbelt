from .nodes.cubemap_to_spherical import NODE_CLASS_MAPPINGS as CUBEMAP_NODE_CLASS_MAPPINGS
from .nodes.cubemap_to_spherical import NODE_DISPLAY_NAME_MAPPINGS as CUBEMAP_NODE_DISPLAY_NAME_MAPPINGS
from .nodes.spherical_to_cubemap import NODE_CLASS_MAPPINGS as SPHERICAL_NODE_CLASS_MAPPINGS
from .nodes.spherical_to_cubemap import NODE_DISPLAY_NAME_MAPPINGS as SPHERICAL_NODE_DISPLAY_NAME_MAPPINGS

NODE_CLASS_MAPPINGS = {
    **CUBEMAP_NODE_CLASS_MAPPINGS,
    **SPHERICAL_NODE_CLASS_MAPPINGS,
    # Add other node mappings here as you create more nodes
}

NODE_DISPLAY_NAME_MAPPINGS = {
    **CUBEMAP_NODE_DISPLAY_NAME_MAPPINGS,
    **SPHERICAL_NODE_DISPLAY_NAME_MAPPINGS,
    # Add other display name mappings here as you create more nodes
}
