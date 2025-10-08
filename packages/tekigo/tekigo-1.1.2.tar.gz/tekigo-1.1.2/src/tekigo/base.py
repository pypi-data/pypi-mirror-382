"""Base functions library for tekigo"""

import h5py
import numpy as np
import os.path as ospath
from loguru import logger


from tekigo.tools import approx_edge_from_vol_node

# The id of the line containing Metric quantity according to HIP
METRIC_NAME = "metric"


def update_h5_file(filename, parent_group, data_dict):
    """Update hdf5 file by adding a data dictionary to a parent group

    :param filename: the hdf5 file name
    :param parent_group: the parent group under which new datasests are appended
    :param data_dict: the data dictionary to append
    """
    if not ospath.isfile(filename):
        logger.warning(f"Creating void initial solution {filename}")
        with h5py.File(filename, "w") as h5f:
            h5f.create_group("Mesh")

    with h5py.File(filename, "r+") as h5f:
        if parent_group not in h5f:
            h5f.create_group(parent_group)

        for key in data_dict:
            if key in h5f[parent_group]:
                h5f[parent_group][key][...] = data_dict[key]
            else:
                h5f[parent_group][key] = data_dict[key]


def get_mesh_infos(mesh_f):
    with h5py.File(mesh_f, "r") as f_h:
        vol_node = f_h["VertexData"]["volume"][()]
        hmin = f_h["Parameters"]["h_min"][...][0]
        elem_type = list(f_h["Connectivity"].keys())[0]
        if elem_type == "tet->node":
            ncell = np.int_(f_h["Connectivity"]["tet->node"][...].shape[0] / 4)
        elif elem_type == "tri->node":
            ncell = np.int_(f_h["Connectivity"]["tri->node"][...].shape[0] / 3)
        else:
            raise ValueError("Unkown element type for computation of cell number")
    return hmin, ncell, vol_node


def metric_forecast(metric, mesh_file):
    with h5py.File(mesh_file, "r") as h5f:
        vol_node = h5f["VertexData"]["volume"][()]
    nnode_est = _estimate_nodes_number(metric)
    edge_est = metric * approx_edge_from_vol_node(vol_node)
    return nnode_est, edge_est


def estimate(metric, target):
    nnodes = _estimate_nodes_number(metric)
    rerror = (nnodes - target) / target
    return nnodes, rerror


def change_direction(direction, gamma, split_step=2):
    gamma_new = (1.0 / gamma) ** (
        1.0 / split_step
    )  # ca marche mais c'est pas utile on dirait
    direction_new = -direction
    return direction_new, gamma_new


def linear_by_part(x, x1, x2, gamma):
    """Compute a piecewise linear function with a global slope gamma but 'centered' on 1 with 2 markers (x1, x2) at which the slope changes."""

    if (gamma * x1 <= 0) or (gamma * x2 <= 1):
        raise ValueError(
            "Please reconsider your gamma or x1/x2 values as gamma*x1 >0 and gamma*x2 > 1"
        )

    a_1 = gamma
    a_2 = (gamma * x1 - 1) / (x1 - 1)
    b_2 = 1 - a_2
    a_3 = (gamma * x2 - 1) / (x2 - 1)
    b_3 = 1 - a_3

    funcs = [
        lambda x: a_1 * x,
        lambda x: a_2 * x + b_2,
        lambda x: a_3 * x + b_3,
        lambda x: a_1 * x,
    ]

    y = np.piecewise(
        x,
        [x <= x1, ((x > x1) & (x <= 1)), ((x > 1) & (x <= x2)), x > x2],
        [
            funcs[0],
            funcs[1],
            funcs[2],
            funcs[3],
        ],
    )
    return y


def filter_metric(
    vol_node,
    met_field,
    nnode_tgt,
    min_vol,
    max_vol,
    gamma,
):
    """Perform filtering on the metrics

    :param vol_node: the nodes volumes array
    :param met_field: the metric field to be filtered
    :param coarsen: boolean , allow coarsening or not
    :param nnode_tgt: limit the final number of nodes
    :param min_vol: limit the min volume
    :param max_vol: limit the max volume(coarsen specific)


    :returns: - nnode_est : estimation of new number of nodes
              - met_field : metric field
    """

    nnode_est = _estimate_nodes_number(met_field)
    logger.info(
        f"""
    |  _filter_metric
    |       nnode_tgt  : {str(nnode_tgt)} 
    |          min_vol : {str(min_vol)}
    |          max_vol : {str(max_vol)}
    |  nnode_est start : {str(nnode_est)}

"""
    )

    X1 = 0.5
    X2 = 1.5

    direction = 1
    if gamma > 1:
        gamma = 1 / gamma
    iter_ = 0
    iter_max = 50
    eps = 0.001
    nnode_est, rerror = estimate(met_field, nnode_tgt)

    if rerror > nnode_tgt:
        direction, gamma = change_direction(direction, gamma)

    logger.info(
        f"\n    |first met field min:{np.min(met_field):.2f} max:{np.max(met_field):.2f}\n"
    )
    logger.info(f"\n    | gamma start: {gamma:.2f}")
    # storage
    # print(iter_, nnode_est, gamma, rerror)

    while abs(rerror) > eps and iter_ < iter_max:
        iter_ += 1
        msg = f"\n Loop {iter_}"
        if nnode_est > nnode_tgt and direction == 1:
            direction, gamma = change_direction(direction, gamma)
            msg += f"\n    | Change of direction hence change of gamma :{gamma:.2f}"

        if nnode_est < nnode_tgt and direction == -1:
            direction, gamma = change_direction(direction, gamma)
            msg += f"\n    | Change of direction hence change of gamma :{gamma:.2f}"

        if gamma > 1:
            msg += "\n    | Coarsening..."
        else:
            msg += "\n    | Refining..."

        msg += f"\n    | linear_by_part treatment ... \n"

        met_field = linear_by_part(met_field, X1, X2, gamma)

        msg += f"\n    | met field min:{np.min(met_field):.2f} max:{np.max(met_field):.2f}\n"

        # Correcting metric field based on max and min volume allowed
        msg += "    | Volume clipping ...\n"
        vol_est = _estimate_volume_at_node(vol_node, met_field)

        met_field = np.where(
            vol_est > min_vol,
            met_field,
            np.power(min_vol / vol_node, 1.0 / 3.0),
        )

        met_field = np.where(
            vol_est < max_vol,
            met_field,
            np.power(max_vol / vol_node, 1.0 / 3.0),
        )

        nnode_est, rerror = estimate(met_field, nnode_tgt)

        msg += f"\n    | nnodes {nnode_est} vs {nnode_tgt} "

        #     #met_field = np.clip(met_field, clip_metric_min, clip_metric_max)
        #     nnode_est = _estimate_nodes_number(met_field)
        msg += (
            f"\n    | met field min:{np.min(met_field):.2f} max:{np.max(met_field):.2f}"
        )

        logger.info(msg)
    logger.info(
        f"Metric reached {(nnode_est / nnode_tgt)*100} % of target in {iter_} iterations"
    )

    return met_field


def compute_metric(criteria, met_mix, n_node, max_refinement_ratio=0.6):
    r"""
        Calculate metric and estimates new number of nodes
        given refinement criteria and criteria choice method ('met_mix' parameter)

        :param criteria: a dictionary holding refinement criteria
        :type criteria: dict( )
        :param met_mix: type of metric mixing calculation method:

    if the criteria choice method is set on "average", the metric is computed as follows:

        .. math:: Metric = 1 - Rr_{max} < C >_i

        if the criteria choice method is set on "abs_max", the metric is computed as follows:

        .. math:: Metric = 1 - Rr_{max} \, C_i |_{ \tiny \displaystyle \max_{i \, \in \, C} | C_i |}

        with Metric and C (criteria) vectors of size n_nodes, Rr as Refinement ratio.

        :type met_mix: string
        :param n_node: current number of nodes
        :type n_node: integer
        :param max_refinement_ratio: refinement parameter for metric computation
        :type max_refinement_ratio: float

        :returns: metric field
    """
    met_field = np.ones(n_node) * 2.0
    if met_mix == "average":
        met_field = 0.0
        for crit in criteria:
            met_field = met_field + (1.0 - criteria[crit] * max_refinement_ratio)
        met_field = met_field / float(len(criteria))
    elif met_mix == "abs_max":
        max_crit = np.zeros(n_node)
        for crit in criteria:
            crit_value = criteria[crit] * max_refinement_ratio
            cond = np.abs(max_crit) > np.abs(crit_value)
            max_crit = np.where(cond, max_crit, crit_value)
        met_field = 1.0 - max_crit
    else:
        pass

    return met_field


# ------------------- PRIVATE -------------------
# internal methods
def _estimate_nodes_number(met_field):
    """Estimates nodes number given the metric field

    Parameters :
    ==========
    met_field_array : metric field
    vol_node : the nodes volumes array

    Returns :
    =======
    node_est : an estimation of the number of nodes
    """

    node_est = int(np.sum(1.0 / (met_field**3)))
    return node_est


def _estimate_volume_at_node(current_volume, met_field):
    """Estimates volume_at_nodes given the metric field

    Parameters :
    ==========
    met_field_array : metric field
    vol_node : the nodes volumes array

    Returns :
    =======
    node_est : an estimation of the number of nodes
    """

    volume_est = current_volume * met_field**3.0

    return volume_est
