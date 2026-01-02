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
from .custom_actions import CUSTOM_ACTIONS
from superqt.utils import ensure_main_thread


# paths
ASSETS_PATH = os.path.join(os.path.dirname(__file__), "resources")
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config")

# controller class
class BoundController:
    def __init__(
            self, 
            deck: StreamDeck, 
            viewer: Viewer, 
            actions: list = CUSTOM_ACTIONS,
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
        actions: list
            custom actions
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
        self._bindings = open_yaml(CONFIG_PATH, self.bindings_n)['menus']
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
        self._load_key_icons() # loads icons into numpy arrays held in key settings
            # self._key_settings[value]['unselected_icon'] & self._key_settings[value]['selected_icon']

        # setup page settings
        # -------------------
        self.remember_page = remember_page
        self._add_page_info()
        self._set_active_menu() # assigns keys to active layer
        self._active_keys = None 
        self._set_active_keys() # assign _active_keys
        self._active_dials = None
        self._set_active_dials() # assign _active_dials
        self._touchscreen_layer_info = None
        self._update_layer_list_info() # assign _touchscreen_layer_info

        # Setup streamdeck display
        # ------------------------
        self._update_keys()
        self._update_touchscreen()


    # ------------------
    # Load configuration
    # ------------------



    def _load_key_icons(self):
        '''
        Load key media into memory - since the icons are tiny this should be perfectly efficient
        '''
        for k in self._key_settings:
            value = k['value']
            up = self._key_settings[value].get('unselected')
            up = os.path.join(ASSETS_PATH, up)
            sp = self._key_settings[value].get('selected')
            sp = os.path.join(ASSETS_PATH, sp)
            u_icon = Image.open(up)
            self._key_settings[value]['unselected_icon'] = u_icon
            s_icon = Image.open(sp)
            self._key_settings[value]['selected_icon'] = s_icon



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
            page_divided_bindings_info(info, menu, self, 7, 'key')
            # N per page 7 as 8th slot is for "next page" button TODO ensure consistancy in config file
            # TODO fix edge case (last page can have 8)
            page_divided_bindings_info(info, menu, self, 4, 'dial')
            # of course use all 4 dials - TODO swipe for next page - should be simple to define on touch pad


    def _set_active_menu(self):
        if not self.viewer_menu:
            active = type(self.viewer.selection.active)
            active = self._menu_assignments[active]
        if self.viewer_menu:
            active = 'viewer_menu'
        self.active_menu = active



    def _set_active_keys(self):
        '''
        Set the list of key bindings for the current active menu/page (8)
            [{'key_id': 0, 'action_id': 
            'streamdeck:toggle_dialview', 
            'value': 'toggle_dialview'}, ...] --> len = 8
        '''
        page = self._bindings[self.active_menu]['current_key_page']
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
        # layers - pageified 
        # thumbnails
        # current page
        # 800 pixels wide fyi
        active_layer = self.viewer.selection.active.name
        ll =  self.viewer.layers
        n_pages = np.ceil(ll / 7).astype(int)
        layer_info = {i: [] for i in range(n_pages)}
        active_info = {}
        for i, l in enumerate(ll):
            page = np.floor(i / 7).astype(int)
            layer_info[page].append(l.thumbnail)
            if l.name == active_layer:
                active_info['page'] = page # 7 layers to display thumbnails for
                active_info['i'] = i % 7 # gives info for indexing onto page of 7 - needed for diplaying selected
        layer_info['active'] = active_info
        self._touchscreen_layer_info = layer_info



    def _set_button_values(self):
        '''
        Function to set initial state for napari button values
        '''
        # find viewer active layer
        l = ...



    def _refresh_deck_display(self):
        if not self.dial_view:
            pass
            # touchscreen in layerview
        if self.dial_view:
            pass # touchscreen in layer
        
        # set keys 
        pass
            

    # -----------------
    # Update Streamdeck
    # -----------------

    def _update_keys(self):
        for k in self._active_keys:
            with self.deck:
                on = self.viewer.layers.selection.active.mode == k['value']
                if on:
                    self.deck.set_key_image(k['key_id'], k['icon_on'])
                else:
                    self.deck.set_key_image(k['key_id'], k['icon'])
                    #TODO how to incorporate on vs off state info


    def _update_touchscreen(self):
        # will leave touch screen visuals until after touchscreen events managing is established
        if not self.layer_view:
            pass # dial icons

        if self.layer_view:
            pass # layer list and axis sliders


    # -------------
    # Update Napari
    # -------------
    def _key_change_callback(self, deck, key, state):
        # Don't try to draw an image on a touch button
        if key >= deck.key_count():
            return
        
        # SET IMAGE BASED ON TOGGLED ON OR OFF
        # ------------------------------------
        # Update the key image based on the new key state.
        update_key_image(deck, key, state)

        # FROM TEST EXAMPLE
        # In test example got different emojis if pressed vs not
        # here we want to toggle 
        if state:
            pass
            key_style = get_key_style(deck, key, state)
            # When an exit button is pressed, close the application.
            if key_style["name"] == "exit":
                # Use a scoped-with on the deck to ensure we're the only thread
                # using it right now.
                with deck:
                    # Reset deck, clearing all button images.
                    deck.reset()
    
                    # Close deck handle, terminating internal worker threads.
                    deck.close()

        # NAPARI CUSTOM ACTIONS
        # ---------------------
        # Rules for buttons each time button is set to 1, += 1 
        pass



    @ensure_main_thread(await_return=True)    
    def _handle_key_push(self, key_value:int):
        k = self._active_keys
        self.deck.set_key_callback(self._key_change_callback)


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


def update_key_image(deck, key, image):
    with deck:
        # Update requested key with the generated image.
        deck.set_key_image(key, image)


def update_button_value(button_val, state):
    button_val += state
    button_val = button_val % 1
    return button_val

