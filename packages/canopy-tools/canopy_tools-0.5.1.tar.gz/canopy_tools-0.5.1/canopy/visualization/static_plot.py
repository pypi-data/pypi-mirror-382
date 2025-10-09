import numpy as np
import pandas as pd
from scipy.stats import linregress
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
from typing import Optional, List
import canopy as cp
from canopy.visualization.plot_functions import get_color_palette, make_dark_mode, handle_figure_output

def make_static_plot(field_a: cp.Field, field_b: cp.Field,
                     output_file: Optional[str] = None, layers: Optional[List[str] | str] = None,
                     field_a_label: Optional[str] = None, field_b_label: Optional[str] = None,
                     unit_a: Optional[str] = None, unit_b: Optional[str] = None, 
                     title: Optional[str] = None, palette: Optional[str] = None, 
                     custom_palette: Optional[str] = None, move_legend: Optional[bool] = False, 
                     dark_mode: Optional[bool] = False, transparent: Optional[bool] = False, 
                     x_fig: Optional[float] = 10, y_fig: Optional[float] = 10, 
                     return_fig: Optional[bool] = False, **kwargs) -> Optional[plt.Figure]:
    """
    This function generates a scatter plot with regression lines and r-scores from two input fields 
    (which can be reduced spatially, temporally or both).

    Parameters
    ----------
    field_a, field_b : cp.Field
        Input data Field to display.
    output_file : str, optional
        File path for saving the plot.
    layers : List[str] or str, optional
        Layers to plot from the input data.
    field_a_label, field_b_label : str, optional
        Labels for the data series, if not provided canopy will try to retrieve the name of the variable in the metadata.
    unit_a, unit_b : str, optional
        Units for the data series, if not provided canopy will try to retrieve the unit of the variable in the metadata.
    title : str, optional
        Title of the plot.
    palette : str, optional
        Seaborn color palette to use for the line colors (https://seaborn.pydata.org/tutorial/color_palettes.html, 
        recommended palette are in https://colorbrewer2.org).
    custom_palette : str, optional
        Path of custom color palette .txt file to use. Names should match label names.
    move_legend : bool, optional
        Location of the legend ('in' or 'out'). Default is False.
    dark_mode : bool, optional
        Whether to apply dark mode styling to the plot.
    transparent : bool, optional
        If True, makes the background of the figure transparent.
    x_fig : float, optional
        Width of the figure in inches. Default is 10.
    y_fig : float, optional
        Height of the figure in inches. Default is 10.
    return_fig : bool, optional
        If True, returns the figure object that can be usuable by multiple_figs().
        Default is False.
    **kwargs
        Additional keyword arguments are passed directly to `seaborn.regplot`. This allows customization of
        plot features such as `lowess`, `robust`, `logx`, etc.
    """
    # Force layers to be a list
    if isinstance(layers, str):
        layers = [layers]

    # Retrieve metadata
    field_a_label = field_a_label or field_a.metadata['name']
    field_b_label = field_b_label or field_b.metadata['name']
    unit_a = field_a.metadata['units'] if unit_a is None else unit_a
    unit_b = field_b.metadata['units'] if unit_b is None else unit_b
    layers = layers or field_a.layers

    df_a = cp.make_lines(field_a)
    df_b = cp.make_lines(field_b)

    # Set up the figure and axes
    fig, ax = plt.subplots(figsize=(x_fig, y_fig))

     # Get the palette
    colors, colors_dict = get_color_palette(len(layers), palette=palette, custom_palette=custom_palette)

    r_squared = []
    for i, layer in enumerate(tqdm(layers, desc="Plotting layers")):
        x = df_a[layer].values.flatten()
        y = df_b[layer].values.flatten()
        # Perform linear regression and calculate R-squared
        slope, intercept, r, p, stderr = linregress(x, y)
        r_squared.append(r**2)
        sns.regplot(x=x, y=y, color=colors[i], label=layer,
                    scatter_kws={'s': 6, 'alpha': 0.1}, line_kws={'label': "Linear Reg"},
                    ax=ax, **kwargs)
    
    # Set axis limits
    min_val = min(df_a[layers].min().min(), df_b[layers].min().min())
    max_val = max(df_a[layers].max().max(), df_b[layers].max().max())
    ax.set_xlim([min_val, max_val])
    ax.set_ylim([min_val, max_val])

    # Make legend
    ax.legend(loc = 'best')
    leg = ax.get_legend()
    L_labels = leg.get_texts()
    for i in range(len(layers)):
        L_labels[(2*i)+1].set_text(r'$R^2:{0:.2f}$'.format(r_squared[i]))
    if move_legend is True:
            sns.move_legend(ax, "center left", bbox_to_anchor=(1, 0.85))

    # Set axis labels with units
    xlabel = f"{field_a_label} (in {unit_a})" if unit_a != "[no units]" else field_a_label
    ylabel = f"{field_b_label} (in {unit_b})" if unit_b != "[no units]" else field_b_label
    ax.set_xlabel(xlabel, fontsize=16)
    ax.set_ylabel(ylabel, fontsize=16)   

    # Set plot title
    ax.set_title(title, fontsize=18) 

    # Apply dark mode if requested
    if dark_mode:
        fig, ax = make_dark_mode(fig, ax)

    return handle_figure_output(fig, output_file=output_file, return_fig=return_fig, transparent=transparent)
