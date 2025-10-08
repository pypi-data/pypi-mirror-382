"""module storing the tekigo specific logging functions"""

import os, sys
import logging
from loguru import logger


def logging_start(out_dir):
    f_log = os.path.join(out_dir, f"tekigo_{os.getpid()}.log")
    logging.basicConfig(
        level=logging.INFO,
        # format="%(levelname)s - %(message)s",
        format="%(message)s",
        handlers=[
            logging.FileHandler(f_log, mode="w"),  # set mode to "a" to append
            logging.StreamHandler(sys.stdout),
        ],
    )


def logging_banner(title):

    logger.info(f"\n\n======= {title} =========\n\n")


def logging_pyhip(
    hausdorff_distance,
    frozen_patch_list,
    max_spacing_gradient,
    periodic_adaptation,
):
    """log PyHIP parameters"""
    logger.info(f"   Hip specific arguments")
    logger.info(f"   max_spacing_gradient : {max_spacing_gradient}")
    if hausdorff_distance is not None:
        logger.info(f"   hausdorff_distance : {hausdorff_distance}")
    else:
        logger.info(f"   hausdorff_distance : (auto)")
    if frozen_patch_list:
        plist = "\n - ".join(frozen_patch_list)
        logger.info(f"   frozen_patch_list : \n - {plist}")
    if periodic_adaptation:
        logger.info(f"   periodic adaptation enabled")
    else:
        logger.info(f"   periodic adaptation disabled\n")


def logging_mesh(name, nnode, ncell, h_min):
    logger.info(f"   {name}:")
    logger.info(f"   Number of nodes     {nnode}")
    logger.info(f"   Number of cells     {ncell}")
    logger.info(f"   Minimal edge size   {h_min:1.5e}\n")


def logging_field(name, field):
    logger.info(f"   Field {name} : {field.min():1.4f}, {field.max():2.4f}\n")
