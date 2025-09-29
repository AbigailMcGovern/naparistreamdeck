from functools import partial
from typing import Callable, Optional
from app_model import Application
from app_model.types import Action, ToggleRule
from napari.components import LayerList
from napari.layers.image import Image
from napari.layers.labels import Labels
from napari.layers.labels._labels_constants import Mode
from napari.viewer import Viewer


# ----------
# Dial tools
# ----------

# Axis (keymode)
# --------------


# Viewer
# ------

# Lables
# ------

# Image
# -----

# Shapes
# ------

# Points
# ------

# Tracks
# ------


# ---------
# Key tools
# ---------


# Viewer
# ------

def toggle_2d_3d(ll: LayerList) -> None:
    pass


# Lables
# ------

# Image
# -----

# Shapes
# ------

# Points
# ------

# Tracks
# ------


# --------------
# Custom Actions
# --------------

CUSTOM_ACTIONS = [

    Action(
        id='napari:viewer:toggle_2d_3d', 
        title='toggle between 2D and 3D camera views',
        callback=toggle_2d_3d
    )

]