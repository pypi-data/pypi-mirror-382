"""
Stochastic sources and background.

Authors:
    Jean-Baptiste Bayle <j2b.bayle@gmail.com>
    Arianna Renzini <arenzini@caltech.edu>
"""

import logging

import h5py
import healpy
import matplotlib.pyplot as plt
import numpy as np
from lisaconstants import au, c
from lisaconstants.indexing import LINKS
from numpy.typing import ArrayLike

from .psd import Generator
from .response import Interpolant, ReadStrain, Response

logger = logging.getLogger(__name__)


class StochasticPointSource(ReadStrain):
    """Represent a point-like gravitational-wave stochastic source.

    This class is used to represent independant pixels in a whole-sky
    :class:`lisagwresponse.StochasticBackground` instance.

    This class generates random strain time series (one for each polarization),
    which is interpolated to compute the link responses for the source. An
    instance of this class is initiated for a certain time window, and one
    cannot compute the response outside of this window (i.e., extrapolation of
    the strain time series is not supported).

    Args:
        generator: Stochastic generator for the strain time series (see
            :class:`lisagwresponse.psd.Generator`).
        t0: Initial TCB time for the strain time series [s], as the number of
            seconds elapsed since the LISA epoch.
        dt: Sampling period for the strain time series [s].
        size: Simulation size for the strain time series [samples].
        margin: Left and right time interpolation margin for strain time series
            [s]. Default is 1.2 au / c, to account for the maximum phase between
            the Sun and the constellation barycenter, with a 20% margin.
        **kwargs: All other args from :class:`lisagwresponse.ReadStrain`.
    """

    def __init__(
        self,
        generator: Generator,
        t0: float,
        dt: float,
        size: int,
        margin: float = 1.2 * au / c,
        **kwargs,
    ) -> None:

        #: Stochastic generator for the strain time series.
        self.generator = generator

        #: Initial TCB time for the strain time series [s].
        self.t0 = t0 - margin
        #: Sampling period for the strain time series [s].
        self.dt = dt
        #: Simulation size for the strain time series [samples].
        self.size = size + 2 * int(margin // dt)

        logger.debug("Generating stochastic strain time series")
        hplus = generator(1 / self.dt, self.size)
        hcross = generator(1 / self.dt, self.size)

        super().__init__(t_interp=self.strain_t, hplus=hplus, hcross=hcross, **kwargs)

    @property
    def strain_t(self) -> np.ndarray:
        """Strain time series [s]."""
        return self.t0 + np.arange(self.size) * self.dt

    def _write_metadata(self, hdf5: h5py.Group, prefix: str = "") -> None:
        super()._write_metadata(hdf5, prefix)
        self._write_attr(hdf5, prefix, "t0", "dt", "size", "strain_interp_order")

    def compute_hplus(self, t: ArrayLike) -> np.ndarray:
        assert self.hplus is not None
        try:
            return self.hplus(t)
        except ValueError as error:
            logger.error("Missing hplus strain data to interpolate at\n%s", t)
            raise ValueError("missing hplus strain data to interpolate") from error

    def compute_hcross(self, t: ArrayLike) -> np.ndarray:
        assert self.hcross is not None
        try:
            return self.hcross(t)
        except ValueError as error:
            logger.error("Missing hcross strain data to interpolate at\n%s", t)
            raise ValueError("missing hcross strain data to interpolate") from error


class StochasticBackground(Response):
    """Represent a whole-sky gravitational-wave stochastic background.

    The sky is pixelized using healpix, and each pixel is considered as a
    stochastic point source, whose power is the product of the background
    spectrum and the pixel amplitude on the sky map.

    The response of each link is the superposition of the responses to each of
    the pixels (i.e., the stochastic point sources) making up the sky. Note that
    using a greater number of pixels increases the precision of the response but
    also the computational cost.

    .. admonition:: Memory usage

        Stochastic point sources are created for each pixel when an instance of
        :class:`StochasticBackground` is initialized, which triggers the
        generation of the random strain time series for the entire sky.

        For long simulations, this might not be tractable in terms of memory
        usage. In this case, we recommend that you use ``optim=True`` to keep
        the memory usage to a minimum; when enabled, point sources are not
        created at initialization time, but when they are needed in
        :meth:`compute_gw_response`, then immediately destroyed.

        Note that in this case, you will be limited to a single call to
        :meth:`compute_gw_response`. Subsequent calls will generate new point
        sources, leading to different an inconsistent sky.

    Args:
        skymap: Amplitude sky map (created from Healpix) in ICRS, of shape
            ``(npix,)``.
        generator: Stochastic generator shared by all pixels, for the strain
            time series (see :class:`lisagwresponse.psd.Generator`).
        t0: Initial TCB time for the strain time series [s], as the number of
            seconds elapsed since the LISA epoch.
        dt: Sampling period for the strain time series [s].
        size: Simulation size for the strain time series [samples].
        margin: Left and right time interpolation margin for strain time series
            [s]. Default is 1.2 au / c, to account for the maximum phase between
            the Sun and the constellation barycenter, with a 20% margin.
        optim: Enable memory usage optimization. If enabled, stochastic point
            sources are only created when needed, and immediately destroyed.
            This will limit you to a single call to :meth:`compute_gw_response`.
        **kwargs: All other args from :class:`lisagwresponse.Response`.
    """

    def __init__(
        self,
        skymap: ArrayLike,
        generator: Generator,
        t0: float,
        dt: float,
        size: int,
        margin: float = 1.2 * au / c,
        optim: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        #: Initial TCB time for the strain time series [s].
        self.t0 = t0 - margin
        #: Sampling period for the strain time series [s].
        self.dt = dt
        #: Simulation size for the strain time series [samples].
        self.size = size + 2 * int(margin // dt)

        #: Amplitude sky map in ICRS, of shape ``(npix,)``.
        self.skymap: np.ndarray = np.asarray(skymap)
        #: Stochastic generator shared by all pixels, for the strain time series.
        self.generator: Generator = generator
        #: Number of sky pixels. Equivalently number of point sources.
        self.npix: int = len(self.skymap)
        #: Whether memory optimization is enabled.
        self.optim: bool = optim
        #: Healpix ``nside``.
        self.nside: int = healpy.npix2nside(self.npix)

        logger.info("Using a resolution of %s pixels (nside=%s)", self.npix, self.nside)

        #: List of stochastic point sources, one for each pixel.
        #:
        #: If memory optimization is enabled, this list is empty and the sources
        #: are created on the fly in :meth:`compute_gw_response`.
        self.sources: list[StochasticPointSource] = []

        # Track if we call `compute_gw_response()` multiple times to issue a warning
        #: Whether we have called `compute_gw_response()` at least once.
        self.called_once: bool = False

        # Build point sources if memory optimization is disabled
        if not self.optim:
            logger.info("Building stochastic point sources")
            x, y, z, ltt = None, None, None, None  # only interpolate orbits once
            for pixel in range(self.npix):
                source = self.point_source(pixel, x, y, z, ltt)
                if source is not None:
                    x, y, z, ltt = source.x, source.y, source.z, source.ltt
                    self.sources.append(source)

    @property
    def strain_t(self) -> np.ndarray:
        """Strain time series [s]."""
        return self.t0 + np.arange(self.size) * self.dt

    def _write_metadata(self, hdf5: h5py.Group, prefix: str = "") -> None:
        super()._write_metadata(hdf5, prefix)
        self._write_attr(
            hdf5, prefix, "skymap", "npix", "nside", "t0", "dt", "size", "optim"
        )

    def compute_gw_response(self, t: ArrayLike, link: ArrayLike = LINKS) -> np.ndarray:
        """Compute link response to stochastic background.

        Each link response is computed as the sum of each pixel's stochastic
        point source's link response.

        .. warning:: Memory optimization

            If memory optimization is enabled (see :attr:`optim`), each call to
            this function will return a new stochastic point source with a new,
            independent strain time series for the same pixel.

        Args:
            t: TCB times [s], as the number of seconds elapsed since the LISA
                epoch, of shape (N,) or (N, M).
            link: Link indices, of shape (M,).

        Returns:
            Link responses [strain, a.k.a. relative frequency shift], as an
            array of shape (N, M).
        """
        t = np.asarray(t)
        link = np.asarray(link)

        # If memory optimization is disabled, we can compute the response
        # directly by summing the contributions of each pixel
        if not self.optim:
            responses = [s.compute_gw_response(t, link) for s in self.sources]
            response = sum(responses)  # (N, M) or (,)
            return np.broadcast_to(response, (len(t), len(link)))  # (N, M)

        # If memory optimization is enabled, each source is destroyed after it's
        # been used Check that we haven't called `compute_gw_response()` before
        if self.called_once:
            logger.warning(
                "Multiple calls to `compute_gw_response()` when memory optimization "
                "is enabled may lead to inconsistent results"
            )
        self.called_once = True

        x, y, z, ltt = None, None, None, None
        gw_response = np.zeros((len(t), len(link)))  # (N, M)
        # Loop over pixels and add contributions
        for pixel in range(self.npix):
            source = self.point_source(pixel, x, y, z, ltt)
            if source is not None:
                gw_response += source.compute_gw_response(t, link)  # (N, M)
                # We rely on the first pixel to interpolate the orbits,
                # and reuse this interpolation for all remaining pixels
                x, y, z, ltt = source.x, source.y, source.z, source.ltt
                del source

        return gw_response  # (N, M)

    def point_source(
        self,
        pixel: int,
        x: Interpolant | None = None,
        y: Interpolant | None = None,
        z: Interpolant | None = None,
        ltt: Interpolant | None = None,
    ) -> None | StochasticPointSource:
        """Return the stochastic point source for a given pixel.

        The spectrum of the pixel is computed as the product of the sky
        modulation :attr:`skymap` at this pixel, and the stochastic background
        spectrum :attr:`generator`.

        .. warning:: Memory optimization

            If memory optimization is enabled (see :attr:`optim`), each call to
            this function will return a new stochastic point source with a new,
            independent strain time series for the same pixel.

        Args:
            pixel: Pixel index.
            x: Spacecraft x-position interpolant (overrides orbits) [m].
            y: Spacecraft y-position interpolant (overrides orbits) [m].
            z: Spacecraft z-position interpolant (overrides orbits) [m].
            ltt: Light travel times interpolant (overrides orbits) [s].

        Returns:
            Stochastic point source instance, or None if the pixel is black.

        Raises:
            ValueError: If the pixel index is out of range.
        """
        if pixel not in range(self.npix):
            raise ValueError(f"pixel '{pixel}' out of range")

        # Bypass black pixel
        if not self.skymap[pixel]:
            logger.info("Bypassing black pixel %s", pixel)
            return None

        logger.info("Initializing stochastic point source for pixel %s", pixel)

        # Theta and phi are colatitude and longitude, respectively (healpy conventions)
        # They are converted to dec and ra, latitude and longitude (LDC conventions)
        theta, phi = healpy.pix2ang(self.nside, pixel)
        dec, ra = np.pi / 2 - theta, phi

        # Define a function to compute the generator for the pixel
        def pixel_generator(fs: float, size: int) -> np.ndarray:
            return self.skymap[pixel] * self.generator(fs, size)

        return StochasticPointSource(
            generator=pixel_generator,
            t0=self.t0,
            dt=self.dt,
            size=self.size,
            margin=0,
            ra=ra,
            dec=dec,
            orbits=self.orbits_path,
            orbit_interp_order=self.orbit_interp_order,
            x=x,
            y=y,
            z=z,
            ltt=ltt,
        )

    def plot(
        self, t: ArrayLike, output: str | None = None, title: str | None = None
    ) -> None:
        """Plot gravitational-wave response and intensity sky map.

        Args:
            t: TCB times [s], as the number of seconds elapsed since the LISA
                epoch, of shape (N,) or (N, 6).
            output: Output filename, or ``None`` to only show the plots.
            title: Optional plot title.
        """
        # Initialize the plot
        _, axes = plt.subplots(
            2, 1, figsize=(12, 10), gridspec_kw={"height_ratios": [1, 1.5]}
        )
        axes[0].set_xlabel("Time [s]")
        if title is not None:
            axes[0].set_title(title)
        # Computing and plotting response
        logger.info("Plotting gravitational-wave response")
        axes[0].set_ylabel("Link response")
        response = self.compute_gw_response(t, LINKS)  # (N, M)
        for link_index, link in enumerate(LINKS):
            axes[0].plot(t, response[:, link_index], label=link)
        axes[0].legend()
        axes[0].grid()
        # Plotting sky map
        plt.axes(axes[1])
        logger.info("Plotting sky map of power spectral density")
        healpy.mollview(
            self.skymap, hold=True, title="", unit="Power spectral density at 1 Hz"
        )
        # Save or show glitch
        if output is not None:
            logger.info("Saving plot to %s", output)
            plt.savefig(output, bbox_inches="tight")
        else:
            plt.show()
