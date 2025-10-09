import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from typing import Optional, List
from canopy.visualization.plot_functions import get_color_palette, make_dark_mode, handle_figure_output
import canopy as cp

def make_comparison_plot(fields: cp.Field | List[cp.Field], output_file: Optional[str] = None,
                         plot_type: Optional[str] = "box", layers: Optional[List[str] | str] = None,
                         gridop: Optional[str] = None, 
                         yaxis_label: Optional[str] = None, field_labels: Optional[List[str]] = None,
                         unit: Optional[List[str]] = None, title: Optional[str] = None, 
                         palette: Optional[str] = None, custom_palette: Optional[List[str]] = None, 
                         horizontal: Optional[bool] = False, vertical_xlabels: Optional[bool] = False, 
                         dark_mode: bool = False, transparent: bool = False, 
                         x_fig: float = 10, y_fig: float = 10, 
                         return_fig: Optional[bool] = False, **kwargs) -> Optional[plt.Figure]:
    """
    Create a comparative plot from a list of input data Fields from, for example, different runs. The functions can generate
    boxplot, strip or swarm plot, violin plot, boxen plot, point plot, bar plot or count plot based on the `plot_type` parameter.

    Parameters
    ----------
    fields : cp.Field or List[cp.Field]
        Input data Field to display.
    output_file : str, optional
        File path for saving the plot.
    plot_type: str, optional
        Type of plot. Either “strip”, “swarm”, “box”, “violin”, “boxen”, “point”, “bar”, or “count”
    layers : List[str] or str, optional
        List of layer names to display.
    gridop : str, optional
        If provided, the grid reduction operation. Either None, 'sum' or 'av'. Default is None.
    yaxis_label : str, optional
        Y-axis label, if not provided canopy will try to retrieve the name of the variable in the metadata.
    field_labels : List[str], optional
        Names of each series to display in the legend.
    unit : List[str], optional
        Unit of the y-axis variable, if not provided canopy will try to retrieve the unit of the variable in the metadata.
    title : str, optional
        Title of the plot.
    palette : str, optional
        Seaborn color palette to use for the line colors (https://seaborn.pydata.org/tutorial/color_palettes.html, 
        recommended palette are in https://colorbrewer2.org).
    custom_palette : List[str], optional
        Path of custom color palette .txt file to use. Names should match label names.
    horizontal : bool, optional
        If True, renders the plot with horizontal orientation (flips the axes).
    vertical_xlabels : bool, optional
        If True, rotates the x-axis tick labels vertically (i.e., 90 degrees).
    dark_mode : bool, optional
        If True, applies dark mode styling to the figure. Default is False.
    transparent : bool, optional
        If True, sets the figure background to be transparent when saved. Default is False.
    x_fig : float, optional
        Width of the figure in inches. Default is 10.
    y_fig : float, optional
        Height of the figure in inches. Default is 10.
    return_fig : bool, optional
        If True, returns the figure object that can be usuable by multiple_figs().
        Default is False.
    **kwargs
        Additional keyword arguments are passed directly to `seaborn.catplot`. This allows customization of
        plot features such as `aspect`, `errorbar`, height`, etc.
    """
    # Force variables to be a list
    if not isinstance(fields, list):
        fields = [fields]
    if isinstance(layers, str):
        layers = [layers]

    # Retrieve metadata
    yaxis_label = yaxis_label or fields[0].metadata['name']
    unit = unit or fields[0].metadata['units']
    layers = layers or fields[0].layers

    # Check valid labels
    if len(fields) > 1 and field_labels is None:
            raise ValueError("field_labels must be defined when there are more than one field.")

    # Convert all series to DataFrames with flattened structure
    combined_data = []
    for i, field in enumerate(fields):
        label = field_labels[i]
        if gridop: # Reduce grid if gridop is provided
            field.red_space(gridop,inplace=True)
        df = cp.make_lines(field)

        for layer in layers:
            data = df[layer].values.flatten()
            combined_data.append(pd.DataFrame({
                "value": data,
                "series": label,
                "layer": layer
            }))

    df_long = pd.concat(combined_data, ignore_index=True)

    # Get color palette
    colors, color_dict = get_color_palette(len(field_labels), palette=palette, custom_palette=custom_palette)
    palette = {label: color for label, color in zip(field_labels, colors)}

    # Set axes depending on orientation
    x, y = ("value", "layer") if horizontal else ("layer", "value")

    # Base arguments
    plot_kwargs = {
        "data": df_long,
        "x": x,
        "y": y,
        "hue": "series",
        "kind": plot_type,
        "palette": palette,
        "height": y_fig,
        "aspect": x_fig / y_fig
    }


    plot_kwargs.update(kwargs)

    # Recommended arguments
    if plot_type == "box" or plot_type == "boxen":
        plot_kwargs["fill"] = False
        plot_kwargs["showfliers"] = False
        plot_kwargs["gap"] = 0.1
    if plot_type == "violin":
        plot_kwargs["inner"] = None
        plot_kwargs["bw_method"] = 1
        if len(fields) == 2:
            plot_kwargs["split"] = True

    # Create the catplot
    fig = sns.catplot(**plot_kwargs)

    ax = fig.ax  # Extract the main axis

    # Set labels and title
    axis_label = f"{yaxis_label} (in {unit})" if unit != "[no units]" else yaxis_label
    if horizontal:
        ax.set_xlabel(axis_label, fontsize=16)
        ax.set_ylabel("")
    else:
        ax.set_ylabel(axis_label, fontsize=16)
        ax.set_xlabel("")

    ax.tick_params(labelsize=14)
    if title:
        ax.set_title(title, fontsize=16)

    if not horizontal and vertical_xlabels: # Rotate x-axis labels if requested
        ax.set_xticklabels(ax.get_xticklabels(), rotation=90)

    # Custom legend (colored labels, no box)
    fig._legend.remove()
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles=[plt.Line2D([], [], color=palette[label], marker='', linestyle='') for label in labels],
              labels=labels, handlelength=0, handletextpad=0, labelcolor=[palette[label] for label in labels],
              loc='best', frameon=False, fontsize=14)

    # Apply dark mode
    if dark_mode:
        fig, ax = make_dark_mode(fig.fig, ax)

    return handle_figure_output(fig, output_file=output_file, return_fig=return_fig, transparent=transparent)
