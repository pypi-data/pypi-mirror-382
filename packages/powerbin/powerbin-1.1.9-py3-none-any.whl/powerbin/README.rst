The PowerBin Package
====================

**PowerBin: Fast Adaptive Data Binning with Centroidal Power Diagrams**

.. image:: https://users.physics.ox.ac.uk/~cappellari/images/powerbin-logo.svg
    :target: https://users.physics.ox.ac.uk/~cappellari/software/#sec:powerbin
    :width: 100
.. image:: https://img.shields.io/pypi/v/powerbin.svg
    :target: https://pypi.org/project/powerbin/
.. image:: https://img.shields.io/badge/arXiv-2509.06903-orange.svg
    :target: https://arxiv.org/abs/2509.06903
.. image:: https://img.shields.io/badge/DOI-10.48550/arXiv.2509.06903-green.svg
    :target: https://doi.org/10.48550/arXiv.2509.06903
    
This `PowerBin` package provides a Python implementation of the **PowerBin** algorithm — a modern alternative to the classic Voronoi binning method. Like Voronoi binning, it performs 2D adaptive spatial binning to achieve a nearly constant value per bin of a chosen *capacity* (e.g., signal‑to‑noise ratio or any other user‑defined function of the bin spaxels).

**Key advances over the classic method include:**

- **Centroidal Power Diagram:** Produces bins that are nearly round, convex, and connected, and eliminates the disconnected or nested bins that could occur with earlier approaches.

- **Scalability:** The entire algorithm scales with **O(N log N)** complexity, removing the **O(N^2)** bottleneck previously present in both the bin-accretion and regularization steps. This makes processing million‑pixel datasets practical.

- **Stable CPD construction:** Generates the tessellation via a heuristic inspired by packed soap bubbles, avoiding the numerical fragility of formal CPD solvers with realistic non-additive capacities (e.g., correlated noise).

The algorithm combines a fast initial bin-accretion phase with iterative regularization, and is described in detail in `Cappellari (2025) <https://arxiv.org/abs/2509.06903>`_.

.. contents:: :depth: 2

Attribution
-----------

If you use this software for your research, please cite `Cappellari (2025)`_.
The BibTeX entry for the paper is::

    @ARTICLE{Cappellari2025,
        author = {{Cappellari}, M.},
        title = "{PowerBin: Fast adaptive data binning with Centroidal Power Diagrams}",
        journal = {MNRAS},
        eprint = {2509.06903},
        year = 2025,
        note = {submitted}
    }

Installation
------------

install with::

    pip install powerbin

Without write access to the global ``site-packages`` directory, use::

    pip install --user powerbin

To upgrade ``PowerBin`` to the latest version use::

    pip install --upgrade powerbin

Usage Examples
--------------

To learn how to use the ``PowerBin`` package, copy, modify and run
the example programs in the ``powerbin/examples`` directory.
It can be found within the main ``powerbin`` package installation folder
inside `site-packages <https://stackoverflow.com/a/46071447>`_.
The detailed documentation is contained in the docstring of the file
``powerbin/powerbin.py``, or on `PyPi <https://pypi.org/project/powerbin/>`_.

Minimal example
---------------

Below is a minimal, runnable example. It demonstrates how to use ``PowerBin``
and highlights the two ways to specify the bin capacity. In this example, we
define the capacity as ``(S/N)^2``, so the target capacity is set to ``target_sn**2``.

The capacity can be specified in two forms:

1.  **As an array** (by setting ``additive=True``): This is the simplest approach,
    recommended when the capacity is additive (e.g., when noise is Poissonian,
    the total ``(S/N)^2`` is the sum of the individual pixel values). For very
    large datasets (millions of pixels), this method is also significantly faster.
    For small or moderate datasets, the speed difference is negligible.
2.  **As a function** (by setting ``additive=False``): This provides maximum
    flexibility for complex, non-additive capacity definitions. The S/N for a
    bin is calculated as ``np.sum(signal) / np.sqrt(np.sum(noise**2))``. This
    is the standard formula for uncorrelated noise and should be the default
    choice for most applications. One would only modify this for special cases,
    such as:
    
    - To account for known covariance in the noise between pixels. The example
      code shows a commented-out empirical correction, but this is data-dependent
      and not a general prescription.
    - To perform complex calculations on each bin (e.g., fitting a model to
      extract kinematics), which is a possible but advanced use case.

.. code-block:: python

    from importlib import resources
    import numpy as np
    import matplotlib.pyplot as plt
    from powerbin import PowerBin

    # Load example data: x, y, signal, noise
    data_path = resources.files('powerbin') / 'examples/sample_data_ngc2273.txt'
    x, y, signal, noise = np.loadtxt(data_path).T
    xy = np.column_stack([x, y])

    target_sn = 50

    # --- Define Capacity Specification ---
    # Toggle this flag to switch between the two methods.
    additive = False

    if additive:
        # 1. Additive case: Provide a pre-calculated array of pixel capacities.
        # This is efficient for capacities like (S/N)^2 with Poissonian noise.
        capacity_spec = (signal / noise)**2

    else:
        # 2. Non-additive case: Provide a function for custom capacity logic.
        def capacity_spec(index):
            """Calculates (S/N)^2 for a bin from its pixel indices."""
            # Standard S/N formula for uncorrelated noise
            sn = np.sum(signal[index]) / np.sqrt(np.sum(noise[index]**2))
            # Example for correlated noise (see full example file for details):
            # sn /= 1 + 1.07 * np.log10(len(index))
            return sn**2

    # Perform the binning. The target is target_sn**2 to match the capacity definition.
    pow = PowerBin(xy, capacity_spec, target_capacity=target_sn**2)

    # Plot the results. We use capacity_scale='sqrt' to display S/N instead of (S/N)^2.
    pow.plot(capacity_scale='sqrt', ylabel='S/N')

    plt.show()

###########################################################################
