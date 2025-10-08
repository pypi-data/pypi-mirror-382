"""

The main goal of this tekigo indirect mesh adaptation script is to create a metric defined via an input yaml file 
and perform the adaption using either hip or kalpataru (WIP)
The metric generated has the particullarity of being created using an indirect approach, where the local values of 
the metric are not directly defined from physical values but rather come from a global recipe which targets a specific
cell number and size. The global topology of where the refinement should occur is defined using physical fields, 
but only the topology is conserved, no user defined local metric value exist per se. 
( i.e the metric does not have a predifined value of let's say 0.5 at a specific node, the metric value is automatically
 constructed by flaging this node as 'must be refined' )

The script use a yaml file as input with the following architecture:

Reminders on Indirect Adaptation:
As indirect adaptation is performed here, criterion refers to a field mapped with values ∈ [-1, 1].
1 stands for "refining" and -1 stands for "coarsening". The criterion is defined buy the user.
From these criteria, "metric field" is build by tekigo calibrate_metric() function.
This function represents an optimisation process taking the target cells number and the user defined criteria as constraints.
Each value of the metric field represents the multiplying factor applied to the corresponding edge.
The metric field is passed to Hip through adaptation_pyhip() function, to proceed to the mesh adaptation.


                      ┌────────────┐                     ┌──────────────────┐         ┌──────────────────┐
Average solution ────►│User defined│    List of user     │                  │  Metric │                  │
                      │            ├────────────────────►│calibrate_metric()├────────►│adaptation_pyhip()├─────► Adapted mesh
Metric parameter ────►│  Criteria  │  defined criteria   │                  │  field  │                  │
                      └────────────┘                     └──────────────────┘         └──────────────────┘

"""

import numpy as np
import sys, os, glob


from tekigo import TekigoSolution, adaptation_pyhip, calibrate_metric
from tekigo.hipster import popen_execute


def _tanh_smoothing(
    field: np.array,
    mean: float,
    delta_x: float,
    lower_bound: float = 0,
    upper_bound: float = 1,
    reverse: bool = False,
    tol=None,
) -> np.ndarray:
    """
      Apply tanh(x) profile to the field given as argument.
      Two modes are provided, using tolerance or delta_x.
      Caution : wrong result are returned if 'mean' is negative

     upper_bound ------------|------------
                   |     ________
                   |    /
                   |---o---0.95
                   |  /|
                   | / |
                   |/  |
              0.5--o   |
                  /|   |
                 / |   |
                /  |   |
        0.05---o---|   |
      ________/|   |   |
    lower_bound ---------+---|---+---------
               |   |   |
               | mean  |
               |       |
               <delta_x>

      args:
          - delta_x :
          - mean :
          - tol (tolerance) : tol ∈ [0,1]. (1+tol)*mean gives the value at which tanh will evaluate to 0.95.
      returns:
          - tanh(x) profile applied to the given field

    Args:
        field (array): _description_
        mean (_type_): value at which tanh evaluate to 0.5.
        delta_x (_type_): spread between 0.05 and 0.95
        lower_bound (int, optional): Lower y value of the tanh. Defaults to 0.
        upper_bound (int, optional): Upper y value of the tanh. Defaults to 1.
        reverse (bool, optional): Specify if the tanh is increasing (False) or decreasing(True) between its bounds. Defaults to False.
        tol (float, optional): (tolerance) : tol ∈ [0,1]. (1+tol)*mean gives the value at which tanh will evaluate to 0.95.. Defaults to None.

    Returns:
        _type_: _description_
    """

    if mean < 0:
        print("Caution : wrong result are returned if 'mean' is negative")
        return None
    if tol is not None and delta_x is not None:
        print("Tolerance and delta options can not be used at the same time")
        return None
    if tol is None and delta_x is None:
        print("Tolerance or delta option should be selected")
        return None
    if delta_x is not None and delta_x == 0:
        print("Delta x is equal to 0, thus the profile will be set to 0 everywhere")
        return np.zeros_like(field)

    direction = 1
    if reverse:
        direction = -1

    if tol is not None:
        a = (mean * tol) / np.arctanh(0.9)
    elif delta_x is not None:
        a = delta_x / (2 * np.arctanh(0.9))

    profile = (
        lower_bound
        + (upper_bound - lower_bound)
        * (1 + direction * np.tanh((field - mean) / a))
        / 2
    )

    return profile


def _get_float(dico: dict, key: str, default=None):
    """Load a float var in a dictionary from a key.
        Return default if key is not present.
        Ensure that the input var from a yaml load is a float (i.e 1e5 is often read as a str in yaml)

    Args:
        dico (dict): input dictionary
        key (str): key to find
        default: default value returned if key not present.
    """
    var = dico.get(key, default)
    if var is not None:
        return float(var)
    else:
        return var


def patch_mask(mesh: str, patch_list: list) -> np.ndarray:
    """Create a mask(array of len(mesh)) with values equal to one around specific patches and zero everywhere else.

    Args:
        mesh (str): mesh file path
        patch_list (list): list of patches name where the mask is applied

    Returns:
        np.array: array of nnode containing the mask with 1 around the patches.
    """
    try:
        from pyavbp.io import mesh_utils
    except ImportError as e:
        raise ImportError(
            "You need access to pyavbp in order to use the patch mask functionality"
        )

    patch_params = mesh_utils.load_mesh_bnd(
        mesh, patchlist=patch_list
    )  # Retrieve patches parameters such as nodes coordinates and their indexes within the global mesh.
    patch_crit_raw = np.zeros(
        mesh_utils.get_mesh_params(mesh)["global"]["node_number"]
    )  # Build a numpy array of the mesh size length, full of 0.
    for patch in patch_params:
        indexes = (
            patch_params[patch]["gnodes"] - 1
        )  # Retrieve all global indexes of each selected patches.

        # ]  # Indexes are filtered to keep the ones satisfaying the condition. Ad hoc filtering for silvercrest configuration
        patch_crit_raw[indexes] = (
            1  # Switch from 0 to 1 for each index satisfaying the condition
        )

    return patch_crit_raw


def popen_execute(cmd, wk_dir="./"):
    """Execute command with contant feedback"""
    import subprocess

    popen = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=wk_dir,
        universal_newlines=True,
    )
    for stdout_line in iter(popen.stdout.readline, ""):
        print(stdout_line)
        sys.stdout.flush()
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)


def adaptation_treeadapt(
    input_dict,
    nb_proc,
    exec_treeadapt,
    out_name="teki_adapt_klptr",
    leaves=1,
    method="RIB",
    max_iter=1,
):
    """Perform the mesh adaptation using treeadapt in subprocess call

    Args:
        input_dict (_type_): dictionnary with treeadapt parameters
        nb_proc (_type_): number of partition for the adaptation
        exec_treeadapt (_type_): path for treeadapt executable
        out_name (str, optional): prefix of the outfile names. Defaults to "teki_adapt_klptr".
        leaves (int, optional): Number of leaves used by treeadapt. Defaults to 1.
        method (str, optional): Adaptation method ( see treeadapt ). Defaults to "RIB".
        max_iter (int, optional): Number of maximum adaption iterations. Defaults to 4.
    """
    ignore_groups = "Parameters Additionals Reactions"
    metric_data = "Adapt/target_edge"

    klptr_cmd = f""" mpirun -np {nb_proc}
    {exec_treeadapt}
    -l {int(leaves)}
    -p {method}
    -i {input_dict["init_mesh"].strip('.mesh.h5')}
    --metric-file {input_dict["metric_file"]}
    --metric-dset {metric_data}
    --iter-max {max_iter}
    --adapt-mesh-filename {out_name}
    --solution-file {input_dict["init_sol"]}
    --solution-group-ignore {ignore_groups}
    """
    print("------ Kalpataru/Treeadapt mesh Adaptation ------")
    print("TREEADAPT Command: ")
    print(klptr_cmd.replace("\n", ""))

    cmd = klptr_cmd.split()

    popen_execute(cmd)
    print("------ END of Kalpataru/Treeadapt mesh Adaptation ------")


def apply_mask(criteria, mask):
    """Apply the mask to the criteria"""
    criteria = criteria * (1 - mask) + criteria * mask * 0.2  # Why 0.2 ?
    return criteria


def propagate(
    criterion: np.array,
    gatscat,
    dilate_pass: int = 2,
    close_pass: int = 0,
    smooth_pass: int = 2,
) -> np.array:
    """Propagate the local values of a node array to neighbouring nodes using 3 different methods:
        - dilate: propagate the local MAXIMUM
        - erode: propagate the local MINIMUM
        - close: propagate the local MAXIMUM then the local MINIMUM
        - open : propagate the local MINIMUM then the local MAXIMUM
        - smooth: propagate the local AVERAGE
    Each 'pass' of these methods propagate the value to the first neighbouring nodes.

    Args:
        criterion (np.array): nnode array with original non propagated values.
        gatscat (GatherScatter): GatherScatter object of tekigosol
        dilate_pass (int, optional): Number of dilatation(pos)/erosion(neg) passes  . Defaults to 2 ( 2 dilate passes).
        close_pass (int, optional): Number of close(pos)/open(neg) passes. Defaults to 0.
        smooth_pass (int, optional): Number of smooth passes. Defaults to 2.

    Returns:
        np.array: nnode array with propagated values.
    """
    propagated_crit = np.copy(criterion)

    # Dilate/Erode Criterion
    if dilate_pass >= 1:
        propagated_crit = gatscat.dilate(propagated_crit, passes=dilate_pass)
    if dilate_pass <= -1:
        propagated_crit = gatscat.erode(propagated_crit, passes=abs(dilate_pass))

    # Open/Close Criterion
    if close_pass >= 1:
        propagated_crit = gatscat.close(propagated_crit, passes=close_pass)
    if close_pass <= -1:
        propagated_crit = gatscat.open(propagated_crit, passes=abs(close_pass))

    # Smooth Criterion
    if smooth_pass:
        propagated_crit = gatscat.smooth(propagated_crit, passes=smooth_pass)

    return propagated_crit


def coarsen_below_refine_above(field, means, delta_x=10):

    profile1 = _tanh_smoothing(field, means[0], delta_x, lower_bound=-1, upper_bound=0)
    profile2 = _tanh_smoothing(field, means[1], delta_x, lower_bound=0, upper_bound=1)

    # glob_min = max(min(bounds[0]), min(bounds[1]))
    # glob_max = min(max(bounds[0]), max(bounds[1]))
    # delta_glob = glob_min + glob_max
    delta_glob = 0  # sum of the maximum lower bound and the minimum upper bound
    profile = (profile1 + profile2) - delta_glob

    return profile


def refine_between(field, means, delta_x=10):

    profile1 = _tanh_smoothing(field, means[0], delta_x, lower_bound=0, upper_bound=1)
    profile2 = _tanh_smoothing(
        field, means[1], delta_x, lower_bound=0, upper_bound=1, reverse=True
    )

    delta_glob = 0 + 1  # sum of the maximum lower bound and the minimum upper bound
    profile = (profile1 + profile2) - delta_glob

    return profile


def get_allocated_cpus():
    """
    Retrieve the number of allocated CPUs for the current SLURM job.

    This function checks the environment variables:
    - SLURM_NPROCS: The number of allocated CPUs in a SLURM job( ex for kraken like machine)
    - BRIDGE_MSUB_NPROC: An alternative variable for CPU allocation.( ex for topaze like machines)

    Returns:
        int: The number of allocated CPUs if found.

    """
    # First attempt: using SLURM_NPROCS
    slurm_nprocs = os.getenv("SLURM_NPROCS")
    if slurm_nprocs is not None:
        return int(slurm_nprocs)

    # Second attempt: using BRIDGE_MSUB_NPROC
    bridge_msub_nproc = os.getenv("BRIDGE_MSUB_NPROC")
    if bridge_msub_nproc is not None:
        return int(bridge_msub_nproc)

    # If both variables are None, raise an error
    raise ValueError("No CPU allocation information available.")


def adapt_from_criteria(
    criteria: dict, input: dict, tekigo_sol: TekigoSolution, perform_adapt: bool = True
):
    """Calibrate a metric from a list of criteria and perform the mesh adaptation

    Args:
        criteria (dict): dictionary of criterion
        input (dict): input dict containing mesh adaptation targets
        tekigo_sol : TekigoSolution object
        perform_adapt (bool): specify if the mesh adaption via hip is performed
          or if only the metric is built.

    """

    # Computing the metric according to the different criteria.
    metric_field = calibrate_metric(
        tekigo_sol,
        criteria,
        target_ncells=_get_float(input, "target_cells"),
        edge_min=_get_float(input, "edge_min"),
        edge_max=_get_float(input, "edge_max", default=1e-2),
        met_mix="average",
        allow_coarsening=input.get("allow_coarsening", True),
    )

    # Forecast future mesh caracteristic from computed metric and mesh to adapt
    tekigo_sol.evaluate_metric(custom_metric=metric_field)

    if perform_adapt is True:
        # Proceed to actual mesh adaptation
        if input.get("kalpataru") == True:
            nb_proc = get_allocated_cpus()
            exec_treeadapt = input["exec_treeadapt"]
            input_dict = {}
            input_dict["init_sol"] = input["inst_sol_path"]
            input_dict["init_mesh"] = tekigo_sol.init_mesh
            input_dict["metric_file"] = tekigo_sol.init_sol

            adaptation_treeadapt(
                input_dict, nb_proc, exec_treeadapt, out_name=tekigo_sol.final_prefix
            )
            sol_name = glob.glob(f"{tekigo_sol.final_prefix}*.sfield.h5")[0]
            os.rename(sol_name, f"{tekigo_sol.final_prefix}.sol.h5")

            mesh_name = glob.glob(f"{tekigo_sol.final_prefix}*.mesh.h5")[0]
            os.rename(mesh_name, f"{tekigo_sol.final_prefix}.mesh.h5")

        else:
            adaptation_pyhip(
                tekigo_sol=tekigo_sol,
                periodic_adaptation=True,
                edge_low=_get_float(input, "edge_min"),
                max_spacing_gradient=_get_float(
                    input, "max_spacing_gradient", default=1.4
                ),
                vol_min=_get_float(input, "vol_min"),
            )

            # Suppress 'Average' field within interpolated solution. Otherwise, AVBP raises an error when attempting to start the simulation from this solution.
            tekigo_sol.make_restartable(input["tekigo_out_dir"])

    elif perform_adapt is None:
        try:
            from workflows_lemmings.ASMR.hip_mockup import hip_mockup
        except ImportError as e:
            raise ImportError("Access to workflows_lemmings needed for tests")

        print("Running hip mockup for test purposes")
        current_cells = tekigo_sol.mesh_infos["ncell"]
        target_ncells = _get_float(input, "target_cells")
        factor = target_ncells / current_cells
        hip_mockup(input["tekigo_out_dir"], factor=factor)


def load_var(crit: dict, tekigo_sol: TekigoSolution) -> np.ndarray:
    """Load in memory a specific quantity of interest depending on the source Group.

    Args:
        crit (dict): dictionary of criterion parameters
        tekigo-sol: TekigoSolution object

    Raises:
        NotImplementedError: All possible groups are not yet coded

    Returns:
        np.array: array of interest
    """

    if crit["var_type"] == "average":
        var = tekigo_sol.load_qoi(f"/Average/{crit['var_name']}")
    elif crit["var_type"] == "additionals":
        var = tekigo_sol.load_qoi(f"/Additionals/{crit['var_name']}")
    else:
        raise NotImplementedError("The variable type specified is not yet available")

    return np.array(var)


def read_yaml(file_path: str) -> dict:
    """Load a yaml input file and return its content as a dictionnay

    Args:
        file_path (str): path the yaml input file

    Returns:
        dict: content of the input
    """
    from yaml import load, SafeLoader

    with open(file_path, "r") as yaml_file:
        content = load(yaml_file, Loader=SafeLoader)
    return content


def run_tekigo(input_dict: dict):
    """Perform a tekigo mesh adaptation by creating a recipe of criteria
    and computing the related metric, all of this defined in an input dictionary.

    Args:
        input_dict (dict): dictionary with adaptation and criteria parameters
    """

    criteria_inpt = input_dict["criteria"]

    adapt = input_dict.get("adapt", True)

    # Failsafe for volume clipping
    if _get_float(input_dict, "edge_min") >= _get_float(
        input_dict, "edge_max", default=1
    ):
        raise ValueError(
            "edge_min in yaml file should be lower than edge_max ( default edge_max is 1m) !"
        )

    # Creation of TekigoSolution object.
    tekigo_sol = TekigoSolution(
        mesh=input_dict["mesh_path"],  # Mesh to adapt
        solution=input_dict[
            "inst_sol_path"
        ],  # Solution to interpolate onto the adapted mesh
        out_dir=input_dict["tekigo_out_dir"],
    )
    # Creation of GatherScatter object to apply propagation of criteria.
    gatscat = tekigo_sol.gatherscatter()

    ave_var = []
    for crit in criteria_inpt:
        if crit["var_type"] == "average":
            ave_var.append(crit["var_name"])
        if crit.get("rms"):
            ave_var.append(crit["var_name"] + "2")

    if input_dict.get("ave_sol_path"):
        # Add average fields to tekigo solution.
        tekigo_sol.add_fields_from_solution(
            input_dict["ave_sol_path"], "Average", ave_var
        )

    criteria_out = {}

    for crit in criteria_inpt:

        buff_crit = None
        type_crit = crit.get("crit_type")
        var = load_var(crit, tekigo_sol)
        if crit.get("rms"):
            var2 = tekigo_sol.load_qoi(f"/Average/{crit['var_name']}2")
            var = (var2 - var**2) ** 0.5

        if type_crit == "refine_above":
            # Width of the tanh ( default is percentage of target val)
            delta = _get_float(crit, "delta", 0.2 * crit["crit_vals"])
            buff_crit = _tanh_smoothing(var, crit["crit_vals"], delta)
        elif type_crit == "refine_below":
            delta = _get_float(crit, "delta", 0.2 * crit["crit_vals"])
            buff_crit = _tanh_smoothing(var, crit["crit_vals"], delta, reverse=True)
        elif type_crit == "coarsen_above":
            delta = _get_float(crit, "delta", 0.2 * crit["crit_vals"])
            buff_crit = _tanh_smoothing(
                var,
                crit["crit_vals"],
                delta,
                lower_bound=-1,
                upper_bound=0,
                reverse=True,
            )
        elif type_crit == "coarsen_below":
            delta = _get_float(crit, "delta", 0.2 * crit["crit_vals"])
            buff_crit = _tanh_smoothing(
                var,
                crit["crit_vals"],
                delta,
                lower_bound=-1,
                upper_bound=0,
            )
        elif type_crit == "coarsen_below_refine_above":
            delta = 0.1 * np.median(crit["crit_vals"])
            buff_crit = coarsen_below_refine_above(
                var, crit["crit_vals"], delta_x=delta
            )
        elif type_crit == "refine_centils":

            min_like = np.percentile(var, crit["crit_vals"][0] * 100)
            max_like = np.percentile(var, crit["crit_vals"][1] * 100)
            mean = (min_like + max_like) / 2
            delta = (max_like - min_like) * 0.7
            buff_crit = _tanh_smoothing(var, mean, delta)

        elif type_crit == None:
            raise KeyError("No criterion type defined")
        else:
            raise NotImplementedError(f"Undefined criterion type: {type_crit}")
        # tekigo_sol.add_field_to_solmesh(f"crit_raw{crit['name']}", buff_crit)
        if adapt is not None:
            buff_crit = propagate(
                buff_crit,
                gatscat,
                dilate_pass=crit.get("dilate_pass", 2),
                close_pass=crit.get("close_pass", 0),
                smooth_pass=crit.get("smooth_pass", 2),
            )

        if buff_crit is not None:
            criteria_out[crit["name"]] = buff_crit * crit["weight"]

    for key in criteria_out:
        tekigo_sol.add_field_to_solmesh(f"crit_{key}", criteria_out[key])

    if input_dict.get("patch_mask"):

        patch_list = input_dict["patch_mask"]["patch_list"]
        mask_raw = patch_mask(input_dict["mesh_path"], patch_list)
        mask = propagate(mask_raw, gatscat, dilate_pass=3, close_pass=1, smooth_pass=2)

        for crit in criteria_out.keys():
            criteria_out[crit] = apply_mask(criteria_out[crit], mask)

        tekigo_sol.add_field_to_solmesh("patches_mask", mask)

    if input_dict.get("geom_mask"):
        try:
            from pyavbp.io import mesh_utils
        except ImportError as e:
            raise ImportError(
                "You need access to pyavbp in order to use the geom mask functionality"
            )

        condition = input_dict["geom_mask"].get("condition").lower()
        condition.replace(" ", "")
        axis = condition[0]
        coords = mesh_utils.get_mesh_bulk(input_dict["mesh_path"])

        axis_dict = {"x": 0, "y": 1, "z": 2}
        coord = coords[:, axis_dict[axis]]

        geom_mask = np.where(eval(condition, {axis: coord}), 1, 0)
        tekigo_sol.add_field_to_solmesh("geom_mask", geom_mask)

        for crit in criteria_out.keys():
            criteria_out[crit] = apply_mask(criteria_out[crit], geom_mask)

    adapt_from_criteria(criteria_out, input_dict, tekigo_sol, perform_adapt=adapt)


if __name__ == "__main__":
    print(sys.argv[1])
    input_dict = read_yaml(sys.argv[1])
    print(input_dict)
    run_tekigo(input_dict)
