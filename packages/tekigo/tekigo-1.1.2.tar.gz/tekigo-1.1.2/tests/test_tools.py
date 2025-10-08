"""tools tests module"""

import tekigo.tools as tools
import numpy as np


# unitary tests
def test_node_volume_approx():
    """approximation of node volume from cells volumes"""
    node_vol_tgt = 1.0
    edge_tgt = 1.0
    cell_tgt = 1.0

    assert node_vol_tgt == tools.approx_vol_node_from_vol_cell(1.0 / 4.5)
    assert node_vol_tgt == tools.approx_vol_node_from_edge(
        np.power(4.0 * np.sqrt(2.0) / 3.0, 1.0 / 3.0)
    )
    assert cell_tgt == tools.approx_vol_cell_from_vol_node(1.0 * 4.5)
    assert edge_tgt == tools.approx_edge_from_vol_node(3.0 / (4.0 * np.sqrt(2.0)))
