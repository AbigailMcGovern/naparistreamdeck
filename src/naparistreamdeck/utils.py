from PIL import Image, ImageDraw, ImageFont
import numpy as np

# ---------
# Resources
# ---------

resource_dict = {
    'colourpicker_on' : 'colourpicker_icon_on.png', # 66 x 66 px
    'colourpicker_off' : 'colourpicker_icon.png', # 66 x 66 px
    'eraser_on' : 'eraser_icon_on.png', # 66 x 66 px
    'eraser_off' : 'eraser_icon.png', # 66 x 66 px
    'fillbucket_on': 'fillbucket_icon_on.png', # 66 x 66 px
    'fillbucket_off': 'fillbucket_icon.png', # 66 x 66 px
    'paintbrush_on' : 'paintbrush_icon_on.png', # 66 x 66 px
    'paintbrush_off' : 'paintbrush_icon.png', # 66 x 66 px
    'pan_on' : 'pan_icon_on.png', # 66 x 66 px
    'pan_off' : 'pan_icon.png', # 66 x 66 px
    'shuffle_colours' : 'shuffle_colours_icon.png', # 66 x 66 px
    'opacity' : 'opacity_icon.png', 
    'contor' : 'contor_icon.png', 
    'blending' : 'blending_icon.png', 
    'contrast_upper' : 'contrast_upper_icon.png', 
    'contrast_lower' : 'contrast_lower_icon.png', 
    'label' : 'label_icon.png', 
    'brush_size' : 'brush_size_icon.png', 
    'edit_dims_2D' : 'edit_dims_2D_icon.png', 
    'edit_dims_3D' : 'edit_dims_3D_icon.png', 

}


def draw_number(n):
    width = 50
    height = 50
    message = str(n)
    img = Image.new('RGB', (width, height), color='white')
    imgDraw = ImageDraw.Draw(img)
    font = ImageFont.truetype("Arial Unicode.ttf", size=30)
    y = 3
    n_digits = 1 if n < 10 else 2 # we won't need to worry about more than this at them moment
    x = (50 - 19 * n_digits) / 2
    imgDraw.text((x, y), message, font=font, fill=(0, 0, 0))
    img = np.array(img)
    return img


def read_resource(name):
    file = resource_dict[name]
    img = Image.open(file)
    img = np.array(img)
    return img



# unneccessary
def check_for_multidial(dial):
    if dial == 'edit_dimensions':
        multidial = {
            '' : 'edit_dims_2D', 
            '' : 'edit_dims_3D'
        }
    elif dial == 'contrast':
        multidial = {
            '' : 'contrast_upper', 
            '' : 'contrast_lower'
        }

    else:
        multidial = False

