# Road Map for naparistreamdeck

The interface will rely on toggling between layers using the touch screen. The type of layer currently selected will determine which dials and buttons are available. The user will be able to toggle the view on the touch screen to enable the user to switch through different options for the dials (dial view) or see and switch between layers (layer view). When in layer view, the first two dials will operate the axis sliders.  

## General Plan
### User interface for streamdeck
- For each menu, the two leftmost buttons will be used to (1) toggle between button and key modes and (2) toggle between high-level controls and single layer controls. Later, higher-level controls may be split into separate menus for viewer and dims but we will keep it simple to start with. Camera controls may be split from layer controls but at present keeping this with layer controls because these determine the function of the cursor and functionally this reduces button pushing.  
- Key mode: dials will change axes, icons will have blue background for selected tools, radioboxes/buttons that are selected will have blue outline
- Dial mode: icons wil depict dials, if integer value (e.g., label number / colour), this will be displayed above dial. If slider position in slider will be shown where axis would be shown in key mode. If categorical, will show number of ticks depicting number of categories where axis sliders would be to show position in the list - ideally dial icon will represent setting chosen but this may be hard (may be good to show something when dial is being turned but htis is very low priority) 
- The order of items to ve decided on a practical basis. Does anyone have statistics on reletive uses of different buttons/controls?
- Higher level controls (key mode): toggle 2D/3D, change axis order, transpose visible axis, toggle grid, return settings, show terminal
- Higher level controls (dial mode): ?
- Labels layer controls (key mode): shuffle, eraser, paint brush, polygon tool, fill bucket, sample label, move, transformm continuous, show selected, preserve labs
- Labels layer controls (dial mode): opacity, blending, label, brush size, colour mode, contor, n edit dims
- Image layer controls (key mode): move, transform, toggle autocontrast,
- Image layer controls (dial mode): opacity, blending, contrast limit upper, contrast limit lower, gamma, colourmap, projection, interpolation
- Shapes layer controls (key mode): move to back, move to front, remove vertex, add vertex, add elipses, add rectangles, delete selected, select verticies, select shapes, add polygons lasso, add lines, add polylines, move camera, transform, display text
- Shapes layer controls (dial mode): opacity, blending, edge width, face colour, edge colour
- Points layer controls (key mode):
- Points layer controls (dial mode):
- Tracks layer controls (key mode):
- Tracks layer controls (dial mode):

### Widgets
- Eventually we want a Q dialogue for editing the layout and configuration of the streamdeck user interdface

### Code structure
- Mappings for keys and dials to napari settings will be contained within yaml files: one for binding controler buttons/dials to IDs and another for binding napari tools/settings to IDs (as per Midi app controler) 

## Old images

### Image Layer

![Draft showing current ideas for buttons, slider, and screen for image layer.](https://github.com/AbigailMcGovern/naparistreamdeck/blob/main/roadmap_media/image_layer_draft.png)


### Labels Layer

![Draft showing current ideas for buttons, slider, and screen for labels layer.](https://github.com/AbigailMcGovern/naparistreamdeck/blob/main/roadmap_media/labels_layer_draft.png)