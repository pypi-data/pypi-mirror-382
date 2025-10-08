"""hipster module unitary tests"""

import tekigo.hipster as hip


def test_hip_process(datadir, h5same_files):
    """test of the hip process tool with interpolation"""

    hip_in = [
        "set check level 0",
        "re hd -a tekigo_solut_000000008_tgt.mesh.h5 -s tekigo_solut_000000008_tgt.sol.h5",
        "re hd -a tekigo_solut_000000008.mesh.h5",
        "in grid 1",
        "wr hd -a tekigo_solut_000000009",
        "ex",
    ]

    hip.hip_process(hip_in, datadir.join("tekigo_solut_000000008.mesh.h5"))

    assert h5same_files(
        datadir.join("tekigo_solut_000000008_tgt.sol.h5"),
        datadir.join("tekigo_solut_000000009.sol.h5"),
    )
    assert h5same_files(
        datadir.join("tekigo_solut_000000008_tgt.mesh.h5"),
        datadir.join("tekigo_solut_000000008.mesh.h5"),
    )
