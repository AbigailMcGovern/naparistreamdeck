from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.Devices.StreamDeck import DialEventType, TouchscreenEventType
import os
import napari
import numpy as np
import napari.layers.labels.labels as nlabs
import napari.layers.image.image as nimg
from toolz import curry

@curry
def touchscreen_event_callback(touchscreen, deck, evt_type, value):
    if evt_type == TouchscreenEventType.SHORT or evt_type == TouchscreenEventType.LONG:
        touchscreen.short_touch_event(value)

    elif evt_type == TouchscreenEventType.DRAG:
        pass


class TouchScreen:

    def __init__(self, viewer: napari.Viewer) -> None:
        self.view = "layerview" # layerview or dialview... always instantiate on layerview
        self.viewer = viewer
        self.screendims = (100, 800)
        self.screen_page = 0
        self.build_and_set_screens() # sets layerlist_screen, axis_screen, and dial_screen attributes
        self.build_touchscreen_image() # sets touchscreen_image attribute
        self.screen_lut = self.get_shorttouch_screen_LUT() # list of array
        self.dialview_lut = self.get_dialview_LUT()
        

    def build_and_set_screens(self):
        """
        Builds and sets the screens for the current layer type and layerout
        """
        self.layerlist_screen = self.build_layerlist_screen() # list of array
        self.axis_screen = self.build_axis_screen() # array
        self.dial_screen = self.build_dial_screen() # list of array

    
    def update_axis_screen(self):
        pass


    def build_touchscreen_image(self):
        """
        Build and set the touchscreen image for the current page displayed. 
        
        TODO: finish this
        """
        self.update_axis_screen()
        self.touchscreen_image = ...
        

    def build_layerlist_screen(self):
        """
        Generate the RGB array representing the image on the top part of the touch screen
        (i.e., a ... x ... pixel area). The image comprises the layer thumbnails on 
        a grey background (the colour of the napari window with the default theme). 
        If there are too many thumbnails, several screens will be built and stored. 

        TODO: connect this to callbacks indicating that the layer list has changed or
        the current selection has changed. 
        """

        # we will have four 90 x 200 pixel regions for up to four layers on the screen at
        # any one time. There will be a 2 pixel boarder around each one. The selected layer
        # will have a white boarder and the others will have grey. For each layer, there 
        # will be a 86 x 86 thumbnail on the left hand side. On the other side there will
        # be a slightly lighter gray region (matching they layerlist icons) with the index
        # of the layer displayed. 
        pass


    def build_axis_screen(self):
        """
        Generate the RGB array representing the bottom part of the touch screen. 
        On this part of the screen, the user can see the location of the sliders on any
        axes currently opperated by sliders. 
        """
        pass


    def build_dial_screen(self):
        pass

    
    def get_shorttouch_screen_LUT(self):
        """
        Using the layerlist, information about axis display, and the current page
        viewed on the touch screen, build a lookup table for the touch screen to determine
        which actions should be applied for touches at different coordinates on the
        screen. 

        Returns
        -------
        screen_lut: array 
            touch screeen coordiates can index into this array to choose a layer to
            become the new active layer
        dial_lookup_table: dict 
            mapping of label numbers to functions which will be applied 
            when the screen is touch in a certain location

        TODO: connect this to callbacks indicating that the layer list has changed
        """
        layers = self.viewer.layers
        nlayers = len(layers)
        npages = len(self.layerlist_screen)
        # build a numpy array of the same dimention as the touch screen that indexes
        # into the layerlist to help set the right layer.
        screen_labels = [np.zeros((100, 800), int) for i in range(npages)]
        # we will have up to four 90 x 200 pixel layers on the screen at a given time
        # any smaller will be too small 
        y0 = 0
        y1 = 90
        for i in range(nlayers):
            page = np.floor_divide(i, 4).astype(int)
            pos = i % 4
            x1 = pos * 200
            x0 = x1 - 200
            screen_labels[page][y0:y1, x0:x1] = i
        return screen_labels


    def get_dialview_LUT(self):
        # if the current layer is an image layer
        if isinstance(self.viewer.layers.selection.active, nimg.Image):
            pass
        # if the current layer is a labels layer
        if isinstance(self.viewer.layers.selection.active, nlabs.Labels):
            pass


    def change_active_layer(self, value):
        """
        Change the active layer based on a short touch event
        """
        x, y = value['x'], value['y'] # value supplied with TouchscreenEventType.SHORT event
        idx = self.screen_lut[self.screen_page][y, x]
        self.viewer.layers.selection.active = self.viewer.layers[idx]


    def short_touch_event(self, value):
        if self.view == 'layerview':
            self.change_active_layer(value)

        elif self.view == 'dialview':
            pass


    def drag_event(self, value):
        if self.view == 'layerview':
            pass

        elif self.view == 'dialview':
            pass


