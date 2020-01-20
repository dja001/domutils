#cb_noshow is just a redefinition of mathplolib ColorbarBase where 
#the plotting of colors in a colorbar is turned off


import matplotlib as mpl
import matplotlib.colorbar as mpc
import numpy as np
import matplotlib.patches as mpatches

class cb_noshow(mpc.ColorbarBase):
    def draw_all(self):
        '''
        Calculate any free parameters based on the current cmap and norm,
        and do all the drawing.
        '''

        # sets self._boundaries and self._values in real data units.
        # takes into account extend values:
        self._process_values()
        # sets self.vmin and vmax in data units, but just for
        # the part of the colorbar that is not part of the extend
        # patch:
        self._find_range()
        # returns the X and Y mesh, *but* this was/is in normalized
        # units:
        X, Y = self._mesh()
        C = self._values[:, np.newaxis]
        self._config_axes(X, Y)
        #
        #Turning off palette from colorbar
        #
        #if self.filled:
        #    self._add_solids(X, Y, C)

    def _config_axes(self, X, Y):
        '''
        Make an axes patch and outline.
        '''
        ax = self.ax
        ax.set_frame_on(False)
        ax.set_navigate(False)
        xy = self._outline(X, Y)
        ax.update_datalim(xy)
        ax.set_xlim(*ax.dataLim.intervalx)
        ax.set_ylim(*ax.dataLim.intervaly)
        if self.outline is not None:
            self.outline.remove()
        self.outline = mpatches.Polygon(
            xy, edgecolor=mpl.rcParams['axes.edgecolor'],
            facecolor='none',
            linewidth=mpl.rcParams['axes.linewidth'],
            closed=True,
            zorder=2)
        ax.add_artist(self.outline)
        self.outline.set_clip_box(None)
        self.outline.set_clip_path(None)
        c = mpl.rcParams['axes.facecolor']
        if self.patch is not None:
            self.patch.remove()
        #
        #Turning off palette from colorbar
        #
        #self.patch = mpatches.Polygon(xy, edgecolor=c,
        #                              facecolor=c,
        #                              linewidth=0.01,
        #                              zorder=-1)
        #ax.add_artist(self.patch)

        self.update_ticks()

    


