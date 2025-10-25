from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper
from StreamDeck.Transport.Transport import TransportError
import os
import threading
import yaml
from napari.layers import Image, Labels, Points, Shapes, Tracks
from PIL import Image as PIL_Image
from napari import Viewer
from StreamDeck.Devices.StreamDeck import StreamDeck
import numpy as np
from collections import defaultdict
# from typing import Union 


# paths
ASSETS_PATH = os.path.join(os.path.dirname(__file__), "resources")
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config")

# controller class
class BoundController:
    def __init__(
            self, 
            deck: StreamDeck, 
            viewer: Viewer, 
            viewer_menu: bool = False, 
            layer_view: bool = True,
            remember_page: bool = True,
            ):
        '''
        Description: Class assigning actions and media to streamdeck keys, 
        dials, and touch screen

        Attributes: 
        -----------
        deck: StreamDeck class or subclass 
            #TODO check typing logic for this might need Union?
        viewer: napari Viewer 
        viewer_menu: bool
            Is the key menu for the viewer currently active? Otherwise, 
            the menu applicable to the currently selected layer will be visible.
            This will facilitate toggleable tools and selection of boolean 
            settings. 
        layer_view: bool
            Are the layer list and axis positions visible on touch screen with
            dials used for scrolling through axes. Otherwise, the dial view 
            will be shown. Dials will change values for integer or categorical
            tools / options in napari. 
        remember_page: bool
            Remember which page you were last on when returning to a given menu 
            after switching between pages. 
        
        Private Attributes:
        -------------------
        _key_media: dict
            assigns all napari tools that can be mapped to keys to an internal
            icon file for when the button is unselected and when it is selected. 
        _dial_settings: dict
            dict representing config file for dials
        _key_settings: dict
            dict representing config file for keys
        _bindings: dict
            dict representing config file for streamdeck, actions, napari 
            function str bindings
        _key_media: dict
            dict holding file paths to icons corresponding to specific napari 
            function str
        _key_icons: dict
            dict holding np arrays for RGB icons corresponding to specific 
            napari function str

        

        '''
        # set the all important central attributes
        self.deck = deck
        self.viewer = viewer
        # load in config files as private dict
        self.dial_n, self.key_n, self.bindings_n = 'dial_settings.yaml', 'key_icon_assignment.yaml', 'napari_bindings.yaml'
        self._dial_settings = open_yaml(CONFIG_PATH, self.dial_n)['settings']
        self._key_settings = open_yaml(CONFIG_PATH, self.key_n)['settings']
        self._bindings = open_yaml(CONFIG_PATH, self.key_n)['menus']
        # menu assignments
        self._menu_assignments = {
            Image : 'image_menu', 
            Labels : 'lables_menu', 
            Points : 'points_menu', 
            Shapes : 'shapes_menu', 
            Tracks : 'tracks_menu', 
            None : 'viewer_menu'
        }

        # setup configuration
        # -------------------
        self.viewer_menu = viewer_menu
        self.layer_view = layer_view # start in layer view w layer selection on ts
        self._key_media = {}
        self._get_key_media_paths() # finds icons for each possible key
            # assigns to self.key_media
        self._key_icons = {}
        self._load_key_icons() # loads icons into numpy arrays held under 
            # name strs in _key_icons

        # setup page settings
        # -------------------
        self.remember_page = remember_page
        self._current_layer_page = 0 # page on touch screen for layer icons (layer_view = True)
        self._add_page_info()
        self._set_active_menu() # assigns keys to active layer
        self._active_keys = None 
        self._set_active_keys() # assign _active_keys
        self._active_dials = None
        self._set_active_dials() # assign _active_dials
        self._visible_layers = None
        # assign _visible_layers
        

        # Setup streamdeck display
        # ------------------------


    # ------------------
    # Load configuration
    # ------------------

    def _set_active_menu(self):
        if not self.viewer_menu:
            active = type(self.viewer.selection.active)
            active = self._menu_assignments[active]
        if self.viewer_menu:
            active = 'viewer_menu'
        self.active_menu = active


    def _refresh_deck_display(self):
        if not self.dial_view:
            pass
            # touchscreen in layerview
        if self.dial_view:
            pass # touchscreen in layer
        
        # set keys 
        pass


    def _get_key_media_paths(self):
        for k in self._key_bindings:
            value = k['value']
            p = self._key_bindings[value].get('unselected')
            sp = self._key_bindings[value].get('selected')
            if p is None and sp is None:
                m = "Please ensure for each entry under settings in resources/key_icon_assignment.yaml " \
                "there is a filename for at least one of selected and unselected "
                raise ValueError(m)
            if sp is None:
                sp = p
            if p is None:
                p = sp
            self.key_media[k['key_id']] = [p, sp]
    

    def _load_key_icons(self):
        if len(self._key_media) == 0:
            self._get_key_media_paths()
        for v, ps in self._key_media.items():
            icon = Image.open(ps[0])
            icon_on = Image.open(ps[1])
            self._key_icons[v] = [icon, icon_on]
    

    def _add_page_info(self):
        '''
        Provide page divided bindings information
        '''
        for menu, info in self._bindings.items():
            # add dict with page divided lists
            # {'page_bindings' : [
            #     {'key_id': 0, 
            #      'action_id': 'streamdeck:toggle_dialview',
            #      'value': 'toggle_dialview'}, 
            #       ...]
            #      [ ... 
            #           <the same stuff subdivided into list for next page>
            #        ]}
            page_divided_bindings_info(info, menu, self, 8, 'key')
            page_divided_bindings_info(info, menu, self, 4, 'dial')
        

    def _set_active_keys(self):
        '''
        Set the list of key bindings for the current active menu/page (8)
            [{'key_id': 0, 'action_id': 
            'streamdeck:toggle_dialview', 
            'value': 'toggle_dialview'}, ...] --> len = 8
        '''
        page = self._bindings[self.active_menu][f'current_key_page']
        binds = self._bindings[self.active_menu]['key_binds']['page_bindings']
        self._active_keys = binds[page]
        for k in self._active_keys:
            icons = self._key_icons[k['value']]
            k['icon'] = icons[0]
            k['icon_on'] = icons[1]


    def _set_active_dials(self):
        '''
        Set the list of dial bindings for the current active menu/page (4)
        '''
        page = self._bindings[self.active_menu][f'current_dial_page']
        binds = self._bindings[self.active_menu]['dial_binds']['page_bindings']
        self._active_dials = binds[page]

    
    def _update_layer_list_info(self):
        pass
        
        
            

    # -----------------
    # Update Streamdeck
    # -----------------

    def _update_keys(self):
        for k in self._active_keys:
            with self.deck:
                on = self.viewer.layers.selection[0].mode == k['value']
                if on:
                    self.deck.set_key_image(k['key_id'], k['icon_on'])
                else:
                    self.deck.set_key_image(k['key_id'], k['icon'])


    def _update_touchscreen(self):
        # will leave touch screen visuals until after touchscreen events managing is established
        if not self.layer_view:
            pass # dial icons

        if self.layer_view:
            pass # layer list and axis sliders


    # -------------
    # Update Napari
    # -------------
        


    # ------------------
    # Edit configuration
    # ------------------


    def edit_dial_settings():
        pass


    def edit_key_settings():
        pass




# ---------
# Utilities 
# ---------

def open_yaml(n, d):
    p = os.path.join(d, n)
    with open(p, "r") as file:
        data = yaml.safe_load(file)
    return data


def page_divided_bindings_info(info, menu, self, n_per_page, name):
    n_pages = np.ceil(len(info[f'{name}_binds'])/ n_per_page).astype(int)
    self._bindings[menu][f'current_{name}_page'] = 0
    menu_key_pages = {i : [] for i in n_pages}
    for i, v in enumerate(info[f'{name}_binds']):
        page = np.floor(i / n_per_page).astype(int)
        menu_key_pages[page].append(v)
    info['page_bindings'] = menu_key_pages 




