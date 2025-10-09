import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from canopy.core.field import Field
from canopy.core.raster import Raster
from canopy.core.redspec import RedSpec
from typing import Optional
from canopy.util.fieldops import make_lines
import matplotlib.gridspec as gridspec
import cartopy.crs as ccrs
import cartopy.feature as cf
from mpl_toolkits.axes_grid1 import make_axes_locatable

# Color dictionaries
CM_EUROPEAN_PFTS = {
    'Abi_alb':'firebrick',
    'BES':'mediumturquoise',
    'Bet_pen':'olive',
    'Bet_pub':'palevioletred',
    'Car_bet':'lightcoral',
    'Cor_ave':'fuchsia',
    'Fag_syl':'cornflowerblue',
    'Fra_exc':'navy',
    'Jun_oxy':'chocolate',
    'MRS':'crimson',
    'Pic_abi':'deepskyblue',
    'Pin_syl':'deeppink',
    'Pin_hal':'palegreen',
    'Pop_tre':'gold',
    'Que_coc':'grey',
    'Que_ile':'steelblue',
    'Que_pub':'darkorange',
    'Que_rob':'teal',
    'Til_cor':'indigo',
    'Ulm_gla':'darkgreen',
    'C3_gr':'mediumpurple',
}

color_schemes = {
        "european_pfts": CM_EUROPEAN_PFTS,
}

# Heat map
# ---- ---
def heatmap(raster: Raster, cmap: Optional = 'Greens', fname: Optional = None):

    gs = gridspec.GridSpec(2, 1, height_ratios=[24,1])
    fig = plt.figure(figsize=(8,5.7))
    ax_map = plt.subplot(gs[0], projection=ccrs.PlateCarree())
    ax_map.add_feature(cf.COASTLINE, linewidth=0.4)
    pc = plt.pcolormesh(raster.xx, raster.yy, raster.vmap, cmap=cmap)
    ax_bar = plt.subplot(gs[1])
    cbar = plt.colorbar(pc, orientation='horizontal', cax=ax_bar)
    if fname is None:
        plt.show()
    else:
        plt.savefig(fname, dpi=300)


# Categorical map (e.g. Dominant PFT map)
def catmap(raster: Raster, cs: Optional = None, fname: Optional = None):

    nbins = len(raster.labels)
    if cs is None:
        cmap = plt.get_cmap('turbo', nbins)
    else:
        categories = list(raster.labels.values())
        color_list = [ color_schemes[cs][cat] for cat in categories ]
        cmap = mpl.colors.ListedColormap(color_list[:nbins])
    fig, ax_map = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()})
    ax_map.add_feature(cf.COASTLINE, linewidth=0.4)
    pc = plt.pcolormesh(raster.xx, raster.yy, raster.vmap, cmap=cmap, vmin=-0.5, vmax=nbins-0.5)
    divider = make_axes_locatable(ax_map)
    ax_cbar = divider.new_horizontal(size="5%", pad=0.1, axes_class=plt.Axes)
    fig.add_axes(ax_cbar)
    cbar = plt.colorbar(pc, orientation='vertical', cax=ax_cbar)
    cbar_ticks = np.arange(nbins)
    cbar.set_ticks(cbar_ticks, labels=[f"${v}$".replace('_', '\,\,') for (_, v) in raster.labels.items()])
    plt.tight_layout()

    if fname is None:
        plt.show()
    else:
        plt.savefig(fname, dpi=300)


def plot_time_series_spatial_average(field: Field):

    redspec = RedSpec(redop='av')
    df_lines = make_lines(field, 'time', redspec=redspec)
    df_lines.plot.line()
    plt.show()

