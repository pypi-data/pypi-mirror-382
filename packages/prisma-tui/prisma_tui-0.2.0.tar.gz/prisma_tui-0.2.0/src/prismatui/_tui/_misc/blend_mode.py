from enum import Enum, auto

# //////////////////////////////////////////////////////////////////////////////
class BlendMode(Enum):
    """Enum for layer blending modes. Defines how layers are blended when drawn."""
    OVERLAY = auto() # Default blending mode, overlays the layer on top of the existing pixels.
    OVERWRITE = auto() # Overwrites the existing pixels with the new layer's pixels.
    MERGE_ATTR = auto() # Merges the attributes of the new layer with the existing pixels, preserving the characters.
