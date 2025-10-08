"""base module unitary tests"""

import os
import pytest
import tekigo.base as tbase
import math
import numpy as np
from h5cross import hdfdict as h5d
import h5py


# Unitary tests
def test_estimate_nodes_number():
    met_field = 0.3
    assert int(1000.0 / 27.0) == tbase._estimate_nodes_number(met_field)


def test_estimate_volume_at_node():
    """estimation of node numer test"""
    assert 2.7 == tbase._estimate_volume_at_node(0.1, 3.0)


def test_compute_metric():
    criteria = {
        "crit1": 0.4,
        "crit2": 0.2,
    }

    params = {
        "max_refinement_ratio": 0.3,
        "met_mix": "average",
        "n_node": 2,
    }

    assert math.isclose(tbase.compute_metric(criteria, **params), 0.91)

    criteria = {
        "crit1": np.array([0.2, 0.5]),
        "crit2": np.array([0.4, 0.3]),
    }

    params["met_mix"] = "abs_max"

    assert np.array_equal(
        np.array([0.88, 0.85]), tbase.compute_metric(criteria, **params)
    )


def test_filter_metric():

    params = {"nnode_tgt": 34, "min_vol": 0.01, "max_vol": 10, "gamma": 0.8}

    vol_node = 0.01
    met_field = np.ones(50) * 0.3
    met_field_clean = tbase.filter_metric(vol_node, met_field, **params)
    assert np.all(np.abs((np.ones(50) - met_field_clean)) < 10e-9)


def test_update_h5_file(datadir, h5same_files):
    """testing h5 criteria updater"""
    filename = datadir.join("tekigo_update.sol.h5")
    data_dict = dict()
    data_dict["crit_none"] = [0.0 for i in range(103895)]

    tbase.update_h5_file(filename, "Adapt", data_dict)

    try:
        h5same_files(filename, datadir.join("tekigo_update_tgt.sol.h5"))
    except AttributeError:
        print("Issue of loading the hdf5 file with hdfdict in arnica")
