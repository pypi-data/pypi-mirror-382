"""Grid associated to site-based data.

This Grid type actually represents the absence of a grid. It is meant to describe a
collection of unrelated sites or locations. Spatial reduction operations are only defined
for both axes (axis = 'both').
"""

import numpy as np
import pandas as pd
import copy
from typing import Optional
from canopy.grid.grid_abc import Grid
from canopy.grid.registry import register_grid, register_gridop

grid_type = 'sites'

@register_grid(grid_type)
class GridSites(Grid):
    """A subclass of Grid used to represent a collection of sites.

    Parameters
    ----------
    sites
        The site locations are arranged in rows. For example:
        .. code-block::
        
            [[12.25, -4.75],
             [-27.75, 45.25],
             [-50.25, 73.25]]
    axis0 : str
        Name of first axis (default: 'lon').
    axis1 : str
        Name of second axis (default: 'lat').
    """

    def __init__(self, sites: np.ndarray, axis0: str = 'lon', axis1: str = 'lat') -> None:
        super().__init__(grid_type, axis0=axis0, axis1=axis1)
        self.sites: np.ndarray = sites
        self.axis_gridop['both'] = None


    @classmethod
    def from_frame(cls, df):
        """Create a GridSites instance from a DataFrame.

        Parameters
        ----------
        df : pd.DataFrame
            A pandas DataFrame with a valid format (see Field documentation).

        Returns
        -------
        An instance of the grid subclass.
        """
        index = df.index
        axis0, axis1 = index.names[:2]
        sites = np.array(list(index.droplevel('time').drop_duplicates().values))
        return cls(axis0 = axis0, axis1 = axis1, sites=sites)


    def get_reduced_grid(self, gridop: str, axis: str) -> Grid:
        """Create a new grid, reduced according to the parameters

        Parameters
        ----------
        gridop : str
            The reduction operation
        axis : str
            The axis to be reduced

        Returns
        -------
        An instance of GridSites
        """
        grid = copy.deepcopy(self)
        if axis == 'both':
            for k in self.axis_gridop:
                grid.axis_gridop[k] = gridop
            grid.sites = np.empty(0)
        else:
            raise ValueError(f"Axis '{axis}' can't be reduced for grid type '{grid_type}'.")
        
        return grid


    def get_sliced_grid(self,
                        axis0_slice: Optional[tuple[float,float]] = None,
                        axis1_slice: Optional[tuple[float,float]] = None) -> Grid:
        """Create a new grid, sliced according to the parameters.

        Parameters
        ----------
        axis0_slice : tuple[float,float]
            Specifies an interval on axis0.
        axis1_slice : tuple[float,float]
            Specifies an interval on axis1.

        Returns
        -------
        An instance of the grid subclass.
        """
        sites = self.sites
        if axis0_slice is not None:
            x0 = sites[:,0]
            x0min, x0max = axis0_slice
            sites = sites[(x0 >= x0min) & (x0 <= x0max)]
        if axis1_slice is not None:
            x1 = sites[:,1]
            x1min, x1max = axis1_slice
            sites = sites[(x1 >= x1min) & (x1 <= x1max)]

        return GridSites(sites, axis0 = self.axis_names[0], axis1 = self.axis_names[1])
        

    def is_compatible(self, other) -> bool:

        if self.grid_type != other.grid_type:
            return False

        if self.axis_gridop != other.axis_gridop:
            return False

        return True


    def __add__(self, other):

        if not self.is_compatible(other):
            raise ValueError("Non-compatible grids cannot be aggregated.")

        sites = np.unique(np.vstack([self.sites, other.sites]), axis=0)

        return GridSites(sites)


    def __repr__(self) -> str:
        repr_str = [super().__repr__()]
        if self.is_reduced('both'):
            repr_str.append(f"Data is spatially reduced (gridop: '{self.axis_gridop['both']}').")
        else:
            repr_str.append(f"Gridlist:\n{str(self.sites)}")
        return '\n'.join(repr_str)


    def __str__(self) -> str:
        return self.__repr__()


@register_gridop(grid_type)
def av_both(df: pd.DataFrame, grid: Grid) -> pd.DataFrame:
    """Spatially average the data.
    
    On this 'grid', all sites count the same for the average.

    Parameters
    ----------
    df : pd.DataFrame
        The pandas DataFrame whose data is to be averaged.
    grid : GridSites
        A GridSites object.

    Returns
    -------
    A reduced pandas DataFrame
    """
    group_levels = ['time']
    df_red = df.groupby(group_levels).mean()
    #df_red = _restore_index(df_red, 'av')

    return df_red


@register_gridop(grid_type)
def sum_both(df: pd.DataFrame, grid: Grid) -> pd.DataFrame:
    """Spatially aggregate the data.

    On this 'grid', all sites count the same for the sum.

    Parameters
    ----------
    df : pd.DataFrame
        The pandas DataFrame whose data is to be aggregated.
    grid : GridSites
        A GridSites object.

    Returns
    -------
    A reduced pandas DataFrame
    """
    group_levels = ['time']
    df_red = df.groupby(group_levels).sum()
    #df_red = _restore_index(df_red, 'sum')

    return df_red

