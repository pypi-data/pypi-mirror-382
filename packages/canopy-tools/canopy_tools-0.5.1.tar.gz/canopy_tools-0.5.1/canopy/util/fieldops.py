import numpy as np
import pandas as pd
import copy
from typing import Optional, Hashable, Type, cast
from canopy import RedSpec, Raster, Field
from canopy.grid import get_grid_type
from pandas.api.types import is_string_dtype
from canopy.util.checks import check_spatial_coords_match

# Make raster
# -----------
def gcidx(x: float, xmin: float, dx: float) -> int:
    return int((x-(xmin-0.5*dx))/dx)
get_coord_index = np.vectorize(gcidx)

def make_raster(field: Field, layer: str) -> Raster:
    """Produce a Raster object from a Field

    Parameters
    ----------
    field : Field
        The field object from which to create the Raster
    layer : str
        The field layer to rasterize
    """

    data = field.data
    grid = field.grid

    # This is to avoid mypy errors.
    # TODO: find a better solution. Maybe Rasterizable Grid?
    grid_type = get_grid_type(grid) 
    if grid_type != 'lonlat':
        raise ValueError("make_raster currently supports only 'lonlat' grid type.")
    from canopy.grid.grid_lonlat import GridLonLat
    grid  = cast(GridLonLat, grid)

    ilon = get_coord_index(data.index.get_level_values('lon').to_numpy(), grid.lon_min, grid.dlon)
    ilat = get_coord_index(data.index.get_level_values('lat').to_numpy(), grid.lat_min, grid.dlat)

    # Create Raster
    xx, yy = np.meshgrid(grid.lon, grid.lat)

    vmap = np.empty([grid.lat.size, grid.lon.size], dtype=float)
    vmap[:] = np.nan
    dtype = data.dtypes[layer]
    if is_string_dtype(dtype):
        labels = dict(enumerate(data[layer].unique()))
        labels_r = {v: k for (k, v) in labels.items()}
        values = np.vectorize(labels_r.get)(data[layer].values)
        vmap[ilat,ilon] = values
    else:
        labels = None
        vmap[ilat,ilon] = data[layer].values
    
    return Raster(xx, yy, vmap, labels)


# Make lines
# ----------
def make_lines(field: Field, axis: str = 'time') -> pd.DataFrame:
    """Create a pandas DataFrame with the field's data unstacked along the specified axis

    This DataFrame is much easier to use to plot lines (e.g. with df.plot())

    Parameters
    ----------
    field : Field
        The field from which to create the DataFrame
    axis: str
        The axis along which to unstack the data
    """

    df = field._data.copy()
                         
    if field._grid.is_reduced('lon'):
        df.index = df.index.droplevel('lon')
    if field._grid.is_reduced('lat'):
        df.index = df.index.droplevel('lat')

    levels = cast(Hashable, [x for x in df.index.names if not x == axis])
    return cast(pd.DataFrame, df.unstack(level=levels))


# Concatenate two fields
# ----------------------

def concat2(field1: Field, field2: Field) -> Field:
    """Concatenate two fields along the time axis.

    The fields must have matching grids and compatible ('concatenable') time series.

    Parameters
    ----------
    field1 : Field
        The first field to concatenate
    field2 : Field
        The second field to concatenate

    Returns
    -------
    A Field object with the concatenated data
    """

    # These will always be MultiIndex
    index1 = cast(pd.MultiIndex, field1._data.index)
    index2 = cast(pd.MultiIndex, field2._data.index)
    columns1 = field1._data.columns.sort_values()
    columns2 = field2._data.columns.sort_values()

    # Check that fields have the same layers
    try:
        layers_match = (columns1 == columns2).all()
    # If layer number doesn't match, the above comparison will fail
    except ValueError:
        layers_match = False
    if not layers_match:
        raise ValueError(f"The fields have different layers (field1: {columns1}; field2: {columns2}).")

    # Check that temporal frequencies match
    freq1 = index1.levels[-1].dtype
    freq2 = index2.levels[-1].dtype
    if freq1 != freq2:
        raise ValueError(f"The time indices of the fields have different frequencies (field1: {freq1}; field2: {freq2}).")

    # Check that time series are concatenable
    period1 = index1.droplevel(['lon', 'lat']).drop_duplicates()[-1]
    period2 = index2.droplevel(['lon', 'lat']).drop_duplicates()[0]
    if period1 + 1 != period2:
        raise ValueError(f"Time series are not consecutive (last period of field1: {period1}; first period of field2: {period2}).")

    check_spatial_coords_match(field1, field2)

    grid = copy.deepcopy(field1._grid)

    df = pd.concat([field1._data, field2._data]).sort_index()
    return Field(df, grid)


# Merge fields
def merge_fields(field_list: list[Field]) -> Field:
    """Merge fields defined in compatible grids.

    The fields must have compatible grids and contain the same layers.

    Parameters
    ----------
    field_list: list[Field]
        List of fields to merge

    Returns
    -------
    A new Field with the merged data.
    """

    # Check that layers are the same for all fields
    layers = field_list[0].layers
    for field in field_list[1:]:
        if field.layers != layers:
            raise ValueError("Fields must contain the same layers")

    # Combine all the grids
    grids = [field.grid for field in field_list]
    grid = sum(grids[1:], start=grids[0])

    # Concatente data along index axes
    data = pd.concat([field.data for field in field_list])

    # Remove rows with duplicated indices
    data = data.loc[~data.index.duplicated(keep='first'), :]

    return Field(data, grid)

