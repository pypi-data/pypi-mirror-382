"""Main functions for Tékigô"""

import numpy as np
from loguru import logger
from tekigo.base import (
    get_mesh_infos,
    update_h5_file,
    compute_metric,
    filter_metric,
)
from tekigo.tkg_logging import (
    logging_mesh,
    logging_pyhip,
    logging_banner,
)
from tekigo.tools import approx_vol_node_from_edge
from tekigo.hipster import hip_adapt, hip_process


def calibrate_metric(
    tekigo_sol,
    custom_criteria,
    target_ncells,
    edge_min=1.0e-12,
    edge_max=1.0e-2,
    allow_coarsening=True,
    met_mix="abs_max",
    gamma=0.8,
):
    """
    Clip and rescale metric to meet global contraints NCELLS and EDGE_MIN.

    As this is a compromise between opposed constraints, the method is not always converging.
    Put some sense in your inputs!

    Args :
        tekigo_solution: TekigoSolution object
        custom_criteria (dict): dict of numpy arrays btw -1 (coarsen), 0 (keep as is) and 1 (refine)

        target_ncells (int): number of cells in the desired mesh
        edge_min (float): minimal edge size, metric yielding smaller sizes will be clipped
        allow_coarsening (bool): if False, no metric higher than 1 will be allowed.
        met_mix (str): method to mix the different criterias


    Returns:
        metric_field_filter (array) :  the metric clipped and rescaled.

    ..Note:
        About met_mix:
        - abs_max: takes the absolute maximum (-.3 and 0.7 yields 0.7, -0.9 and 0.1 yields -0.9)
        - average : average among criterias  (-.3 and 0.7 yields 0.2, -0.9 and 0.1 yields -0.4)
    """
    logging_banner("Calibrating metric....")

    _criteria_range_check(custom_criteria, allow_coarsening)

    metric_field = compute_metric(
        custom_criteria,
        met_mix,
        tekigo_sol.mesh_infos["nnode"],
    )

    min_vol = approx_vol_node_from_edge(edge_min)
    max_vol = approx_vol_node_from_edge(edge_max)
    nnode_tgt = int(
        tekigo_sol.mesh_infos["nnode"] * target_ncells / tekigo_sol.mesh_infos["ncell"]
    )

    metric_field_filter = filter_metric(
        tekigo_sol.mesh_infos["vol_node"],
        metric_field,
        nnode_tgt,
        min_vol,
        max_vol,
        gamma,
    )
    return metric_field_filter


def adaptation_pyhip(
    tekigo_sol,
    max_spacing_gradient=1.4,
    hausdorff_distance=None,
    periodic_adaptation=False,
    frozen_patch_list=None,
    edge_high=None,
    edge_low=None,
    vol_min=None,
):
    """
    Performs a hip adaptation on a tekigo solution

    Args :
        tekigoSol (obj) : TekigoSOlution object
        max_spacing_gradient (float): spacing gradient used to smooth the mesh (smoother if closing to 1)
        hausdorff_distance (float): control curvatuvre fidelity on CADs.
        periodic_adaptation (bool): allow adaptation on periodic patches
        frozen_patch_list (list): list of strings, pathecs that must not be changed
        edge_high (float): MMG3D will try to not get edges higher than this
        edge_low (float): MMG3D will try to not get edges lower than this
        vol_min (float): MMG3D will try to remove cells with volume lower than this

    Returns :
        f_nnode (int): final nb. of nodes
        f_ncell (int): final nb. of cells
        f_hmin (float): final minimal edge length

    """
    logging_banner("Starting Adaptation using PyHIP/MM")

    logging_pyhip(
        hausdorff_distance,
        frozen_patch_list,
        max_spacing_gradient,
        periodic_adaptation,
    )

    hip_cmd_lines = hip_adapt(
        tekigo_sol.init_mesh,
        tekigo_sol.init_sol,
        tekigo_sol.final_prefix,
        max_spacing_gradient,
        hausdorff_distance,
        frozen_patch_list,
        metric_field="metric",
        periodic_adaptation=periodic_adaptation,
        edge_low=edge_low,
        edge_high=edge_high,
        vol_min=vol_min,
    )
    logger.info("------ HIP script -------")
    logger.info("\n".join(hip_cmd_lines))
    logger.info("-----------------------\n")

    logger.info("------ HIP log -------")
    hip_process(hip_cmd_lines=hip_cmd_lines, mesh_file=tekigo_sol.init_mesh)
    logger.info("--- end of  HIP log -------\n")

    # Recall init Mess
    logging_mesh(
        "Initial mesh",
        tekigo_sol.mesh_infos["nnode"],
        tekigo_sol.mesh_infos["ncell"],
        tekigo_sol.mesh_infos["hmin"],
    )

    # Final mesh
    f_hmin, f_ncell, f_vol_node = get_mesh_infos(f"{tekigo_sol.final_prefix}.mesh.h5")
    f_nnode = f_vol_node.shape[0]
    logging_mesh("Final mesh", f_nnode, f_ncell, f_hmin)

    # Transfer final node volume to solution file
    update_h5_file(
        f"{tekigo_sol.final_prefix}.sol.h5",
        parent_group="Adapt",
        data_dict={"vol_node": f_vol_node},
    )
    return f_nnode, f_ncell, f_hmin


# --------- PRIVATE ---------


def _criteria_range_check(criteria, coarsen):
    """Check if the ranges of the criteria are out of bounds

    :param criteria: dictionnary holding criteria for mesh adaptation
    :type criteria: dict( )

    :returns: None
    """

    over_crit_max = [np.any(criteria[variable] > 1.0) for variable in criteria]
    if coarsen:
        min_limit = " -1"
        over_crit_min = [np.any(criteria[variable] < -1.0) for variable in criteria]
    else:
        over_crit_min = [np.any(criteria[variable] < 0.0) for variable in criteria]
        min_limit = " 0"

    if any(over_crit_max + over_crit_min):
        crit_max_names = [
            crit_name for i, crit_name in enumerate(criteria) if over_crit_max[i]
        ]
        crit_min_names = [
            crit_name for i, crit_name in enumerate(criteria) if over_crit_min[i]
        ]
        line = "Change the range of the following criteria" + "\n"
        if crit_max_names:
            line += (
                str(crit_max_names)[1:-1] + "contains a value(s) larger than 1" + "\n"
            )
        if crit_min_names:
            line += (
                str(crit_min_names)[1:-1]
                + "contains a value(s) smaller than"
                + min_limit
            )

        logger.error(line)
        raise ValueError(line)
