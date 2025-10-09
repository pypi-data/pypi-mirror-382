.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
    :alt: License: MIT
    :target: LICENSE

.. image:: https://img.shields.io/pypi/pyversions/sir3stoolkit.svg
    :alt: Supported Python versions
    :target: https://pypi.org/project/sir3stoolkit

.. image:: https://img.shields.io/pypi/v/sir3stoolkit.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/sir3stoolkit/

.. image:: https://img.shields.io/badge/docs-latest-brightgreen.svg?logo=readthedocs&logoColor=white
   :target: https://3sconsult.github.io/sir3stoolkit/
   :alt: docs

----

SIR 3S Toolkit
==============

**SIR 3S Toolkit** is a Python package developed by 3S Consult that provides a programming interface for SIR 3S - 
a software for the simulation, analysis and optimization of flow processes in gas/water/heat supply networks, 
plants, pipelines and caverns. 

At its core, the package wraps basic functionality of SIR 3S, offering a low-level access to the creation, modification and simulation of SIR 3S models.

On top of this core, higher-level functionality is provided, enabling more powerful and intuitive interactions with SIR 3S models. 

This layered architecture of the SIR 3S Toolkit ensures both flexibility and extensibility for advanced applications.

.. image:: https://raw.githubusercontent.com/3SConsult/PT3S/master/sphinx_docs/_static/Sir3S_Splash.jpg
   :target: https://www.3sconsult.de/software/sir-3s/
   :width: 20%
   :alt: Sir3S Splash

Note: This package is a client toolkit for the proprietary SIR 3S software. A valid license for SIR 3S is required to use this package in production.

Features
--------

- **Create** new SIR 3S models
- **Modify** existing SIR 3S models
- **Simulate** SIR 3S models
- **Read** data and simulation results from SIR 3S models

Documentation
-------------
For detailed documentation, visit `SIR 3S Toolkit Documentation <https://3sconsult.github.io/sir3stoolkit/>`_.

PyPI
----
You can find the SIR 3S Toolkit package on `PyPI <https://pypi.org/project/sir3stoolkit/>`_.

Installation
------------

To install the SIR 3S Toolkit, use pip:

   .. code-block:: bash

      pip install sir3stoolkit

Quick Start
-----------

.. code-block:: python

   from sir3stoolkit.core import wrapper

   SIR3S_SIRGRAF_DIR = r"C:\SIR3S\SirGraf-90-15-00-12_Quebec_x64"
   wrapper.Initialize_Toolkit(SIR3S_SIRGRAF_DIR)

   model = wrapper.SIR3S_Model()
   model.OpenModel(dbName=r"example_model.db3", 
                   providerType=model.ProviderTypes.SQLite, 
                   Mid="M-1-0-1", 
                   saveCurrentlyOpenModel=False, 
                   namedInstance="", 
                   userID="", 
                   password="")

   model.ExecCalculation(True)

Contact
-------
If you'd like to report a bug or suggest an improvement for the SIR 3S Toolkit, please `open a new issue on GitHub <https://github.com/3SConsult/sir3stoolkit/issues>`_. Describe the situation in detail — whether it's a bug you encountered or a feature you'd like to see improved. Feel free to attach images or other relevant materials to help us better understand your request.

For other requests, please contact us at `sir3stoolkit@3sconsult.de <mailto:sir3stoolkit@3sconsult.de>`_.

License
-------
MIT License. See `LICENSE <https://github.com/3SConsult/sir3stoolkit/blob/master/LICENSE>`_ for details.

