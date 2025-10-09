# ----------------------------------------------
# | Tests for comparison plotting using canopy |
# ----------------------------------------------

import pytest
from pathlib import Path
import matplotlib
matplotlib.use('Agg')  # Set non-GUI backend before pyplot import
from canopy import Field
import canopy.visualization as cv

DATA_DIR = Path("tests/test_data")

@pytest.mark.filterwarnings("ignore:FigureCanvasAgg is non-interactive, and thus cannot be shown:UserWarning")
@pytest.mark.filterwarnings("ignore:.*vert.*will be deprecated.*:PendingDeprecationWarning")
def test_make_comparison_plot():
    """Test that make_comparison_plot works on two test fields."""

    field_a = Field.from_file(DATA_DIR / "anpp_spain_1990_2010.out.gz")
    field_b = Field.from_file(DATA_DIR / "anpp_spain_1990_2010_mod.out.gz")

    cv.make_comparison_plot(
        fields=[field_a,field_b],
        plot_type="box",
        layers=["Abi_alb","Bet_pen","Bet_pub","Que_rob","C3_gr"],
        yaxis_label="Actual NPP",
        field_labels=["no mod", "mod"],
        unit="kgC m-2",
        title="Actual NPP in Spain (1990-2010)", 
        palette="tab10", 
        dark_mode=True, 
        transparent=False,
        x_fig=10,
        y_fig=10,
        aspect=0.5
        )