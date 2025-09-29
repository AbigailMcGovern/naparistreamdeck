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

def toggle_2d_3d(v: Viewer) -> None:
    pass


def change_axis_order(v: Viewer) -> None:
    pass


def transpose_visible_axis(v: Viewer) -> None:
    pass


def toggle_grid(v: Viewer) -> None:
    pass


def restore_default_view(v: Viewer) -> None:
    pass


def show_terminal(v: Viewer) -> None:
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
    ), 

    Action(
        id='napari:viewer:change_axis_order', 
        title='change order of visible axes',
        callback=change_axis_order
    ), 

    Action(
        id='napari:viewer:transpose_visible_axis', 
        title='transpose oreder of last two visible axes',
        callback=transpose_visible_axis
    ), 

    Action(
        id='napari:viewer:toggle_grid', 
        title='toggle grid mode',
        callback=toggle_grid
    ), 

    Action(
        id='napari:viewer:restore_default_view', 
        title='reset view to original state',
        callback=restore_default_view
    ), 

    Action(
        id='napari:viewer:show_terminal', 
        title='toggle show Python terminal',
        callback=show_terminal
    ), 

]