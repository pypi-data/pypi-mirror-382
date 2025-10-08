"""Toward an API for h!p"""

import os
import subprocess
from loguru import logger
from pyhip.hipster import HIP_CMD


def hip_adapt(
    mesh_file,
    sol_file,
    out_prefix,
    max_spacing_gradient,
    hausdorff_distance,
    frozen_patch_list,
    edge_low=None,
    edge_high=None,
    metric_field="metric",
    periodic_adaptation=True,
    vol_min=None,
):  # pylint: disable = too-many-arguments
    """Generates hip.in file from template

    :param mesh_file: full path to hip input file
    :type mesh_file: string
    :param max_spacing_gradient: maximum spacing gradient
    :type max_spacing_gradient: number, *optional*
    :param hausdorff_distance: target hausdorff distance
    :type hausdorff_distance: number, *optional*
    :param frozen_patch_list: list of patches to freeze during refinement
    :type frozen_patch_list: list of integers, *optional*
    :param *optional* sol_file: solution file, if None a solution
                           file is created
    :param dry_run: if True no refinement is done
    :type dry_run: boolean, *optional*
    :param metric_field: metric index parameter
    :type metric_field: string, *optional*
    :param periodic_adaptation: if True periodic adaptation is activated in hip
    :type periodic_adaptation: boolean, *optional*

    :returns: output of hip
    """
    mesh_f = os.path.basename(mesh_file)
    sol_f = os.path.basename(sol_file)
    out_f = os.path.basename(out_prefix)

    # Adaptation limiters
    cmd_perio_adapt = ""
    if not periodic_adaptation:
        cmd_perio_adapt = "se ad-per 0"

    cmd_frozen_patch_list = "\n"
    if frozen_patch_list is not None:
        bc_string = [
            f'se bc-mark "{str(frozen_patch_list)}" 1'
            for frozen_patch_list in frozen_patch_list
        ]
        cmd_frozen_patch_list += "\n".join(bc_string) + "\n"

    # MMG controls
    cmd_mmg = f"mm isoVar -v {metric_field} -g {max_spacing_gradient} "
    if hausdorff_distance is not None:
        cmd_mmg += f" -h {hausdorff_distance}"
    if edge_low is not None:
        cmd_mmg += f" -l {edge_low}"
    if edge_high is not None:
        cmd_mmg += f" -u {edge_high}"

    cmd_vol_clip = "\n"
    if vol_min:
        cmd_vol_clip = f"mg -v {vol_min}"

    # Script
    cmd_lines = [
        "set check level 0",
        f"re hd -a {mesh_f}  -s {sol_f}",
        cmd_perio_adapt,
        "var",
        cmd_frozen_patch_list,
        cmd_mmg,
        cmd_vol_clip,
        f"wr hd {out_f}",
        "ex",
    ]
    return cmd_lines


def hip_refresh(mesh_file: str) -> list:
    """
    Add the following information under 'Parameters' group within a copy of your mesh :
    - gridName
    - h_max
    - h_min
    - hipversion
    - md5_signature
    - r_max r_min
    - version
    - vol_domain
    - vol_elem_max
    - vol_elem_min
    - x_max
    - x_min

    1. Read previous information within your mesh.
    2. Write them into a copy of your mesh called after your mesh + '_bis' string

    :param mesh_file: path of the mesh you want to add informations into

    :return: list of commands to execute by Hip
    """
    mesh_f = os.path.basename(mesh_file)
    copy_of_mesh = mesh_f.split(".")[0] + "_bis"
    cmd_lines = [f"re hd {mesh_f}", f"wr hd {copy_of_mesh}", "ex"]
    return cmd_lines


# TODO : why this mesh file???
def hip_process(hip_cmd_lines, mesh_file):
    """runner for hipster, uses hip in subprocess, takes command lines, runs it and returns output

    :param hip_cmd_lines: hip script (with newlines) to be runned
    :param mesh_file: mesh (and its directory !) to be read by hip.
    """
    mesh_dir = os.path.abspath(os.path.dirname(mesh_file))
    hip_file = os.path.join(mesh_dir, "hip.in")

    with open(hip_file, "w") as fout:
        fout.write("\n".join(hip_cmd_lines))

    cmd = [HIP_CMD, "%s" % hip_file]
    for stdout_line in popen_execute(cmd, mesh_dir):
        logger.info(stdout_line.rstrip("\n"))

    return "Done"


def popen_execute(cmd, mesh_dir):
    """Execute comand with contant feedback"""
    popen = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, cwd=mesh_dir, universal_newlines=True
    )
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)
