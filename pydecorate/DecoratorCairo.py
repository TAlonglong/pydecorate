# pydecorate - python module for labelling
# and adding colour scales to images
#
#Copyright (C) 2011  Hrobjartur Thorsteinsson
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import division
from pydecorate.DecoratorBase import DecoratorBase

import numpy as np

try:
    from PIL import Image, ImageFont
except ImportError:
    print "ImportError: Missing PIL image objects"

try:
    import cairo
except ImportError:
    print "ImportError: Missing module: Cairo"

try:
    from PIL import ImageDraw
except ImportError:
    print "ImportError: Missing module: ImageDraw"


import numpy
import os

class DecoratorCairo(DecoratorBase):
    """
    Allows to draw text and overlays on images.

    Extends DecoratorBase. Uses Cairo as drawing library instead of Aggdraw.


    """

    def __init__(self, image):
        self.surface = cairo.ImageSurface.create_from_png(image)
        self.context = cairo.Context(self.surface)
        super(DecoratorCairo, self).__init__(image)
        print("surface size: %s x %s" % (self.surface.get_width(), self.surface.get_height()))

        # cairo uses different scales than pil and aggdraw
        self.style['bg'] = (255,255,255)
        self.style['bg_opacity'] = 0.5
        self.style['line'] = (0, 0, 0)
        self.style['line_opacity'] = 1


    def write_vertically(self):
        super(DecoratorCairo, self).write_vertically()

    def write_horizontally(self):
        super(DecoratorCairo, self).write_horizontally()

    def align_bottom(self):
        super(DecoratorCairo, self).align_bottom()

    def align_top(self):
        super(DecoratorCairo, self).align_top()

    def align_right(self):
        super(DecoratorCairo, self).align_right()

    def align_left(self):
        super(DecoratorCairo, self).align_left()

    def add_scale(self,colormap,**kwargs):
        self._add_scale(colormap,**kwargs)

    def add_text(self,txt,**kwargs):
        self._add_text(txt, **kwargs)

    def add_logo(self,logo_path,**kwargs):
        self._add_logo(logo_path,**kwargs)

    def _load_default_font(self):
        # Koe: loading fonts in Cairo is done through the context
        # isn't necessary to instantiate a font object and return it
        cairo_select_font_face (cr, "monospace", CAIRO_FONT_SLANT_NORMAL, CAIRO_FONT_WEIGHT_NORMAL);

    def _get_canvas(self,image):
        # Koe: the AGG image object is "translated" in self.surface.
        # I decided to create it once on __init__ and keep that single instance
        # for the entire run, making this function unnecessary.
        # This can be reverted if needed.
        raise NotImplementedError("not implemented yet")

    def save_png(self, path):
        ## FIXME Koe: testing path and name, NEEDS to be changed
        self.surface.write_to_png(path)
        self.surface.finish()

    def _finalize(self, draw):
        """Do any need finalization of the drawing
        """
        #raise NotImplementedError("not implemented yet")
        pass
     
    def _draw_polygon(self, draw,xys,outline=None,fill=[255,255,255], fill_opacity=1,outline_width=1, outline_opacity=1):
        raise NotImplementedError("not implemented yet")
        # import aggdraw
        # if outline is None:
            # pen=None
        # else:
            # pen=aggdraw.Pen(outline,width=outline_width,opacity=outline_opacity)
        # if fill is None:
            # brush=None
        # else:
            # brush=aggdraw.Brush(fill,opacity=fill_opacity)
        # xys_straight=[ item for t in xys for item in t ]
        # draw.polygon(xys_straight,pen,brush)

    def set_style(self, **kwargs):
        self.style.update(kwargs)
        self.style['cursor'] = list(self.style['cursor'])

    def home(self):
        self.style['cursor'][0] = int(self.style['alignment'][0] * self.surface.get_width())
        self.style['cursor'][1] = int(self.style['alignment'][1] * self.surface.get_height())

    def rewind(self):
        super(DecoratorCairo, self).rewind()

    def new_line(self):
        super(DecoratorCairo, self).new_line()

    def _step_cursor(self):
        super(DecoratorCairo, self)._step_cursor()

    def _load_default_font(self):
        #temporary toy-method
        self.context.select_font_face("Serif", 1, 1)

    def _draw_polygon(self,draw,xys,**kwargs):
        draw.polygon(xys,fill=kwargs['fill'],outline=kwargs['outline'])

    def _add_text(self, txt, **kwargs):

        # synchronize kwargs into style
        self.set_style(**kwargs)

        # check for font object
        if self.style['font'] is None:
            self.style['font'] = self._load_default_font()

        # image size
        x_size = self.surface.get_height()
        y_size = self.surface.get_width()

        # split text into newlines '\n'
        txt_nl=txt.split('\n')

        # current xy and margins
        x = self.style['cursor'][0]
        y = self.style['cursor'][1]
        mx = self.style['margins'][0]
        my = self.style['margins'][1]
        prev_width  = self.style['width']
        prev_height = self.style['height']

        # calculate text space
        extents = self.context.text_extents(txt_nl[0])
        tw = extents[2]
        th = extents[3]
        bearing_x = extents[0]
        bearing_y = extents[1]

        for t in txt_nl:
            w = self.context.text_extents(t)[2]
            if w > tw: tw = w
        hh=len(txt_nl)*th


        # set height/width for subsequent draw operations
        if prev_height < int(hh+2*my):
            self.style['height'] = int(hh+2*my)
        self.style['width'] = int(tw+2*mx)

        # draw base
        px = (self.style['propagation'][0] + self.style['newline_propagation'][0])
        py = (self.style['propagation'][1] + self.style['newline_propagation'][1])
        x1 = px*self.style['width']
        y1 = py*self.style['height']

        pos_x = x + mx
        pos_y = y + my

        self._draw_rectangle(None, [x, y, x1, y1], **self.style)

        # draw
        for i in range(len(txt_nl)):
            pos_x = x + mx
            pos_y = y + i*th+my
            if py < 0:
                pos_y += py*self.style['height']
            if px < 0:
                pos_x += px*self.style['width']
            self._draw_text_line(None, (pos_x, pos_y), txt_nl[i], self.style['font'], fill = self.style['fill'])

        # update cursor
        self._step_cursor()

    def _draw_text(self, draw, xy, txt, font, fill='black', align='cc', dry_run=False, **kwargs):
        """
        Elementary text draw routine,
        with alignment. Returns text size.
        """
        
        # check for font object
        if font is None:
            font = self._load_default_font()
        # calculate text space
        text_extents = self.context.text_extents(txt)
        tw = text_extents[2]
        th = text_extents[3]
        # align text position
        x, y = xy
        if align[0] == 'c':
            x -= tw/2.0
        elif align[0] == 'r':
            x -= tw
        if align[1] == 'c':
            y -= th/2.0
        elif align[1] == 'r':
            y -= th
        # draw the text
        if not dry_run:
            self._draw_text_line(draw, (x,y), txt, font, fill=fill)
        return tw,th

    def _draw_text_line(self, draw, xy, text, font, fill='black'):
        self.context.set_source_rgb(self.style['line'][0], self.style['line'][1], self.style['line'][2])
        self.context.move_to(xy[0], xy[1])
        self.context.show_text(text)

    def _draw_line(self,draw,xys,**kwargs):
        self.context.set_line_width(self.style['line_width'])
        self.context.set_source_rgb(self.style['line'][0], self.style['line'][1], self.style['line'][2])
        self.context.move_to(xys[0][0], xys[0][1])
        self.context.line_to(xys[1][0], xys[1][1])
        self.context.stroke()

    def _draw_rectangle(self,draw,xys,**kwargs):
        # adjust extent of rectangle to draw up to but not including xys[2/3]
        self.context.set_source_rgba(self.style['bg'][0], self.style['bg'][0], self.style['bg'][0], self.style['bg_opacity'])
        if kwargs['bg'] or kwargs['outline']:
            self.context.rectangle(xys[0], xys[1], xys[2], xys[3])
        self.context.fill()


    def _insert_RGBA_image(self,img,box):
        # make sure box is formed tl to br corners:
    
        ## Koe: does not use a "box" anymore, the image has to be already scaled
        
        self.context.save()
        self.context.set_source_surface(img, box[0], box[1])
        self.context.paint()
        self.context.restore()

    def _add_logo(self, logo_path, **kwargs):
        # synchronize kwargs into style
        self.set_style(**kwargs)
        # current xy and margins
        x = self.style['cursor'][0]
        y = self.style['cursor'][1]
        marg_x = self.style['margins'][0]
        marg_y = self.style['margins'][1]

        try:
            logo_surface = cairo.ImageSurface.create_from_png(logo_path)
        except:
            print("logo file not available or not in png format")

        # default size is _line_size set by previous draw operation
        # else do not resize
        logo_width = logo_surface.get_width()
        logo_height = logo_surface.get_height()
        aspect = float(logo_height)/logo_width

        # default logo sizes ...
        # use previously set line_size
        if self.style['propagation'][0] != 0:
            logo_height = self.style['height']
            nyi = int(round(logo_height-2*marg_y))
            nxi = int(round(nyi/aspect))
            logo_width = (nxi + 2*marg_x)
        elif self.style['propagation'][1] != 0:
            logo_width = self.style['width']
            nxi = int(round(logo_width-2*marg_x))
            nyi = int(round(nxi*aspect))
            logo_height = (nyi + 2*marg_y)

        # draw base
        px = (self.style['propagation'][0] + self.style['newline_propagation'][0])
        py = (self.style['propagation'][1] + self.style['newline_propagation'][1])
        rectangle_box = [x, y, px*logo_width, py*logo_height]

        self._draw_rectangle(None, rectangle_box, **self.style)

        scale_x = nxi/logo_surface.get_width()
        scale_y = nyi/logo_surface.get_height()
        
        logo_x = x + (rectangle_box[2])/2 - nxi/2
        logo_y = y + (rectangle_box[3])/2 - nyi/2
        
        # paste logo
        self._scale_and_draw_image(logo_surface, (logo_x, logo_y), (scale_x, scale_y))

        # update cursor
        self.style['width'] = int(logo_width)
        self.style['height'] = int(logo_height)
        self._step_cursor()
        
    def _scale_and_draw_image(self, surface, xy, scale):
        
        # make sure xy is formed tl to br corners:
    
        self.context.save()
        self.context.scale(scale[0],scale[1])
        self.context.set_source_surface(surface, xy[0]/scale[0], xy[1]/scale[1])
        self.context.paint()
        self.context.restore()
        
    def _form_xy_box(self,box):
        newbox = box + []
        if box[0] > box[2]:
            newbox[0] = box[2]
            newbox[2] = box[0]
        if box[1] > box[3]:
            newbox[1] = box[3]
            newbox[3] = box[1]
        return newbox

    def _add_scale(self, colormap, **kwargs):
        # synchronize kwargs into style
        self.set_style(**kwargs)

        # sizes, current xy and margins
        x=self.style['cursor'][0]
        y=self.style['cursor'][1]
        mx=self.style['margins'][0]
        my=self.style['margins'][1]
        x_size = self.surface.get_width()
        y_size = self.surface.get_height()


        # horizontal/vertical?
        is_vertical = False
        if self.style['propagation'][1] != 0:
            is_vertical = True

        # left/right?
        is_right = False
        if self.style['alignment'][0] == 1.0:
            is_right = True

        # top/bottom?
        is_bottom = False
        if self.style['alignment'][1] == 1.0:
            is_bottom = True

        # adjust new size based on extend (fill space) style,
        if self.style['extend']:
            if self.style['propagation'][0] == 1:
                self.style['width'] = (x_size - x)
            elif self.style['propagation'][0] == -1:
                self.style['width'] = x
            if self.style['propagation'][1] == 1:
                self.style['height'] = (y_size - y)
            elif self.style['propagation'][1] == -1:
                self.style['height'] = y

        # set scale spacer for units and other
        x_spacer = 0
        y_spacer = 0
        if self.style['unit']:
            if is_vertical:
                y_spacer = 40
            else:
                x_spacer = 40

        # draw base
        px = (self.style['propagation'][0] + self.style['newline_propagation'][0])
        py = (self.style['propagation'][1] + self.style['newline_propagation'][1])
        x1 = x + px*self.style['width']
        y1 = y + py*self.style['height']
        self._draw_rectangle(None,[x,y,x1,y1],**self.style)

        # scale dimensions
        scale_width = self.style['width'] - 2*mx - x_spacer
        scale_height = self.style['height'] - 2*my - y_spacer

        # generate color scale image obj inset by margin size mx my,
        from trollimage.image import Image as TImage

        #### THIS PART TO BE INGESTED INTO A COLORMAP FUNCTION ####
        minval,maxval = colormap.values[0],colormap.values[-1]

        if is_vertical:
            linedata = np.ones((scale_width,1)) * np.arange(minval,maxval,(maxval-minval)/scale_height)
            linedata = linedata.transpose()
        else:
            linedata = np.ones((scale_height,1)) * np.arange(minval,maxval,(maxval-minval)/scale_width)

        timg = TImage(linedata,mode="L")
        timg.colorize(colormap)
        scale = timg.pil_image()
        ###########################################################

        # computing the top left corner of the scale background
        image_corner_x = min(x,x1)+mx 
        image_corner_y = min(y,y1)+my 
        
        cairo_image = _pil_to_cairo(scale)
        
        self.context.save()
        self.context.set_source_surface(cairo_image, image_corner_x, image_corner_y)
        self.context.paint()
        self.context.restore()
        
        # draw tick marks
        val_steps =  _round_arange2( minval, maxval , self.style['tick_marks'] )
        minor_steps =  _round_arange( minval, maxval , self.style['minor_tick_marks'] )
        ffra, fpow = _optimize_scale_numbers( minval, maxval, self.style['tick_marks'] )
        form = "%"+"."+str(ffra)+"f"
        last_x = x+px*mx
        last_y = y+py*my
        
        text_extents = self.context.text_extents(form%(val_steps[0]))
        ref_width = text_extents[2]
        ref_height = text_extents[3]

        if is_vertical:
            # major
            offset_start = val_steps[0]  - minval
            offset_end   = val_steps[-1] - maxval
            y_steps = py*(val_steps - minval - offset_start - offset_end)*scale_height/(maxval-minval)+y+py*my
            y_steps = y_steps[::-1]
            for i, ys in enumerate(y_steps):
                self._draw_line(None,[(x+px*mx,ys),(x+px*(mx+scale_width/3.0),ys)],**self.style)
                if abs(ys-last_y)>ref_height:
                    self._draw_text(None,(x+px*(mx + scale_width),ys + ref_height), (form%(val_steps[i])).strip(), **self.style)
                    last_y = ys
            # minor
            y_steps = py*(minor_steps - minval)*scale_height/(maxval-minval)+y+py*my
            y_steps = y_steps[::-1]
            for i, ys in enumerate(y_steps):
                self._draw_line(None,[(x+px*mx,ys),(x+px*(mx+scale_width/6.0),ys)],**self.style)
        else:
            # major
            x_steps = px*(val_steps - minval)*scale_width/(maxval-minval)+x+px*mx
            for i, xs in enumerate(x_steps):
                x_start = (xs,y+py*my)
                x_end = (xs,y+py*(my+scale_height/3.0))
                self._draw_line(None,[x_start,x_end],**self.style)
                if abs(xs-last_x)>ref_width:
                    self._draw_text(None,(xs, y+py*(my+2*scale_height/2)), (form%(val_steps[i])).strip(), **self.style)
                    last_x = xs
            # minor
            x_steps = px*(minor_steps - minval)*scale_width/(maxval-minval)+x+px*mx
            for i, xs in enumerate(x_steps):
                x_start = (xs,y+py*my)
                x_end = (xs,y+py*(my+scale_height/6.0))
                self._draw_line(None,[x_start, x_end],**self.style)
      

        # draw unit and/or power if set
        if self.style['unit']:
            # calculate position
            if is_vertical:
                if is_right:
                    x = x - mx - scale_width/2.0
                else:
                    x = x + mx + scale_width/2.0
                y = y + my + scale_height + y_spacer/2.0
            else:
                x = x + mx + scale_width + x_spacer/2.0
                if is_bottom:
                    y = y - my - scale_height/2.0
                else:
                    y = y + my + scale_height/2.0
            # draw marking
            self._draw_text(None,(x,y),self.style['unit'],**self.style)

        # finalize
        #self._finalize(draw)

#########################################


# float list generator
def _frange(x,y,jump):
    while x < y:
        yield x
        x += jump
def frange(x,y,jump):
    return [p for p in _frange(x,y,jump) ]

def  _round_arange(val_min, val_max , dval):
    """
    Returns an array of values in the range from valmin to valmax
    but with stepping, dval. This is similar to numpy.arange except
    the values must be rounded to the nearest multiple of dval.
    """
    vals = np.arange(val_min, val_max, dval)
    round_vals = vals - vals%dval
    if round_vals[0] < val_min:
        round_vals = round_vals[1:]
    return round_vals

def  _round_arange2(val_min, val_max , dval):
    """
    Returns an array of values in the range from valmin to valmax
    but with stepping, dval. This is similar to numpy.linspace except
    the values must be rounded to the nearest multiple of dval.
    The difference to _round_arange is that the return values include
    also the bounary value val_max.
    """
    val_min_round = val_min + (dval-val_min%dval)%dval
    val_max_round = val_max - val_max%dval
    n_points = int((val_max_round-val_min_round)/dval)+1
    vals = np.linspace( val_min_round, val_max_round, num=n_points)

    return vals


def _optimize_scale_numbers( minval, maxval, dval ):
    """
    find a suitable number format, A and B in "%A.Bf" and power if numbers are large
    for display of scale numbers.
    """
    ffra = 1
    # no fractions, so turn off remainder
    if dval%1.0 == 0.0:
        ffra=0

    return ffra,0

def _pil_to_cairo(pil_img):
    """
    Convert PIL image to cairo surface
    
    """

    img_rgba = pil_img.convert('RGBA')
    data = np.array(img_rgba.tobytes('raw', 'BGRA'))
    width, height = img_rgba.size
    surface = cairo.ImageSurface.create_for_data(data, cairo.FORMAT_ARGB32,
                                           width, height)
    return surface
