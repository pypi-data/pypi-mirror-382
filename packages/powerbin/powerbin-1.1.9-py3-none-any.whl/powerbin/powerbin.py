"""
#####################################################################

Copyright (C) 2025 Michele Cappellari  
E-mail: michele.cappellari_at_physics.ox.ac.uk  

Updated versions of this software are available at:  
https://pypi.org/project/powerbin/  

If you use this software in published research, please acknowledge it as:  
“PowerBin method by Cappellari (2025, MNRAS submitted)”  
https://arxiv.org/abs/2509.06903  

This software is provided “as is”, without any warranty of any kind,  
express or implied.  

Permission is granted for:  
 - Non-commercial use.  
 - Modification for personal or internal use, provided that this  
   copyright notice and disclaimer remain intact and unaltered  
   at the beginning of the file.  

All other rights are reserved. Redistribution of the code, in whole or in part,  
is strictly prohibited without prior written permission from the author.  

#####################################################################

V1.0.0: PowerBin created — MC, Oxford, 10 September 2025

Vx.x.xx: Additional changes are documented in the global CHANGELOG.rst
    file of the PowerBin package
"""
from time import perf_counter
from typing import Callable

import numpy as np
from numpy.typing import ArrayLike
import matplotlib.pyplot as plt
from scipy import spatial, sparse

from powerbin.bin_accretion import bin_accretion
from powerbin.early_stopper import EarlyStopper
from powerbin.plotting import format_asinh_axis
from powerbin.plotting import plot_power_diagram

#----------------------------------------------------------------------------

def power_diagram(xy, xybin, rbin):
    """Computes a Power Diagram tessellation for a set of 2D points."""

    rmax = 1.001*np.max(np.abs(rbin))   # Needs to make z**2 > 0 below
    znode = np.sqrt(rmax**2 - rbin**2)  # z**2 = R - r**2  Sec.5 Imai+84
    tree = spatial.KDTree(np.column_stack([xybin, znode]))
    _, bin_num = tree.query(np.column_stack([xy, np.zeros(len(xy))]), workers=-1)

    return bin_num

#----------------------------------------------------------------------

def update_bins(capacity_spec, xy, xybin, rbin, args=()):
    """Updates bin properties based on a new Power Diagram tessellation."""

    bin_num = power_diagram(xy, xybin, rbin)    # bin assignment of every pixel

    N = len(xy)
    S = sparse.csr_matrix((np.ones(N), (bin_num, np.arange(N))), shape=(rbin.size, N))
    npix = S.getnnz(1)  # number of pixels per bin
    xybin = (S @ xy) / npix[:, None]  # bin centroids

    if callable(capacity_spec):
        groups = np.split(S.indices, S.indptr[1:-1])
        capacity = np.fromiter((capacity_spec(idx, *args) for idx in groups), float)
    else:
        capacity = S @ capacity_spec    # bin capacities

    return xybin, npix, capacity, bin_num

#----------------------------------------------------------------------------

def regularization(xy, xybin, target_capacity, capacity_spec, verbose, args, maxiter):
    """Iteratively adjusts bin generators to equalize bin capacities.
    This function implements Algorithm 1 of Cappellari (2025)."""

    rbin = np.ones(len(xybin))
    stopper = EarlyStopper()
    damp = 0.5
    under_relax_printed = False

    for it in range(maxiter):

        xybin_old, rbin_old = xybin.copy(), rbin.copy()
        xybin, npix, capacity, bin_num = update_bins(capacity_spec, xy, xybin, rbin, args)

        fac = target_capacity / capacity
        rbin = np.sqrt(fac * npix / np.pi)

        # Under-relaxation step to reduce cycling
        if stopper.under_relax:
            if verbose >= 2 and not under_relax_printed:
                print("Under-relaxation started")
                under_relax_printed = True
            xybin = xybin_old + damp * (xybin - xybin_old)
            rbin = rbin_old + damp * (rbin - rbin_old)

        # Nearest neighbours of every bin
        dist = spatial.KDTree(xybin).query(xybin, 2, workers=-1)[0][:, 1]
        rbin = rbin.clip(0.5, dist - 0.5)

        diff = np.linalg.norm(xybin - xybin_old)

        if verbose >= 2:
            print(f'Iter: {it:4d}  Diff: {diff:.3f}')

        # Test for convergence
        if diff < 0.1:
            if verbose >= 2:
                print("Converged")
            break
        if stopper.update(diff):
            if verbose >= 2:
                print(f"Cycling over last {stopper.window} iterations")
            break
        if it >= maxiter - 1:
            if verbose >= 2:
                print("Reached maximum number of iterations")
        if verbose >= 3:
            plt.clf()
            plot_power_diagram(xy, None, bin_num, xybin, rbin, npix)
            plt.title(f'Power Diagram - Iter: {it}  Diff: {diff:.3f}')
            plt.pause(1)

    bin_num = power_diagram(xy, xybin, rbin)

    return bin_num, xybin, rbin, capacity, npix, it

#-----------------------------------------------------------------------

class PowerBin:
    """
    PowerBin Class
    ==============

    PowerBin Purpose
    ----------------

    Performs 2D adaptive spatial binning using Centroidal Power Diagrams.

    This class implements the **PowerBin** algorithm described in
    `Cappellari (2025) <https://arxiv.org/abs/2509.06903>`_. It partitions
    a set of 2D points (pixels) into bins, aiming for a nearly constant
    *capacity* per bin (e.g., signal-to-noise squared).

    Key advances over classic Voronoi binning include:

    - **Centroidal Power Diagram:** Produces nearly round, convex, and
      connected bins, avoiding issues like disconnected or nested bins.

    - **Scalability:** Uses O(N log N) algorithms, making it practical for
      datasets with millions of pixels.

    - **Stable Construction:** Employs a robust heuristic for building the
      diagram, avoiding numerical fragility.

    The algorithm has two main stages:

    1. **Bin Accretion:** Generates an initial set of bin centers.

    2. **Regularization:** Iteratively adjusts bin shapes to equalize their
       capacities.

    Parameters
    ----------
    xy: array_like of shape (npix, 2)
        Coordinates of the pixels to be binned.

    capacity_spec: callable or array_like of shape (npix,)
        The rule for calculating capacity, given in one of two forms:

        - **Callable:** A function ``fun(indices, *args) -> float`` that returns
          the total capacity of a bin containing the pixels at ``indices``.
          This allows for non-additive capacity definitions (for example with
          correlated noise).

        - **Array-like:** A 1D array ``dens`` of length ``npix``, where
          ``dens[j]`` is the additive capacity of pixel ``j``. The capacity of
          a bin is the sum of ``dens`` over its member pixels. This is faster.

    target_capacity: float
        The target capacity value for each bin.

    pixelsize: float, optional
        The size of a pixel in the input coordinate units. This is used to
        internally work in pixel units for numerical stability. If ``None``,
        it is estimated as the median distance to the second-nearest neighbor.

    verbose: int, optional
        Controls the level of printed output:

        - 0: No output.
        - 1: Basic summary (default).
        - 2: Detailed iteration-by-iteration progress.
        - 3: Same as 2, but also plots the binning at each iteration.

    regul: bool, optional
        If ``True`` (default), performs the iterative regularization step after
        the initial accretion. If ``False``, only accretion is performed.

    args: tuple, optional
        Additional positional arguments passed to ``capacity_spec`` when it is
        a callable function.

    maxiter: int, optional
        Maximum number of iterations for the regularization step (default: 50).

    Attributes
    ----------
    xy: ndarray of shape (npix, 2)
        The original input pixel coordinates.

    bin_num: ndarray of int of shape (npix,)
        An array where ``bin_num[j]`` gives the index of the bin containing
        pixel ``j``. This is the primary output for mapping pixels to bins.

    pixel_capacity: ndarray of shape (npix,)
        The capacity of each individual input pixel, derived from
        ``capacity_spec``.

    bin_capacity: ndarray of shape (nbin,)
        The final calculated capacity for each output bin.

    xybin: ndarray of shape (nbin, 2)
        The coordinates of the Power Diagram generators (bin centers), in the
        same units as the input ``xy``.

    rbin: ndarray of shape (nbin,)
        The radii of the Power Diagram generators, in the same units as ``xy``.

    npix: ndarray of int of shape (nbin,)
        The number of pixels in each bin.

    single: ndarray of bool of shape (nbin,)
        A boolean array indicating which bins contain one or zero pixels.

    rms_frac: float
        The fractional root-mean-square scatter of the ``bin_capacity`` values,
        calculated as a percentage for non-single bins.

    target_capacity, pixelsize, verbose, args :
        Stored values of the corresponding input parameters.

    References
    ----------
    .. [1] Cappellari, M. 2025, MNRAS submitted, https://arxiv.org/abs/2509.06903
    """
    def __init__(
        self,
        xy: ArrayLike,
        capacity_spec: Callable | ArrayLike,
        target_capacity: float,
        pixelsize: float | None = None,
        verbose: int = 1,
        regul: bool = True,
        args: tuple = (),
        maxiter: int = 50
    ) -> None:

        # --- Input Validation ---
        xy = np.asarray(xy, dtype=float)
        if xy.ndim != 2 or xy.shape[1] != 2:
            raise ValueError(
                f"xy must be a 2D array-like with shape (npix, 2), "
                f"but got shape {xy.shape}"
            )
        if xy.shape[0] == 0:
            raise ValueError("Input 'xy' cannot be empty.")
        if not np.all(np.isfinite(xy)):
            raise ValueError("xy must contain only finite values.")

        npix = xy.shape[0]
        if callable(capacity_spec):
            if np.ndim(capacity_spec([0, 1], *args)) != 0:
                raise ValueError("If 'capacity_spec' is a callable, it must return a single scalar number.")
        else:
            capacity_spec = np.asarray(capacity_spec)
            if capacity_spec.ndim != 1 or capacity_spec.shape[0] != npix:
                raise ValueError(f"'capacity_spec' must have shape ({npix},), but got {capacity_spec.shape}")
            if not np.all(np.isfinite(capacity_spec)):
                raise ValueError("If 'capacity_spec' is an array, it must contain only finite values.")

        if not isinstance(target_capacity, (int, float)) or target_capacity <= 0:
            raise ValueError("target_capacity must be a positive number.")

        if pixelsize is not None and (not isinstance(pixelsize, (int, float)) or pixelsize <= 0):
            raise ValueError("pixelsize, if provided, must be a positive number.")

        if not isinstance(verbose, int) or verbose < 0:
            raise ValueError("verbose must be a non-negative integer.")

        if not isinstance(args, tuple):
            raise TypeError("args must be a tuple.")

        if not isinstance(maxiter, int) or maxiter <= 0:
            raise ValueError("maxiter must be a positive integer.")
        # --- End Validation ---

        self.xy = xy
        self.capacity = capacity_spec
        self.target_capacity = target_capacity
        self.verbose = verbose
        self.args = args

        if pixelsize is None:
            dist, _ = spatial.KDTree(xy).query(xy, [2], workers=-1)
            pixelsize = np.median(dist)
        self.pixelsize = pixelsize

        # All operation in powerbin are performed in pixel units
        xy = xy/pixelsize

        t1 = perf_counter()
        xybin, pixel_capacity = bin_accretion(xy, target_capacity, capacity_spec, verbose, args)
        t2 = perf_counter()

        if regul:
            if verbose >= 1:
                print(f'Regularization...')
            bin_num, xybin, rbin, bin_capacity, npix, it = regularization(
                xy, xybin, target_capacity, capacity_spec, verbose, args, maxiter)
        else:
            it = 0
            rbin = np.zeros(len(xybin))
            xybin, npix, bin_capacity, bin_num = update_bins(capacity_spec, xy, xybin, rbin, args)
            rbin = np.sqrt(npix/np.pi)
        t3 = perf_counter()

        single = npix == 1   # single pixels
        rms = np.std(bin_capacity[~single], ddof=1)/np.mean(bin_capacity[~single])*100

        self.single = single 
        self.bin_num = bin_num
        self.xybin = xybin*pixelsize
        self.rbin = rbin*pixelsize
        self.bin_capacity = bin_capacity      # per bin
        self.npix = npix
        self.rms_frac = rms
        self.pixel_capacity = pixel_capacity    # per pixel

        if verbose >= 1:
            print(f'Bins: {rbin.size}; Single Pixels: {np.sum(single)}/{len(xy)}')
            print(f'Capacity Fractional RMS Scatter (%): {rms:.2f}')
            print(f'Time Accretion: {t2 - t1:.2f} s')
            if regul:
                print(f'Time Regularization (it={it}): {t3 - t2:.2f} s')

#----------------------------------------------------------------------------

    def plot(
        self,
        capacity_scale: str = "raw",
        ylabel: str | None = None,
        ylim: tuple[float, float] | None = None,
        magrange: float = 10,
        left_title: str | None = None,
        abscissa: str = "radius",
        points_alpha: float | None = None,
        rasterize_points: bool = True,
        legend_loc: str = "best"
    ) -> None:
        """
        Generates a two-panel plot summarizing the binning results.

        The left panel shows the Centroidal Power Diagram, with bins colored
        by their final capacity. The right panel shows the capacity of
        individual pixels and final bins as a function of radius.

        Parameters
        ----------
        capacity_scale: {"raw", "sqrt"}, optional
            Transformation to apply to the capacity values for plotting.
            - "raw": Plot the capacity as is (e.g., (S/N)^2).
            - "sqrt": Plot the square root of the capacity (e.g., S/N).
        ylabel: str, optional
            Custom y-axis label for the right panel. If None, a default label
            is generated based on `capacity_scale`.
        ylim: tuple of (float, float), optional
            A tuple `(bottom, top)` for the y-axis limits of the right panel.
            If None, limits are determined automatically.
        magrange: float, optional
            The magnitude range for the color scale of the pixel density
            contours in the left panel (default: 10).
        left_title: str, optional
            Custom title for the left panel. If None, a default is used.
        points_alpha: float, optional
            The alpha transparency for the input pixel data points in the
            right panel (default: 0.01).
        rasterize_points: bool, optional
            If ``True`` (default), the scatter plot of input pixels in the
            right panel is rasterized. This can significantly reduce file
            size and rendering time for vector output formats (e.g., PDF,
            SVG) when there are many points. Set to ``False`` to keep the
            points as vector elements.
        legend_loc: str, optional
            The location of the legend in the right panel, e.g., 'best',
            'upper left' (default: 'best').

        """
        # --- Input Validation ---
        if capacity_scale not in ("raw", "sqrt"):
            raise ValueError("capacity_scale must be either 'raw' or 'sqrt'.")

        if ylabel is not None and not isinstance(ylabel, str):
            raise TypeError("ylabel, if provided, must be a string.")

        if ylim is not None:
            if not isinstance(ylim, (list, tuple)) or len(ylim) != 2 or \
               not all(isinstance(v, (int, float)) for v in ylim):
                raise ValueError("ylim must be a tuple or list of two numbers, e.g., (bottom, top).")

        if not isinstance(magrange, (int, float)) or magrange <= 0:
            raise ValueError("magrange must be a positive number.")

        if points_alpha is not None and (not isinstance(points_alpha, (int, float)) or not (0 <= points_alpha <= 1)):
            raise ValueError("points_alpha must be a float between 0 and 1.")

        if not isinstance(rasterize_points, bool):
            raise TypeError("rasterize_points must be a boolean.")

        if not isinstance(legend_loc, str):
            raise TypeError("legend_loc must be a string.")
        # --- End Validation ---

        # Prepare data for plotting (scaled to pixel units)
        xy = self.xy / self.pixelsize
        xybin = self.xybin / self.pixelsize
        rbin = self.rbin / self.pixelsize
        pixel_capacity = self.pixel_capacity
        bin_capacity = self.bin_capacity
        target_capacity = self.target_capacity
        rms_frac = self.rms_frac
        single = self.single

        if capacity_scale == "sqrt":
            pixel_capacity = np.sqrt(pixel_capacity)   # per pixel
            bin_capacity = np.sqrt(bin_capacity)     # per bin
            target_capacity = np.sqrt(target_capacity)
            rms_frac = np.std(bin_capacity[~single], ddof=1)/np.mean(bin_capacity[~single])*100

        if ylabel is None:
            ylabel = "Capacity" if capacity_scale == "raw" else r"$\sqrt{\mathrm{Capacity}}$"

        rx, ry = np.ptp(xy, axis=0)
        _, (ax0, ax1) = plt.subplots(1, 2, width_ratios=[3 / 4, ry / rx], layout="constrained")
        ax1.set_box_aspect(3 / 4)

        # Left panel: Power Diagram
        plt.sca(ax0)
        plot_power_diagram(xy, pixel_capacity, self.bin_num, xybin, rbin, self.npix, magrange)
        ax0.set_title(left_title if left_title is not None else "Centroidal Power Diagram")
        ax0.set_xlabel('X (pixels)')
        ax0.set_ylabel('Y (pixels)')

        # Right panel: Capacity vs. Radius
        plt.sca(ax1)

        if abscissa == "radius":
            x_pix = np.hypot(*xy.T)
            x_bin = np.hypot(*xybin.T)
            xlabel = 'R (pixels)'
            x_left = -0.5
            x_right = np.max(x_pix)
        elif abscissa == "x":
            x_pix = xy[:, 0]
            x_bin = xybin[:, 0]
            xlabel = 'X (pixels)'
            x_left, x_right = np.min(x_pix), np.max(x_pix)
        else:  # "y"
            x_pix = xy[:, 1]
            x_bin = xybin[:, 1]
            xlabel = 'Y (pixels)'
            x_left, x_right = np.min(x_pix), np.max(x_pix)

        if points_alpha is None:
            points_alpha = 46/len(x_pix)**0.67
        ax1.plot(x_pix, pixel_capacity, '.k', alpha=points_alpha, markeredgewidth=0, 
                 label='Input', rasterized=rasterize_points)
        if single.sum() > 0:
            ax1.plot(x_bin[single], bin_capacity[single], 'xb', markersize=3, label='Single')
        ax1.plot(x_bin[~single], bin_capacity[~single], 'or', markersize=4.2, markeredgewidth=0, label='Bins')
        ax1.plot(x_bin[~single], bin_capacity[~single], 'ok', markersize=1, markeredgewidth=0)
        ax1.axhline(target_capacity, linestyle='--', linewidth=1, color='gray')
        ax1.axis([x_left, x_right, np.min(pixel_capacity), np.max(bin_capacity) * 1.5])
        
        if ylim is not None:
            ax1.set_ylim(ylim)  # Must preceed format_asinh_axis
        
        ax1.set_title(rf'Fractional RMS Scatter $\sigma={rms_frac:.1f}$ %')
        ax1.set_yscale('asinh')
        format_asinh_axis(ax1)
        ax1.set_xlabel(xlabel)
        ax1.set_ylabel(ylabel)
        
        leg = ax1.legend(loc=legend_loc, handletextpad=0, labelspacing=0)
        leg.legend_handles[0].set_alpha(0.5)

#----------------------------------------------------------------------------
