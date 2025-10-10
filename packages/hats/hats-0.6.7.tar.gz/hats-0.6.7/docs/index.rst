HATS - Hierarchical Adaptive Tiling Scheme
========================================================================================

HATS is a directory structure and metadata for spatially arranging large catalog survey data. 
This was originally motivated by a desire to perform spatial cross-matching between surveys 
at large scale, but is applicable to a range of spatial analysis and algorithms.

We use healpix (`Hierarchical Equal Area isoLatitude Pixelization <https://healpix.jpl.nasa.gov/>`__)
for the spherical pixelation, and adaptively size the partitions based on the number of objects.
Each partition will have roughly the same number of objects, instead of dividing into equal area. 
Because each partition is roughly the same size on disk, we can expect reasonable performance of 
parallel operations on each partition.

We use parquet as the underlying storage format, as it provides efficient storage and retrieval 
of tabular data.

The ``hats`` python package provides basic access to a catalog's metadata, and shared functionality
for interacting with the healpix space. This allows for multiple libraries to implement parallel 
operations on top of these utilities. Some known extensions:

* `LSDB <https://lsdb.readthedocs.io/>`__ - Large Survey Database - A framework for scalable 
  spatial analysis using ``dask`` for job scheduling and execution.
* `hats-import <https://hats-import.readthedocs.io/>`__ - map reduce pipelines for converting
  large or custom catalogs into HATS format.

.. toctree::
   :maxdepth: 1
   :caption: Using HATS

   Getting Started <getting_started>
   Directory Scheme <guide/directory_scheme>
   Notebooks <notebooks>
   API Reference <autoapi/index>

.. toctree::
   :maxdepth: 1
   :caption: Project

   About & Citation <citation>
   Contribution Guide <guide/contributing>


Getting Started
-------------------------------------------------------------------------------

For the most part, we recommend accessing and processing HATS data using the `LSDB package
<https://github.com/astronomy-commons/lsdb>`__ framework. LSDB provides a variety of utility
functions as well as a lazy, distributed execution framework using Dask. However if you are are
interested in using just the HATS package, you can find installation instructions at the 
:doc:`getting started page</getting_started>`.

Acknowledgements
-------------------------------------------------------------------------------

This project is supported by Schmidt Sciences.

This project is based upon work supported by the National Science Foundation
under Grant No. AST-2003196.

This project acknowledges support from the DIRAC Institute in the Department of 
Astronomy at the University of Washington. The DIRAC Institute is supported 
through generous gifts from the Charles and Lisa Simonyi Fund for Arts and 
Sciences, and the Washington Research Foundation.