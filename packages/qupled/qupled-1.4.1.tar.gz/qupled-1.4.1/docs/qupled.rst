The package
===========

**qupled** is a hybrid Python/C++ package designed to simulate and analyze dielectric response 
schemes, both classical and quantum. **Python** orchestrates the workflow: setting up simulations, 
managing input/output, and storing results in an SQLite database. **C++** performs the heavy 
numerical computations, accessed via the 
`Boost.Python <https://www.boost.org/doc/libs/1_80_0/libs/python/doc/html/index.html>`_ bindings.

To run a simulation, users configure input parameters through Python classes 
(e.g., :obj:`qupled.hf.Input`) and launch the computation using the corresponding solver 
class (e.g., :obj:`qupled.hf.HF`). Results are returned in dedicated result objects 
(e.g., :obj:`qupled.hf.Result`) and automatically written to an SQLite database for 
post-processing or analysis.

The database is implemented in standard SQLite format and can be accessed using any 
compatible external tool (e.g., `sqlite3`, DB Browser for SQLite). For convenience, 
the package provides a dedicated Python interface in the :obj:`qupled.output.Database` 
class, which includes helper methods to query, inspect, and extract stored simulation 
data programmatically.

The sections below describe the supported schemes in more detail, including their 
respective input, solver, and result classes.


Classic schemes
---------------

HF scheme
~~~~~~~~~~

The :obj:`qupled.hf` module is used to setup and perform all the necessary calculations
for the solution of the `Hartree-Fock approximation <https://arxiv.org/abs/2411.04904>`_.
The solution parameters are specified with a dedicated class called :obj:`qupled.hf.Input`.
After the solution is completed the results are stored in an object :obj:`qupled.hf.Result` 
and written to the output database.

.. autoclass:: qupled.hf.Solver
    :members:

.. autoclass:: qupled.hf.Input
    :members:
    :exclude-members: to_native

.. autoclass:: qupled.hf.Result
    :members:
    :exclude-members: compute_rdf, from_native

Rpa scheme
~~~~~~~~~~

The :obj:`qupled.rpa` module is used to setup and perform all the necessary calculations
for the solution of the `Random-Phase Approximation <https://journals.aps.org/pr/abstract/10.1103/PhysRev.92.609>`_.
The solution parameters are specified with a dedicated class called :obj:`qupled.rpa.Input`.
After the solution is completed the results are stored in an object :obj:`qupled.hf.Result` 
and written to the output database.

.. autoclass:: qupled.rpa.Solver
    :show-inheritance:
    :members:

.. autoclass:: qupled.rpa.Input	       
    :show-inheritance:
    :members:

Stls scheme
~~~~~~~~~~~		      

The :obj:`qupled.stls` module is used to setup and perform all the necessary calculations
for the solution of the `Stls scheme <https://journals.jps.jp/doi/abs/10.1143/JPSJ.55.2278>`_.
The solution parameters are specified with a dedicated class called :obj:`qupled.stls.Input`.
After the solution is completed the results are stored in an object :obj:`qupled.stls.Result` 
and written to the output database.

.. autoclass:: qupled.stls.Solver
    :show-inheritance:
    :members:

.. autoclass:: qupled.stls.Input	       
    :show-inheritance:
    :members:
      
.. autoclass:: qupled.stls.Result
    :show-inheritance:
    :members:

.. autoclass:: qupled.stls.Guess
    :members:
    :exclude-members: to_native

Stls-IET schemes
~~~~~~~~~~~~~~~~	      

The :obj:`qupled.stlsiet` module is used to setup and perform all the necessary calculations
for the solution of the `Stls-IET schemes <https://journals.jps.jp/doi/abs/10.1143/JPSJ.55.2278>`_.
The solution parameters are specified with a dedicated class called :obj:`qupled.stlsiet.Input`.
After the solution is completed the results are stored in an object :obj:`qupled.stlsiet.Result` 
and written to the output database.

.. autoclass:: qupled.stlsiet.Solver
    :show-inheritance:
    :members:

.. autoclass:: qupled.stlsiet.Input	       
    :show-inheritance:
    :members:
      
.. autoclass:: qupled.stlsiet.Result
    :show-inheritance:
    :members:

.. autoclass:: qupled.stlsiet.Guess
    :members:
    :exclude-members: to_native

VSStls scheme
~~~~~~~~~~~~~

The :obj:`qupled.vsstls` module is used to setup and perform all the necessary calculations
for the solution of the `VSStls scheme <https://journals.aps.org/prb/abstract/10.1103/PhysRevB.88.115123>`_.
The solution parameters are specified with a dedicated class called :obj:`qupled.vsstls.Input`.
After the solution is completed the results are stored in an object :obj:`qupled.vsstls.Result` 
and written to the output database.

.. autoclass:: qupled.vsstls.Solver
    :show-inheritance:
    :members:
    :exclude-members: get_free_energy_integrand

.. autoclass:: qupled.vsstls.Input	       
    :show-inheritance:
    :members:
      
.. autoclass:: qupled.vsstls.Result
    :show-inheritance:
    :members:

.. autoclass:: qupled.vsstls.FreeEnergyIntegrand
    :members:
    :exclude-members: to_native

Hybrid schemes
--------------

ESA scheme
~~~~~~~~~~

The :obj:`qupled.esa` module is used to setup and perform all the necessary calculations
for the solution of the `Effective Static Approximation <https://journals.aps.org/pr/abstract/10.1103/PhysRev.92.609>`_.
The solution parameters are specified with a dedicated class called :obj:`qupled.esa.Input`.
After the solution is completed the results are stored in an object :obj:`qupled.hf.Result` 
and written to the output database.

.. autoclass:: qupled.esa.Solver
    :show-inheritance:
    :members:

.. autoclass:: qupled.esa.Input	       
    :show-inheritance:
    :members:

Quantum schemes
---------------

Qstls scheme
~~~~~~~~~~~~

The :obj:`qupled.qstls` module is used to setup and perform all the necessary calculations
for the solution of the `Qstls scheme <https://journals.aps.org/prb/abstract/10.1103/PhysRevB.48.2037>`_.
TThe solution parameters are specified with a dedicated class called :obj:`qupled.qstls.Input`.
After the solution is completed the results are stored in an object :obj:`qupled.qstls.Result` 
and written to the output database.

.. autoclass:: qupled.qstls.Solver
    :show-inheritance:
    :members:
    :exclude-members: find_fixed_adr_in_database

.. autoclass:: qupled.qstls.Input	       
    :show-inheritance:
    :members:

Qstls-IET scheme
~~~~~~~~~~~~~~~~

The :obj:`qupled.qstlsiet` module is used to setup and perform all the necessary calculations
for the solution of the `Qstls-IET schemes <https://pubs.aip.org/aip/jcp/article/158/14/141102/
2877795/Quantum-version-of-the-integral-equation-theory>`_.
The solution parameters are specified with a dedicated class called :obj:`qupled.qstlsiet.Input`.
After the solution is completed the results are stored in an object :obj:`qupled.qstlsiet.Result` 
and written to the output database.

.. autoclass:: qupled.qstlsiet.Solver
    :show-inheritance:
    :members:
    :exclude-members: find_fixed_adr_in_database

.. autoclass:: qupled.qstlsiet.Input	       
    :show-inheritance:
    :members:

QVSStls scheme
~~~~~~~~~~~~~~~~

The :obj:`qupled.quantum.QVSStls` class is used to setup and perform all the necessary calculations
for the solution of the QVStls schemes. The solution parameters are specified with a dedicated class 
called :obj:`qupled.qvsstls.Input`. After the solution is completed the results are stored in an 
object :obj:`qupled.qvsstls.Result` and written to the output database.

.. autoclass:: qupled.qvsstls.Solver
    :show-inheritance:
    :members:
    :exclude-members: get_free_energy_integrand

.. autoclass:: qupled.qvsstls.Input	       
    :show-inheritance:
    :members:

Output database
---------------

The output generated by qupled is stored in an SQL database named `qupled.db`, which is created in 
the directory where qupled is executed. If the database doesn't already exist, it will be created 
automatically; otherwise, new results are added to the existing database. The :obj:`qupled.output.DataBase`
class provides functionality for accessing the data stored in the database.

.. autoclass:: qupled.output.DataBase
    :members:

Dimenions
---------

.. autoclass:: qupled.dimension.Dimension
    :members: