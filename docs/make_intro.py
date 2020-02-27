#script to make the different frames of the animated gif intro

# a function for formatting axes
def format_axes(ax):
    for axis in ['top','bottom','left','right']:
        ax.spines[axis].set_linewidth(.3)
    limits = (-1.,1.)
    ax.set_xlim(limits)
    ax.set_ylim(limits)
    ticks  = [-1.,0.,1.]
    ax.set_xticks(ticks)
    ax.set_yticks(ticks)

#a function for bw color palette
def b_w(pos, hide=None, pal_format='{:2.0f}', pal_units=None):
    import domutils.legs as legs

    #color map
    if hide == 0:
        c_map = legs.PalObj(range_arr = [0.,1.], color_arr='b_w')
        c_map.plot_palette(pal_pos=pos, pal_format=pal_format, pal_units=pal_units)

#a function for 5 semi-continuous color palette
def semi_continuous(pos, hide=None, pal_format='{:2.1f}', pal_units=None):
    import domutils.legs as legs

    #color map
    if hide == 0:
        c_map = legs.PalObj(range_arr = [0.,1.], n_col=5)
        c_map.plot_palette(pal_pos=pos, pal_format=pal_format, pal_units=pal_units)

#a function for 5 semi-continuous color palette
def divergent(pos, hide=None, pal_format='{:2.1f}', pal_units=None):
    import domutils.legs as legs
    green_purple =[ [114,  30, 179],  #dark purple
                    [172,  61, 255],
                    [210, 159, 255],
                    [255, 215, 255],  #pale purple
                    [255, 255, 255],  #white
                    [218, 255, 207],  #pale green
                    [162, 222, 134],
                    [111, 184,   0],
                    [  0, 129,   0] ] #dark green
    #color map
    if hide == 0:
        c_map = legs.PalObj(range_arr=[-4.5, 4.5],
                            color_arr=green_purple,
                            solid='supplied',
                            over_under='extend')
        c_map.plot_palette(pal_pos=pos, pal_format=pal_format, pal_units=pal_units)

def unequal(pos, hide=None, pal_format='{:2.1f}', pal_units=None):
    import domutils.legs as legs

    # color map
    if hide == 0:
        c_map = legs.PalObj(range_arr=[.1, 3., 6., 12., 25., 50., 100.],
                            n_col=6,
                            over_high='extend',
                            under_low='white')
        c_map.plot_palette(pal_pos=pos, pal_format=pal_format, pal_units=pal_units,
                           equal_legs=True)


"""
Legs, a library for easy custom color mappings

Integrated

domutils.legs

    Define data intervals
        define color mapping in this range
        Chain multiple intervals for more complex color mappings
        Decide what happens at end points
        Define exceptions ; any number of exceptions

    Homogeneous style
        It is easy to map NODATA to the same colors in all figures of a given manuscript
        control color changes at meaningful values
            0 included vs not included

    Protection against errors
        User is forced to define units
        The same function is used for the mapping of data and the construction of colorbars
        Direct association between data values and RGB
        Builtin check that all values in the interval -infty, infty are mapped to a color
        Get noticed if values are found outside of exact palettes
"""
import os
import matplotlib as mpl
import matplotlib.pyplot as plt
import domutils._py_tools as py_tools

# point density for figure
mpl.rcParams.update({'font.size': 17})
# Use this to make text editable in svg files
mpl.rcParams['text.usetex'] = False
mpl.rcParams['svg.fonttype'] = 'none'
# Hi def figure
mpl.rcParams['figure.dpi'] = 400



# figure properties
mpl.rcParams.update({'font.size': 15})
fig_w = 16. / 2.54
fig_h =  9. / 2.54
rec_w = (1. / 2.54) / fig_w
rec_h = (7. / 2.54) / fig_h
pal_w = (.4 / 2.54) / fig_w
pal_h = (5. / 2.54) / fig_h
sp_w  = (2. / 2.54) / fig_w
sp_h  = (.5 / 2.54) / fig_h
y0    = (.5 / 2.54) / fig_h
pic_dir = 'animated_gif/'
if not os.path.isdir(pic_dir):
    os.mkdir(pic_dir)

#Frame
frame_tit = 'legs_01_intro.svg'
fig = plt.figure(figsize=(fig_w, fig_h))

fig_ax = fig.add_axes([0., 0., 1., 1.])
fig_ax.axis('off')
#for axis in ['top','bottom','left','right']:
#    fig_ax.spines[axis].set_linewidth(0)

fig_ax.annotate('domutils.legs',
                size=18, xy = (.1, .9 ), xycoords = 'axes fraction')
fig_ax.annotate('a library for easy custom color mappings',
                size=18, xy = (.15, .8 ), xycoords = 'axes fraction')

#b_w palette
x0 = (.5 / 2.54) / fig_w
pos = (x0, y0, pal_w, pal_h)
b_w(pos, hide=0, pal_units='[m/s]')

#5 cols semi-continuous palette
x0 += (3. / 2.54) / fig_w
pos = (x0, y0, pal_w, pal_h)
semi_continuous(pos, hide=0, pal_units='[mm/h]')

#divergent palette
x0 += (3. / 2.54) / fig_w
pos = (x0, y0, pal_w, pal_h)
divergent(pos, hide=0, pal_units='[kg]')

#unequal ranges
x0 += (3. / 2.54) / fig_w
pos = (x0, y0, pal_w, pal_h)
unequal(pos, hide=0, pal_units='[mm]')


pic_name = pic_dir + frame_tit
plt.savefig(pic_name)
py_tools.lmroman(pic_name)
#py_tools.convert(pic_name,  )
