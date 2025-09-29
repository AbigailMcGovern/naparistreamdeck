from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.Devices.StreamDeck import DialEventType, TouchscreenEventType
import os
import napari
import numpy as np
import napari.layers.labels.labels as nlabs
import napari.layers.image.image as nimg
from toolz import curry
from skimage.color import rgba2rgb
from PIL import Image, ImageDraw, ImageFont
from collections import defaultdict
from .utils import draw_number, read_resource, check_for_multidial

@curry
def touchscreen_event_callback(touchscreen, deck, evt_type, value):
    if evt_type == TouchscreenEventType.SHORT or evt_type == TouchscreenEventType.LONG:
        touchscreen.short_touch_event(value)

    elif evt_type == TouchscreenEventType.DRAG:
        pass


class TouchScreen:

    def __init__(self, viewer: napari.Viewer) -> None:
        # some basic variables
        self.view = "layerview" # layerview or dialview... always instantiate on layerview
        self.viewer = viewer
        self.screendims = (100, 800)
        self.screen_page = 0
        # axis pixel conversion info
        self.ax_pix_per_step = []
        self.ax_remainder = []
        self.ax_current_pix = []
        # build image grids
        self.layer_screen_list = None
        self.dial_screen_list = None
        self.axis_screen = None
        self.touchscreen_image = None
        # LUTs
        screen_lut, dial_lut = self.get_shorttouch_screen_LUT() # list of array
        self.screen_lut = screen_lut
        self.dial_lut = dial_lut
        # build screns
        self.build_and_set_screens() # sets layer_screen_list, axis_screen, and dial_screen_list attributes
        self.build_touchscreen_image() # sets touchscreen_image attribute
        

    def build_and_set_screens(self):
        """
        Builds and sets the screens for the current layer type and layerout
        """
        self.build_axis_screen() # array
        self.build_layerlist_screen() # list of array
        self.build_dial_screen() # list of array


    def build_touchscreen_image(self):
        """
        Build and set the touchscreen image for the current page displayed. 
        
        TODO: finish this
        """
        if self.view == 'layerview':
            top = self.layerlist_screen[self.screen_page]
        elif self.view == 'dialview':
            top = self.dial_screen_list[self.screen_page]
        self.touchscreen_image = np.zeros(100, 800, 3)
        self.touchscreen_image[:90, :, :] = top
        self.touchscreen_image[90:, :, :] = self.axis_screen
        

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

        # 32 x 32 pix images with rgba colour + 50 x 50 image showing layer number
        layer_data = {i : {'thumb' : rgba2rgb(l.thumbnail), 'numb' : draw_number(i)} \
                      for i, l in enumerate(self.viewer.layers)} 
        # NB the layer number will be improved. White background for now.
        # thumbnail starts at (34, 11), number starts at (25, 50)
        # there will be a 4 px border around the left, top, and bottom sides of each region
        # areas not claimed by the layer list will be the colour of the border. 
        n_layers = len(layer_data)
        n_pages = np.floor_divide(n_layers, 8) + 1
        layer_screen_list = [np.zeros((90, 800, 3), dtype=int) for _ in range(n_pages)]
        background_colour = np.array([101, 101, 102])
        tile_colour = ... #TODO pick a colour
        for page in layer_screen_list:
            page[:, :, :] = tile_colour
            page[0:4, :, :] = background_colour
            page[-4:, :, :] = background_colour
        for i in range(n_layers):
            page_i = np.floor_divide(i, 8) 
            #tile_i = i % 8
            start_x = i * 100
            layer_screen_list[page_i][34:67, start_x:start_x + 32, :] = layer_data[i]['thumb']
            layer_screen_list[page_i][25:75, start_x:start_x + 50, :] = layer_data[i]['numb']
            layer_screen_list[page_i][:, start_x:start_x + 4, :] = background_colour
        self.layer_screen_list = layer_screen_list



    def build_axis_screen(self):
        """
        Generate the RGB array representing the bottom part of the touch screen. 
        On this part of the screen, the user can see the location of the sliders on any
        axes currently opperated by sliders. 
        """
        # if the viewer is displaying data
        if len(self.viewer.layers) > 0:
            # set up
            # ------
            # get the displayed axes
            ndim = self.viewer.dims.ndim
            ndisplayed = self.viewer.dims.ndisplay
            order = self.viewer.dims.order
            n_sliders = ndim - ndisplayed
            n_sliders = n_sliders if n_sliders < 3 else 2
            dims = order[:n_sliders]
            extent = self.viewer.dims.nsteps[dims]
            current_step = self.viewer.dims.current_step[dims]
            if len(self.ax_pix_per_step) == 0:
                self.ax_pix_per_step = [np.floor_divide(800, e).astype(int) for e in extent]
            if len(self.ax_remainder) == 0:
                self.ax_remainder = [800 % e for e in extent]
            self.ax_current_pix = [px * c for px, c in zip(self.ax_pix_per_step, current_step)]
            

            # Build screen
            # ------------
            # colours for building RGB picture
            past_colour = np.array([67, 135, 230])
            future_colour = np.array([63, 63, 64])
            border_colour = np.array([101, 101, 102])
            # instantiate RGB image
            axscreen = np.zeros((10, 800, 3)) 
            # paint borders into picture
            axscreen[:, 1, :] = border_colour # first column
            axscreen[1, :, :] = border_colour # top row
            axscreen[-1, :, :] = border_colour # bottom row
            for i, r in enumerate(self.ax_remainder):
                rows = slice(start=i * 5, stop=i * 5 + 5, step=None) 
                axscreen[rows, -r:, :] = border_colour
            for i, cp in enumerate(self.ax_current_pix):
                rows = slice(start=i * 5, stop=i * 5 + 5, step=None) 
                # paint the past (i.e., scrolled through already) colour in
                axscreen[rows, :cp, :] = past_colour
                axscreen[rows, -cp:, :] = future_colour
            # paint the future (i.e., what you would scroll through to get to the extent) colour in
        
        else:
            pass
        
        # set internal variable
        self.axis_screen = axscreen


    def update_axis_screen(self):
        """
        Generate the RGB array representing the bottom part of the touch screen. 
        On this part of the screen, the user can see the location of the sliders on any
        axes currently opperated by sliders. 

        TODO: connect this to events so as to update when slider is moved or new data is added
        to the viewer
        """
        self.axis_screen = self.build_axis_screen(self)
        pass


    def build_dial_screen(self):
        """
        Generate the RGB array representing the top part of the touchscreen when in 
        dialview. This will show the icons representing each dial option. 

        Image layer
        -----------
        PAGE 1
        1: opacity 
        2: 'contrast', 
        3: 'gamma', 
        4: 'colour map'
        
        PAGE 2
        1: 'blending', 
        2: 'interpolation', 
        3: 'depiction', 
        4: 'rendering'

        Labels layer
        ------------
        PAGE 1
        1 : 'label'
        2 : 'opacity'
        3 : 'brush size'
        4 : 'blending'
        
        PAGE 2
        1: 'contor', 
        2 : 'edit dimensions'

        """
        # the icons in the resources folder are 66 x 66 px
        # icons of these dims will begin at (17, 67)
        # need icons for: opacity, contrast, gamma, colourmap, 'blending', 'interpolation'
        #    'depiction', 'rendering', 'label', 'brush size', 'contor', 'edit dimensions'
        
        n_pages = len(self.dial_lut) # is a list containing dicts that map icons to dials for each page
        dial_screen = []
        for i in range(n_pages):
            screen = np.zeros((90, 800, 3), dtype=int)
            lut = self.dial_lut[i]
            for j in range(len(lut)):
                dial = lut[i]
                multidial = check_for_multidial(dial)
                if not multidial:
                    img = read_resource(dial)
                    




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
            page = np.floor_divide(i, 8).astype(int)
            pos = i % 8
            x1 = pos * 100
            x0 = x1 - 100
            screen_labels[page][y0:y1, x0:x1] = i
        return screen_labels


    def get_dialview_LUT(self):
        # if the current layer is an image layer
        if isinstance(self.viewer.layers.selection.active, nimg.Image):
            icon_lut = [
                {
                    1: 'opacity', 
                    2: 'contrast', 
                    3: 'gamma', 
                    4: 'colourmap'
                },
                {
                    1: 'blending', 
                    2: 'interpolation', 
                    3: 'depiction', 
                    4: 'rendering'
                }
            ]
        # if the current layer is a labels layer
        if isinstance(self.viewer.layers.selection.active, nlabs.Labels):
            if isinstance(self.viewer.layers.selection.active, nimg.Image):
                icon_lut = [{
                    1 : 'label', 
                    2 : 'opacity', 
                    3 : 'brush_size',
                    4 : 'blending', 
                }, 
                {
                    1: 'contor', 
                    2 : 'edit_dimensions'
                }
                ]


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
            pass # no functionality for now


    def drag_event(self, value):
        start_x = value['x']
        stop_x = value['x_out']
        forward = start_x < stop_x
        self.change_current_page(forward)
        if self.view == 'layerview':
            pass
        elif self.view == 'dialview':
            pass

        
    def change_current_page(self, forward):
        n_pages = len(self.screen_lut)
        if self.screen_page + 1 < n_pages and forward:
            self.screen_page += 1
        elif self.screen_page > 0 and not forward:
            self.screen_page -= 1
        else: pass


