"""module with tools for tekigo"""

from loguru import logger
import matplotlib.pyplot as plt
from tekigo.tkg_logging import logging_banner

# required for GatherScatter
from scipy.sparse import csr_matrix
import numpy as np


class GatherScatter:
    """
    Internal Class to hold the sparse gather matrix and do the sparse gather scatter
    Efficient implementation of unstructured mesh operations

    Originally created Feb 8th, 2018 by C. Lapeyre (lapeyre@cerfacs.fr)

    .. warning: the mesh MUST be composed of tetrahedrons

    :param connectivity: connectivity of the tetrahedral mesh (param 'tet->node' in .h5 mesh)
    :param operation_type: [**optional**] either **smooth** or **morph** (morphing operations)
    :type operation_type: string
    """

    def __init__(self, connectivity, operation_type="smooth"):
        """initialisation method of the class"""
        # Smooth related
        self._ope = operation_type
        self._elt = 4
        self._bincount = np.bincount(connectivity)
        # building gather matrix
        ncell = np.int_(connectivity.shape[0] / self._elt)
        nnode = np.max(connectivity) + 1
        # print("Ncell and Nnode = ", ncell, nnode)
        data = np.ones(connectivity.shape)
        indptr = np.arange(ncell + 1) * self._elt
        self.gather_matrix = csr_matrix(
            (data, connectivity, indptr), shape=(ncell, nnode)
        )
        # other than smooth related
        self._tet2nde = np.reshape(connectivity, (-1, 4))

    def smooth(self, field, passes=1):
        """Smooth a field using standard gather/scatter.

        The LOCAL AVERAGE is propagated

        Args:
            field (array): field compatible with mesh loaded
            passes (int): nb. of application of the operation

        Returns:
            out_field (array): adjusted field

        """
        out_field = field.copy()
        for _ in range(passes):
            out_field = self._base_morph(out_field, morphing_type="smooth")
        return out_field

    def erode(self, field, passes=1):
        """Erode a field using standard gather/scatter

        The LOCAL MINIUM is propagated

        Args:
            field (array): field compatible with mesh loaded
            passes (int): nb. of application of the operation

        Returns:
            out_field (array): adjusted field

        """
        out_field = field.copy()
        for _ in range(passes):
            out_field = self._base_morph(out_field, morphing_type="erode")
        return out_field

    def dilate(self, field, passes=1):
        """Dilate a field using standard gather/scatter

        The LOCAL MAXIMUM is propagated

        Args:
            field (array): field compatible with mesh loaded
            passes (int): nb. of application of the operation

        Returns:
            out_field (array): adjusted field

        """
        out_field = field.copy()
        for _ in range(passes):
            out_field = self._base_morph(out_field, morphing_type="dilate")
        return out_field

    def close(self, field, passes=1):
        """Close a field using standard gather/scatter

        The LOCAL MAXIMUM is propagated, then the LOCAL MINIMUM.
        Features at the resolution limit are strengthened.

        Args:
            field (array): field compatible with mesh loaded
            passes (int): nb. of application of the operation

        Returns:
            out_field (array): adjusted field

        """
        out_field = field.copy()
        out_field = self.dilate(out_field, passes=passes)
        out_field = self.erode(out_field, passes=passes)
        return out_field

    def open(self, field, passes=1):
        """Open a field using standard gather/scatter

        The LOCAL MINIMUM is propagated, then the LOCAL MAXIMUM.
        Features ar the resolution limit are cleaned out.

        Args:
            field (array): field compatible with mesh loaded
            passes (int): nb. of application of the operation

        Returns:
            out_field (array): adjusted field

        """
        out_field = field.copy()
        out_field = self.erode(out_field, passes=passes)
        out_field = self.dilate(out_field, passes=passes)
        return out_field

    def _get_scatter(self):
        """get the scattered field function

        :param self: uses the builtin parameters gather matrix and bincount if instanciated

        :returns: a method to scatter values over nodes
        """

        def scatter(cells):
            tmp = self.gather_matrix.T * cells
            return tmp / self._bincount

        return scatter

    def _base_morph(self, values_vtx, morphing_type="dilate"):
        """function to remorph values over given operation and morphing type

        :param values_vtx: input field over nodes
        :param morphing_type: [**optional**] basic morphing: either **dilate** or **erode**

        :returns: morphed field over nodes
        """
        fld_out = np.zeros(values_vtx.shape)

        if morphing_type == "smooth":
            # recovering scatter function
            scat = self._get_scatter()
            # gather scatter values : smooth
            fld_out = scat(self.gather_matrix * values_vtx) / self._elt
        else:
            # building remorph direction
            if morphing_type == "dilate":
                # computing maximum by cell (gather)
                val_cell = values_vtx[self._tet2nde].max(axis=1)
                # retrieving cell order (from min to max)
                sorted_idx = np.argsort(val_cell)
                # computing max values of each cell
                vals = val_cell[sorted_idx].repeat(4).reshape((-1, 4))
                # remorphing: broadcast the values of the cells to the nodes composing it (scatter)
                fld_out[self._tet2nde[sorted_idx, :]] = vals
            elif morphing_type == "erode":
                # computing minimum by cell
                val_cell = values_vtx[self._tet2nde].min(axis=1)
                # retrieving cell order (from max to min)
                sorted_idx = np.flip(np.argsort(val_cell))
                # computing max values of each cell
                vals = val_cell[sorted_idx].repeat(4).reshape((-1, 4))
                # remorphing: broadcast the values of the cells to the nodes composing it
                fld_out[self._tet2nde[sorted_idx, :]] = vals
            else:
                raise NotImplementedError(
                    "Morphing type must be either 'dilate' or 'erode'"
                )

        return fld_out


def approx_vol_node_from_vol_cell(vol_cell, ratio=4.5):
    """Function to approximate volume at node from cell volume

    Prefer to use the actual cell/node ratio of your initial mesh

    Arg:
        vol_cell (array):  shape(nnode), typical cell volume at nodes locations
        ratio: typical cell/nnode

    Returns:
        vol_node (array):  shape(nnode), typical node volume at nodes locations
    """
    return vol_cell * ratio


def approx_vol_cell_from_vol_node(vol_node, ratio=4.5):
    """Function to approximate cell volume from volume at node

    Prefer to use the actual cell/node ratio of your initial mesh

    Arg:
        vol_node (array):  shape(nnode), typical node volume at nodes locations
        ratio: typical cell/nnode

    Returns:
        vol_cell (array):  shape(nnode), typical cell volume at nodes locations
    """
    return vol_node / ratio


def approx_vol_node_from_edge(edge):
    r"""Function to approximate volume at node from edge size

    .. math:: V_{node} = (e^3 \frac{\sqrt(2)}{12}) * 4.5

    :param edge: edge size to be computed into a node volume equivalent

    :returns: node volume
    """
    return approx_vol_node_from_vol_cell(np.power(edge, 3) * np.sqrt(2.0) / 12.0)


def approx_edge_from_vol_node(vol_node):
    r"""Function to approximate edge size from volume at node

    .. math:: e = (\frac{V_{node}}{4.5} \frac{12}{\sqrt(2)})^{1/3}

    :param vol_node: node volume to be computed into an edge size equivalent

    :returns: edge size
    """
    return np.power(
        approx_vol_cell_from_vol_node(vol_node) * 12.0 / np.sqrt(2.0), 1.0 / 3.0
    )


def auto_hist(values, bins=10, title="title", xlabel="value"):
    """Automatic histogram of a numpy array for tekigo.

    Note that the function filter_outlier() would strip this
    field of values lower than -3std and higher than +3std
    """
    avg = np.average(values)
    std = np.std(values)
    median = np.median(values)
    hist_vals, edges = np.histogram(values, bins=bins)

    total = np.sum(hist_vals)
    xhist = [edges[0]]
    yhist = [0]
    for i, bin_ in enumerate(hist_vals):
        xhist.append(edges[i])
        yhist.append(bin_ / total)
        xhist.append(edges[i + 1])
        yhist.append(bin_ / total)
    xhist.append(edges[-1])
    yhist.append(0)

    maxbin = np.argmax(hist_vals)
    mf_value = 0.5 * (edges[maxbin] + edges[maxbin + 1])

    plt.plot(xhist, yhist)

    def _add_bar(xval, label, style, color, ypos=0.80, ingraph=False):
        leg_label = label
        if ingraph:
            plt.text(xval, ypos, label, rotation=45)
            leg_label = ""

        plt.plot([xval, xval], [0, 1], linestyle=style, color=color, label=leg_label)

    _add_bar(avg, "mean", "dashed", "black")
    for i in range(3):
        factor = i + 1
        _add_bar(
            avg + factor * std,
            "+" + str(factor) + "std",
            "dotted",
            "black",
            ingraph=True,
        )
        _add_bar(
            avg - factor * std,
            "-" + str(factor) + "std",
            "dotted",
            "black",
            ingraph=True,
        )

    _add_bar(median, "median", "dashed", "blue", ypos=0.70)
    _add_bar(mf_value, "most_frequent", "dashed", "green", ypos=0.90)
    plt.legend()
    plt.title(title)
    plt.xlabel(xlabel)
    plt.plot()
    plt.show()


def filter_outliers(data, n=3.0):
    """Remove outliers using stantard deviation

    Remove outlier data defined as N (defaiut 3) times the distance of the standard deviation
    with reference to the average value.
    Not suited to all fields at all!!!

    ..warning:
        standard deviation is well defined for a gaussian distribution,
        still stand for a unimodeal distribution
        but is garbage for more comple distribution.
        Foe example, a temperature fiel is combustion is
        a bimodal distribution (hot gases and cold gases)
        Its standard deviation is not relevant.
        Same for HR, etc, etc.


    Args:
        values (array): shape (n), values, gaussian-like, or unimodal distibution

    """
    filtered_data = np.copy(data)

    logger.info(f" - filtering outliers using {n} std_dev")

    hi_limit = np.mean(filtered_data) + n * np.std(filtered_data)
    low_limit = np.mean(filtered_data) - n * np.std(filtered_data)

    filtered_data = np.clip(filtered_data, low_limit, hi_limit)

    outliers_cnt = np.sum(filtered_data != data)
    logger.info(
        f" - Ignoring {outliers_cnt} outliers out of {np.size(data)} ({outliers_cnt/np.size(data)})"
    )
    return filtered_data


def normalize_metric(values, expnt=10.0, floor=0.3):
    """A typical normalization function

    This normalization occur in many adaptation recipes, but it is not universal.
    Read carefully what its does, in some cases this could be totally stupid to, use.

    Args:
        values (array): shape (n), any value.
        expnt (float) : >0 exponent applied on the normalized values
        floor (float): [0-1[ floor of the final data.

    Returns:
        metric (array): the normalized metric
    """
    logging_banner(" - Normalizing metric based on min. (0) and max. values (1)")
    logger.info(f" - expnt : {expnt}")
    logger.info(f" - floor : {floor}")

    metric = np.copy(values)
    metric = filter_outliers(values)
    metric[:] = 1 - (metric - np.min(metric)) / (np.max(metric) - np.min(metric))
    metric[:] = metric[:] ** expnt
    metric = metric * (1 - floor) + floor
    return metric


# ------------------------------------#
# ------------------------------------#

# def approx_gradmag(self, field, edge):
#     """method to compute approximative maximum gradient on each node

#     :param field: field to be morphed (node centered)
#     :param edge: edges approximation (use the approx_edge_from_vol_node tool if needed)

#     :returns: maximum gradient field over nodes
#     """
#     cells = self._tet2nde.repeat(4, axis=1).reshape((-1, 4, 4))
#     maxima = np.divide(
#         np.abs(field[cells.transpose((0, 2, 1))] - field[cells]), edge[cells]
#     ).max(axis=1)
#     sorted_idx = np.argsort(maxima - field[self._tet2nde], 0)
#     field[
#         np.take_along_axis(self._tet2nde, sorted_idx, axis=0)
#     ] = np.take_along_axis(maxima, sorted_idx, axis=0)

#     return field

# The following set of functions have been ported from hdfdict 0.1.1
# taking into account the changes (unpack dataset) present in hdfdict 0.3.1
# which ensures compatability of tekigo with python 3.6

# TYPEID = "_type_"


# def _check_hdf_file(hdf):
#     """Returns h5py File if hdf is string (needs to be a path)."""
#     if isinstance(hdf, str):
#         hdf = h5py.File(hdf)
#     return hdf


# def unpack_dataset(item):
#     """Reconstruct a hdfdict dataset.
#     Only some special unpacking for yaml and datetime types.

#     Parameters
#     ----------
#     item : h5py.Dataset

#     Returns
#     -------
#     value : Unpacked Data

#     """
#     value = item[()]
#     if TYPEID in item.attrs:
#         if item.attrs[TYPEID].astype(str) == "datetime":
#             if hasattr(value, "__iter__"):
#                 value = [datetime.fromtimestamp(ts) for ts in value]
#             else:
#                 value = datetime.fromtimestamp(value)

#         if item.attrs[TYPEID].astype(str) == "yaml":
#             value = yaml.safe_load(value.decode())
#     return value


# def load_local(hdf):
#     """Returns a dictionary containing the
#     groups as keys and the datasets as values
#     from given hdf file.

#     NOTE: This is a copy paste of load() from hdfdict 0.1.1 with
#             addition of the unpack_dataset function call.

#     Parameters
#     ----------
#     hdf : string (path to file) or `h5py.File()` or `h5py.Group()`

#     Returns
#     -------
#     d : dict
#         The dictionary containing all groupnames as keys and
#         datasets as values.
#     """
#     hdf = _check_hdf_file(hdf)
#     d = {}

#     def _recurse(h, d):
#         for k, v in h.items():
#             # print(type(v))
#             # print(isinstance(v, h5py.Group))
#             # print(isinstance(v, h5py.Dataset))
#             if isinstance(v, h5py.Group):
#                 d[k] = {}
#                 d[k] = _recurse(v, d[k])
#             elif isinstance(v, h5py.Dataset):
#                 d[k] = unpack_dataset(v)
#                 # d[k] = v.value  -> original code
#         return d

#     return _recurse(hdf, d)
