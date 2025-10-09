import numpy as np
import pandas as pd
from canopy.core.field import Field


def check_field_contains_layers(field: Field, layers: str | list[str], name: str = 'field'):
    """Check if field contains required layers

    Parameters
    ----------
    field : Field
        The field whose layers to check
    layers : str | list[str]
        A string or a list of strings, identifying the required layer(s)
    name: str = 'field'
        The name of the field for message printing purposes
    """
    if isinstance(layers, str):
        layers = [layers]

    not_found = []
    for layer in layers:
        if layer not in field.layers:
            not_found.append(layer)

    if len(not_found):
        raise ValueError(f"Layers {not_found} not found in {name}'s layers ({field.layers}).")


def check_spatial_coords_match(field1: Field, field2: Field, tolerance: int | float = 1.e-6):
    """Check if spatial coordinates of two fields match up to given tolerance

    Parameters
    ----------
    field1 : Field
        The first of the two fields whose coordinates to compare
    field2 : Field
        The second of the two fields whose coordinates to compare
    tolerance : int | float
        Absolute tolerance to apply in the comparison

    Notes
    -----
    Two fields with one site with coordinates (12.23, -32.56) and (12.234, -32.561) will match up to a
    tolerance of 0.01, but not 0.001.
    """

    gridlist1 = np.array(field1.data.index.droplevel('time').drop_duplicates().to_frame())
    gridlist2 = np.array(field2.data.index.droplevel('time').drop_duplicates().to_frame())
    try:
        gridlists_match = np.allclose(gridlist1, gridlist2, atol=tolerance)
    # If gridlists don't have the same length, the above comparison will fail
    except ValueError:
        gridlists_match = False
    if not gridlists_match:
        raise ValueError("Gridlists do not match.")


def check_indices_match(field1: Field, field2: Field, tolerance: int | float = 1.e-6):
    """Check if the indices of the DataFrames of two fields match

    Parameters
    ----------
    tolerance
        Absolute tolerance to apply in the spatial coordinate comparison
    field1 : Field
        The first of the two fields whose coordinates to compare
    field2 : Field
        The second of the two fields whose coordinates to compare
    """

    index1 = field1.data.index
    index2 = field2.data.index

    if len(index1) != len(index2):
        raise ValueError("Indices have different lenghts.")

    # Check spatial axes
    indices_match = []
    for i in range(2):
        axis1 = index1.get_level_values(i)
        axis2 = index2.get_level_values(i)
        if axis1.dtype != axis2.dtype:
            indices_match.append(False)
            continue
        if isinstance(axis1[0], str) and axis1[0] == axis2[0]:
            indices_match.append(True)
        elif isinstance(axis1[0], str) and axis1[0] != axis2[0]:
            indices_match.append(False)
        else:
            try:
                indices_match.append(np.allclose(axis1, axis2, atol=tolerance))
            except ValueError:
                indices_match.append(False)

    # Check time axis
    timeax1 = index1.get_level_values('time')
    timeax2 = index2.get_level_values('time')
    try:
        indices_match.append((timeax1 == timeax2).all())
    except ValueError:
        indices_match.append(False)

    if not all(indices_match):
        non_matching = list(np.where(np.logical_not(indices_match))[0])
        raise ValueError(f"Field indices {non_matching} do not match.")
