"""Module for object TekigoSolution"""

import os
import h5py
import shutil
import filecmp

from loguru import logger

from tekigo.base import (
    get_mesh_infos,
    update_h5_file,
    metric_forecast,
)

from tekigo.tkg_logging import (
    logging_start,
    logging_mesh,
    logging_field,
    logging_banner,
)

from tekigo.tools import approx_edge_from_vol_node, GatherScatter


class TekigoSolution:
    """Object storing a mesh and its INSTANTANEOUS solution

    This is whe mesh and solution used as the basis for an adaptation.
    Many adaptations strategies exists, and somes do not need averaged CFD fields,
    But all need an instantaneous field to restart with the new mesh...

    ..note:
        To load average fields into your tekigo solution, use:
        `TekigoSolution.include_average(avg_sol, avg_field)`

    Args:

        mesh (string): path to an AVBP mesh
        solution (string) :  path to an AVBP instantaneous solution
        additionals (bool) : include additionals if solution is provided
        out_dir (string) : path to a folder where results will be stored
    """

    def __init__(
        self,
        mesh,
        solution=None,
        additionals=True,
        out_dir="./Results",
    ):
        # pylint: disable=too-many-arguments

        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        path = os.path.abspath(out_dir)

        logging_start(path)
        logging_banner("Creating TekigoSolution handler...")

        self.out_dir = path
        self.final_prefix = os.path.join(path, "tekigo_adapt")
        self.init_mesh = os.path.join(path, "tekigo_init.mesh.h5")
        self.init_sol = os.path.join(path, "tekigo_init.sol.h5")
        self.init_xmf = os.path.join(path, "tekigo_init.sol.xmf")

        if os.path.exists(self.init_mesh):
            if filecmp.cmp(self.init_mesh, mesh):
                logger.info("Mesh is the same, skipping copy...")
            else:
                shutil.copy(mesh, self.init_mesh)
        else:
            shutil.copy(mesh, self.init_mesh)

        if os.path.exists(self.init_sol):
            os.remove(self.init_sol)

        self._include_mesh_data()
        if solution is not None:
            self._include_instantaneous(solution, additionals=additionals)

        hmin, ncell, vnode = get_mesh_infos(self.init_mesh)
        nnode = vnode.shape[0]
        self.mesh_infos = {
            "nnode": nnode,
            "hmin": hmin,
            "ncell": ncell,
            "vol_node": vnode,
        }
        logging_mesh(
            "Inital mesh",
            self.mesh_infos["nnode"],
            self.mesh_infos["ncell"],
            self.mesh_infos["hmin"],
        )
        self._qoi_list()

    # Most used -----------------

    def make_restartable(self, out_dir: str, groups: list = []):
        """
        Delete unnecessary group(s) within adapted solution.
        Otherwise, if AVBP detects 'AVERAGE' fields within initial solution, it does not start simulation.

        note : At least, 'Average' field will be suppressed.

        Args:
            out_dir (str) : Path in which adapted mesh are dumped.
                            Used to find the interpolated solution on the new mesh to remove average field
            groups (list) : Optionnal parameter used to suppress additionnal groups within 'tekigo_adapt.sol.h5'.
        """
        tekigo_sol = out_dir + "/tekigo_adapt.sol.h5"

        groups_to_del = ["Average"]

        if groups:
            for group in groups:
                if group not in groups_to_del:
                    groups_to_del.append(group)
        logger.info(
            f"To help AVBP restart, following group(s) will be deleted from h5 file {tekigo_sol} : {groups_to_del}"
        )

        with h5py.File(out_dir + "/tekigo_adapt.sol.h5", "r+") as f:
            for group in groups_to_del:
                del f[group]

    def add_fields_from_solution(self, sol_file, group, fields, group_suffix=None):
        """Include average fields to initial solution

        Args:
            sol_file: str, path to average solution
            group (str): str, name of the group
            fields (list): list of str, paths of Hdf datasets
            group_suffix(str): suffix added to the group in the targed solution


        Note:
            if a group_suffix is provided, the target group will be group+group_suffix
            this option is to load fields with the same name from different solutions
        """

        if isinstance(fields, str):
            fields = [fields]

        if group_suffix is None:
            suffix = ""
        else:
            suffix = "_" + group_suffix

        d_vars = {}
        address_avails = ""
        logger.info(f" The following New Quantities of Interest can be loaded: ")
        with h5py.File(sol_file, "r") as fin:
            for field in fields:
                d_vars[field] = fin[f"/{group}/{field}"][()]
                address_avails += " - " + f"/{group}/{field}" + "\n"
        logger.info("\n" + address_avails)

        update_h5_file(
            self.init_sol,
            parent_group=group + suffix,
            data_dict=d_vars,
        )
        self._refresh_xmf()

    def load_qoi(self, address):
        """Load a quantity of interest from solution

        Args:
            address : str, paths of Hdf dataset
        """
        logger.info(f"Loading Quantity of interest {address}")

        with h5py.File(self.init_sol, "r") as fin:
            qoi = fin[address][()]
        logging_field(address, qoi)
        return qoi

    def evaluate_metric(self, custom_metric, update_tkgsol=True):
        """
        Evaluate effects of metric prior to adaptation

        - results of evaluation are printed to log
        - If update_tkgsol is true ,Metrics and target edge
            are stored in solution and xmf file is refreshed


        Args :
            custom_metric (array) : metric of shape (nnode) : target_edge/init_edge

        Returns :
            e_nnode (int) : estimated nb. of nodes
            e_ncell (int) : estimated nb. of cells
            e_edge (float) : estimated minimal edge length
        """

        logging_banner("Evaluate metric w.r. to solution")
        logging_field("Custom metric", custom_metric)
        e_nnode, e_edge = metric_forecast(custom_metric, self.init_mesh)
        e_ncell = int(self.mesh_infos["ncell"] * e_nnode / self.mesh_infos["nnode"])
        logging_mesh("Forecast mesh", e_nnode, e_ncell, e_edge.min())

        if update_tkgsol:
            metric = {
                "target_edge": e_edge,
                "metric": custom_metric,
            }
            update_h5_file(
                self.init_sol,
                parent_group="Adapt",
                data_dict=metric,
            )
            self._refresh_xmf()
        return e_nnode, e_ncell, e_edge

    def add_field_to_solmesh(self, name, field, group="Adapt"):
        """Add a numpy arry field to the Hdf5 sol file"""
        logger.info(f"   add field {group}/{name} to init solmesh : {self.init_sol}")
        update_h5_file(
            self.init_sol,
            parent_group=group,
            data_dict={name: field},
        )
        self._refresh_xmf()

    def gatherscatter(self):
        """Returns a gathher Sactter object to make operations on fields"""
        with h5py.File(self.init_mesh, "r") as fin:
            connect_tet = fin["/Connectivity/tet->node"][()].astype("int64")
        # fortran to c indexing
        connect_tet -= 1
        return GatherScatter(connect_tet, "smooth")

    # Private ---- Never seen by users
    def _qoi_list(self):
        """List all potential quantity of interest loadable"""
        with h5py.File(self.init_sol, "r") as fin:
            list_addr = []
            for group in fin.keys():
                if group not in ["Parameters"]:
                    for key in fin[group].keys():
                        list_addr.append(f"/{group}/{key}")

            logger.info(f" The following Quantities of Interest can be loaded: ")
            address_avails = " - " + "\n - ".join(list_addr) + "\n"
            logger.info(address_avails)

    def _include_mesh_data(self):
        """Include average fields to initial solution"""
        with h5py.File(self.init_mesh, "r") as fin:
            vol_node = fin["/VertexData/volume"][()]
            mesh_data = {
                "coord_x": fin["/Coordinates/x"][()],
                "coord_y": fin["/Coordinates/y"][()],
                "coord_z": fin["/Coordinates/z"][()],
                "volume": vol_node,
                "init_edge": approx_edge_from_vol_node(vol_node),
            }
            update_h5_file(
                self.init_sol,
                parent_group="Mesh",
                data_dict=mesh_data,
            )
            self._refresh_xmf()

    def _refresh_xmf(self):
        """Refresh xmf for initial sol"""
        try:
            from pyavbp.tools.visu import visu_sol_from_files
        except ImportError:
            logger.warning("Package pyavbp not installed, skipping .xmf generation.\n")
            return None

        sol_xmf = visu_sol_from_files(self.init_mesh, self.init_sol)
        with open(self.init_xmf, "w") as fout:
            fout.write(sol_xmf)

    def _include_instantaneous(self, inst_sol_file, additionals=True):
        """Include average fields to initial solution

        Args:
           inst_sol_file (str): path to average solution
           additionals (bool): include additionals
        """

        groups_to_copy = ["GaseousPhase", "RhoSpecies", "Parameters", "FictiveSpecies"]
        if additionals:
            groups_to_copy.append("Additionals")

        with h5py.File(inst_sol_file, "r") as fin:
            for gname in fin.keys():
                if gname in groups_to_copy:
                    holder = {}
                    for dsname in fin[f"/{gname}/"].keys():
                        holder[dsname] = fin[f"/{gname}/{dsname}"][()]
                    update_h5_file(
                        self.init_sol,
                        parent_group=gname,
                        data_dict=holder,
                    )
        self._refresh_xmf()


# def include_average(self, ave_sol_file, ave_fields):
#     """Include average fields to initial solution

#     Args:
#        ave_sol_file: str, path to average solution
#        ave_fields: list of str, paths of Hdf datasets"""

#     avg_vars = {}
#     with h5py.File(ave_sol_file, "r") as fin:
#         for field in ave_fields:
#             avg_vars[field] = fin["/Average/" + field][()]
#     update_h5_file(
#         self.init_sol,
#         parent_group="Average",
#         data_dict=avg_vars,
#     )
#     self._refresh_xmf()
