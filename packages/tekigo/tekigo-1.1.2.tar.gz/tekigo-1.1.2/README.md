![splash](https://gitlab.com/cerfacs/tekigo/-/raw/master/tekigo_splashscreen.png)

# Tékigô

## About

Tékigô is a python helper tool for static mesh adaptation.
It eases the creation of metrics, and store them in a file.
The online documentation is available on [the internal Cerfacs forge](http://opentea.pg.cerfacs.fr/tekigo/) (Credentials needed). Soon the package will be updated on pypi with documentation on readthedocs.

There is a built-in adaptation step done with [HIP](http://www.cerfacs.fr/avbp7x/hip.php) mesh handler  developed at CERFACS. It is suited for unstructured grids and particularly useful for CFD. 

**Note : for now, Tekigo handle AVBP mesh and solution format. However contact us for extendion to others format, it should not be a big deal...**

---

## Installation

please install first pyHIP :

``` 
pip install pyhip
```

While we a refurbishing this new version 1.0, it will not be released on PyPI before we reach a stable version.
Therefore, please, use tekigo from the sources:

```
git clone git@gitlab.com:cerfacs/tekigo.git
```
followed in the  `tekigo/` parent directory by: 

```
 python setup.py install
```

If possible add `pyavbp`to your environement. 
This is not compulsory, but needed to create the `xmf`file from you ionitial mesh and solution.
Learn more about COOP virtual environements in this [blog post on COOP venvs](https://cerfacs.fr/coop/coop-venvs)


## Basic usage:

Tekigo is used via python scripts, to do the following steps

1. create a `TekigoSolution`, i.e. a mesh + solution with some additional fields 
(coordinates , volume at node).
1. Load from this `TekigoSolution` some Quantities of Interests.
1. Build a metric from these Quantities of Interests, using `numpy`formalism -and if neededsome tekigo utilities-.
1. Evaluate the metric, i.e. forecast the future mesh : how many cells are we going to get?, what the fields will look like in the end?
1. If asked, perform a HIP/MMG adaptation

The script reads:


```python
import numpy as np
from tekigo import (TekigoSolution, adaptation_pyhip)

tekigo_sol = TekigoSolution(
    mesh='../../GILGAMESH/trapvtx/trappedvtx.mesh.h5',
    solution='combu.init.h5',
    out_dir='./Results')


x_coor = tekigo_sol.load_qoi('/Mesh/coord_x')
metric_field = np.where(x_coor<0.1,1,0.7)

tekigo_sol.evaluate_metric(metric_field)

adaptation_pyhip(tekigo_sol, edge_low=1.e-3)
```

See tutorials for more in-depth description of scripts.
No magic exxecution for the moment, create your python script  and run it with 

```python
python my_tekigo_script.py
```
---


## Performances

Tekigo's  `adaptation_pyhip()` through HIP/MMG, is sequential : **do not aim for final meshes above 150M Tetrahedrons.**. Around 200 MCells, you will reach the limits of a sequential mesh adapter.
For larger cases, just use tekigo without the `adaptation_pyhip()` step, pass the solution to **TreeAdapt**. For the record,  **TreeAdapt** needs the final edge lenght (field `target_edge`), not the metric(field `metric`).

## Acknowledgements

Tekigo is the result of many discussions and developments of different contributors within the COOP team of CERFACS.

Tekigo is a service created in the [COEC Center Of Excellence](https://coec-project.eu/), funded by the European community. 

![logo](https://coec-project.eu/wp-content/uploads/2020/12/logo.png)
