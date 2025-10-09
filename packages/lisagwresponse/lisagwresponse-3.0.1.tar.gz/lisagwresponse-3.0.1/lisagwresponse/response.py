"""
Core module.

Implements the base class to compute LISA response to gravitational waves, plot
them and write a gravitational-wave file.

Authors:
    Jean-Baptiste Bayle <j2b.bayle@gmail.com>
"""

import abc
import logging
from typing import Callable, Literal, Optional, Tuple

import astropy
import astropy.coordinates
import h5py
import importlib_metadata
import matplotlib.pyplot as plt
import numpy as np
from astropy.coordinates import SkyCoord
from lisaconstants import GM_SUN, PARSEC, c
from lisaconstants.indexing import LINKS
from lisaconstants.indexing import SPACECRAFT as SC
from numpy import cos, pi, sin
from numpy.typing import ArrayLike
from packaging.version import Version

from .utils import (
    arrayindex,
    bspline_interp,
    chunk_slices,
    dot,
    emitter,
    norm,
    receiver,
)

logger = logging.getLogger(__name__)

Interpolant = Callable[[np.ndarray], np.ndarray]


class Response(abc.ABC):
    """Abstract base class representing a GW source.

    Args:
        orbits: Path to orbit file.
        orbit_interp_order: Orbits spline-interpolation order.
    """

    def __init__(self, orbits: str, orbit_interp_order: int = 2) -> None:

        self.git_url = "https://gitlab.in2p3.fr/lisa-simulation/gw-response"
        self.version = importlib_metadata.version("lisagwresponse")
        self.classname = self.__class__.__name__
        logger.info(
            "Initializing gravitational-wave response (lisagwresponse verion %s)",
            self.version,
        )

        #: Path to orbit file.
        self.orbits_path: str = str(orbits)
        #: Orbits spline-interpolation order.
        self.orbit_interp_order: int = int(orbit_interp_order)

    @abc.abstractmethod
    def compute_gw_response(self, t: ArrayLike, link: ArrayLike = LINKS) -> np.ndarray:
        """Compute link response to gravitational waves.

        If ``t`` is of shape ``(N,)``, the same time array is used for all
        links; otherwise a different time array is used for each link, and ``t``
        should have the shape ``(N, M)``, if ``(M,)`` is the shape of ``link``.

        The link responses are expressed as dimensionless relative frequency
        fluctuations, or Doppler shifts, or strain units.

        Args:
            t: TCB times [s], as the number of seconds elapsed since the LISA
                epoch, of shape (N,) or (N, M).
            link: Link indices, of shape (M,).

        Returns:
            Link responses [strain, a.k.a. relative frequency shift], as an
            array of shape (N, M).
        """
        raise NotImplementedError

    def plot(
        self, t: ArrayLike, output: str | None = None, title: str | None = None
    ) -> None:
        """Plot gravitational-wave response.

        Args:
            t: TCB times [s], as the number of seconds elapsed since the LISA
                epoch, of shape (N,) or (N, 6).
            output: Output filename, or ``None`` to only show the plots.
            title: Optional plot title.
        """
        logger.info("Plotting gravitational-wave response")
        plt.figure(figsize=(12, 4))
        response = self.compute_gw_response(t, LINKS)
        for link_index, link in enumerate(LINKS):
            plt.plot(t, response[:, link_index], label=link)
        plt.grid()
        plt.legend()
        plt.xlabel("Time [s]")
        plt.ylabel("Link response")
        if title is not None:
            plt.title(title)
        # Save or show glitch
        if output is not None:
            logger.info("Saving plot to %s", output)
            plt.savefig(output, bbox_inches="tight")
        else:
            logger.info("Showing plots")
            plt.show()

    def _interpolate_tps(self, tau: ArrayLike, sc: ArrayLike = SC) -> np.ndarray:
        r"""Return TCB times corresponding to TPS times.

        GW responses :math:`H_{ij}^{t}(\tau)` are computed as functions of TCB.

        To compute GW responses as functions of the receiving spacecraft TPS
        :math:`H_{ij}^{\tau_i}(\tau)`, one needs to convert those reception TPSs
        :math:`\tau` to their TCB equivalent :math:`t^{\tau_i}`, such that

        .. code-block :: python

            H_{ij}^{\tau_i}(\tau) = H_{ij}^{t}(t^{\tau_i}(\tau)) \qs

        Orbit files contain a vector of TCB times for a regularly sampled TPS
        time grid.

        Use this method to interpolate between these values and obtain the TCB
        equivalent times for an arbitrary vector of TPS times, and for each
        spacecraft.

        Args:
            tau: TPS times [s] for all spacecraft, of shape (N,).
            sc: Spacecraft indices in an array of shape (M,).

        Returns:
            Equivalent TPS times [s], as the number of seconds elapsed since the
            LISA epoch, as an array of shape (N, M).

        Raises:
            ValueError: If ``tau`` lies outside of the orbit valid range (no
            extrapolation is allowed here).
        """
        logger.info("Computing spline interpolation for TPS times")
        tau = np.asarray(tau)
        sc = np.asarray(sc)

        def interpolate(t, data) -> Interpolant:
            return bspline_interp(t, data, k=self.orbit_interp_order, ext="raise")

        with h5py.File(self.orbits_path, "r") as orbitf:

            # Warn for orbit file development version
            version = Version(orbitf.attrs["version"])
            logger.debug("Using orbit file version %s", version)
            if version.is_devrelease or version.local is not None:
                logger.warning("You are using an orbit file in a development version")
            if version > Version("3.0"):
                logger.warning(
                    "You are using an orbit file in a version that "
                    "might not be fully supported"
                )

            if version >= Version("2.0.dev"):
                times = (
                    orbitf.attrs["t0"]
                    + np.arange(orbitf.attrs["size"]) * orbitf.attrs["dt"]
                )
                orbit_sc = [1, 2, 3]
                tps = [
                    interpolate(
                        times,
                        times + orbitf["tps/delta_t"][:, arrayindex(sci, orbit_sc)],
                    )(tau)
                    for sci in sc
                ]
            else:
                tps = [
                    interpolate(orbitf["/tps/tau"], orbitf[f"/tps/sc_{sci}"])(tau)
                    for sci in sc
                ]

        return np.stack(tps, axis=-1)  # (N, M)

    @staticmethod
    def read_file_sampling(path: str) -> Optional[Tuple[float, int, float]]:
        """Read the sampling parameters from a GW file.

        Args:
            path: Path to GW file.

        Returns:
            A tuple ``(dt, size, t0)`` for the GW file, or ``None`` if the file
            does does not exist or does not contain the sampling parameters.
        """
        logger.info("Reading sampling parameters from file '%s'", path)
        try:
            with h5py.File(path, "r") as hdf5:
                dt = hdf5.attrs["dt"]
                size = hdf5.attrs["size"]
                t0 = hdf5.attrs["t0"]
        except (FileNotFoundError, KeyError):
            logger.warning("Cannot read sampling parameters from '%s'", path)
            return None
        return dt, size, t0

    def _write_attr(self, hdf5: h5py.Group, prefix: str, *names: str) -> None:
        """Write a single object attribute as metadata on ``hdf5``.

        This method is used in :meth:`lisagwresponse.Response._write_metadata`
        to write Python self's attributes as HDF5 attributes.

        >>> class ConcreteResponse(Response):
        ...     def __init__(self):
        ...         self.parameter = 42
        ...     def compute_gw_response(self):
        ...         return np.zeros(6)
        >>> response = ConcreteResponse()
        >>> with h5py.File("test.h5", "w") as hdf5:
        ...     response._write_attr(hdf5, 'prefix_', 'parameter')
        >>> with h5py.File("test.h5", "r") as hdf5:
        ...     hdf5.attrs["prefix_parameter"]
        np.int64(42)

        Args:
            hdf5: HDF5 group or dataset to write to.
            prefix: Prefix for attribute names.
            names*: Attribute names.
        """
        for name in names:
            hdf5.attrs[f"{prefix}{name}"] = getattr(self, name)

    def _write_metadata(self, hdf5: h5py.Group, prefix: str = "") -> None:
        """Write relevant object's attributes as metadata on ``hdf5``.

        This is for tracability and reproducibility. All parameters
        necessary to re-instantiate the response object and reproduce the
        exact same simulation should be written to file.

        Use the :meth:`lisagwresponse.Response._write_attr` method.

        .. admonition:: Suclassing notes
            This class is intended to be overloaded by subclasses to write
            additional attributes.

        .. important::
            You MUST call super implementation in subclasses.

        Args:
            hdf5: HDF5 group or dataset to write to.
            prefix: Prefix for attribute names.
        """
        self._write_attr(
            hdf5,
            prefix,
            "git_url",
            "version",
            "classname",
            "orbits_path",
            "orbit_interp_order",
        )

    def write(
        self,
        path: str,
        dt: float = 0.3,
        size: int = 259200,
        t0: float = 0,
        mode: str = "a",
        timeframe: Literal["tps"] | Literal["tcb"] | Literal["both"] = "both",
        chunks: int | None = None,
    ) -> None:
        """Compute and write the response to a GW file.

        If the file does not exist, it is created with a time axis matching
        ``dt``, ``size``, and ``t0`` arguments. The link responses are computed
        according to these parameters and written to file.

        If the file already exists, we make sure that ``dt``, ``size``, and
        ``t0`` match the values used to create the file and raise an error if
        they do not. Use :meth:`lisagwresponse.Response.read_file_sampling` to
        get the value for these parameters from an existing file.

        When creating the GW file, metadata are saved as attributes.

        When writing the link responses, we add attributes for each local
        variable, prefixed with ``gw<i>``, where i is the index of GW response
        in the file.

        Args:
            path: Path to GW file.
            dt: Time step (applies to both TPS and TCB grids) [s].
            size: Number of samples.
            t0: Start time [s] (applied to both TPS and TCB grids). When
                interpreted as a TCB time, this is the number of seconds elapsed
                since the LISA epoch.
            mode: File opening mode.
            timeframe: Time coordinate(s) in which the response is computed
                (either 'tps', 'tcb', or 'both').
            chunks: Number of samples per chunk for memory optimization. If
                None, the response for the whole time series is computed at
                once, which can require a lot of memory.
        """
        # pylint: disable=too-many-branches,too-many-statements
        with h5py.File(path, mode) as hdf5:

            # Write sampling parameters if needed
            sampling = self.read_file_sampling(path)
            if sampling is None:
                logger.info("New GW file with version %s", self.version)
                # Warn if development version (might create incompatibilities)
                if Version(self.version).is_devrelease:
                    logger.warning("You are using a GW file in a development version")
                # Write sampling parameters
                hdf5.attrs["dt"] = dt
                hdf5.attrs["fs"] = 1 / dt
                hdf5.attrs["size"] = size
                hdf5.attrs["t0"] = t0
                hdf5.attrs["duration"] = size * dt
                logger.info("Setting global metadata")
                hdf5.attrs["gw_count"] = 0
                hdf5.attrs["timeframe"] = timeframe
                self._write_metadata(hdf5)
                # Create link response datasets
                if timeframe in ["both", "tcb"]:
                    hdf5["tcb/y"] = np.zeros((size, 6))
                if timeframe in ["both", "tps"]:
                    hdf5["tps/y"] = np.zeros((size, 6))
            else:
                # If file exists, check version
                version = Version(hdf5.attrs["version"])
                logger.debug("Existing GW file of version %s", version)
                # Warn if development version (might create incompatibilities)
                if version.is_devrelease or version.local is not None:
                    logger.warning("You are using a GW file in a development version")
                # Only accept to append to a GW of same version
                if version < Version("2.0.dev"):
                    raise ValueError(f"unsupported GW file version '{version}'")
                # Only accept ``timeframe`` value that matches the file's
                if timeframe != hdf5.attrs["timeframe"]:
                    raise ValueError(
                        f"timeframe parameter '{timeframe}' does not match that "
                        f"of the GW file '{hdf5.attrs['timeframe']}'"
                    )
                # Check that sampling parameters match the file's
                if sampling != (dt, size, t0):
                    raise ValueError("Sampling parameters do not match")

            # Setting metadata for this source
            logger.debug("Setting new source metadata")
            ngw = int(hdf5.attrs["gw_count"])
            hdf5.attrs["gw_count"] = ngw + 1
            self._write_metadata(hdf5, prefix=f"gw{ngw}_")
            # Compute equivalent TCB times for TPSs
            receivers = arrayindex(receiver(LINKS), SC)
            if chunks is None:
                chunks = size
            for i, chunk_slice in enumerate(chunk_slices(size, chunks)):
                t = (
                    t0
                    + np.arange(
                        start=chunk_slice.start, stop=chunk_slice.stop, dtype=np.float64
                    )
                    * dt
                )  # (N')
                if timeframe == "both":
                    tau = self._interpolate_tps(t, SC)  # (N', 3)
                    tau_links = tau[:, receivers]  # (N', 6)
                    t_links = np.tile(t[:, np.newaxis], 6)  # (N', 6)
                    times = [t_links, tau_links]  # (N', 6)
                    datasets = ["tcb/y", "tps/y"]
                elif timeframe == "tcb":
                    times = [t]  # (N')
                    datasets = ["tcb/y"]
                elif timeframe == "tps":
                    tau = self._interpolate_tps(t, SC)  # (N', 3)
                    tau_links = tau[:, receivers]  # (N', 6)
                    times = [tau_links]  # (N', 6)
                    datasets = ["tps/y"]
                else:
                    raise ValueError(f"invalid timeframe '{timeframe}'")
                logger.info("Computing gravitational-wave response for chunk %d", i)
                for dataset, sub_times in zip(datasets, times):
                    # Compute link response
                    response = self.compute_gw_response(sub_times, LINKS)  # (N', 6)
                    # Add response to link datasets
                    logger.info("Writing link response datasets")
                    hdf5[dataset][chunk_slice] += response  # (N', 6)
        # Closing file
        logger.info("Closing gravitational-wave file '%s'", path)


class ReadResponse(Response):
    """Interpolate user-provided link responses.

    To honor the source's sampling parameters, the input time series may be
    resampled using spline interpolation. If you do not wish to interpolate,
    make sure to use this class with sampling parameters matching your input
    data.

    Args:
        t_interp: TCB times associated with link responses [s], as the number of
            seconds elapsed since the LISA epoch, of shape (N,).
        y_12: Response of link 12, of shape (N,).
        y_23: Response of link 23, of shape (N,).
        y_31: Response of link 31, of shape (N,).
        y_13: Response of link 13, of shape (N,).
        y_32: Response of link 32, of shape (N,).
        y_21: Response of link 21, of shape (N,).
        interp_order: Response spline-interpolation order.
        **kwargs: All other args from :class:`lisagwresponse.Response`.
    """

    def __init__(
        self,
        t_interp: ArrayLike,
        y_12: ArrayLike,
        y_23: ArrayLike,
        y_31: ArrayLike,
        y_13: ArrayLike,
        y_32: ArrayLike,
        y_21: ArrayLike,
        interp_order: int = 1,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        #: Response spline-interpolation order.
        self.interp_order: int = int(interp_order)
        # Compute spline interpolation
        logger.info("Computing spline interpolation from time series")
        data = {12: y_12, 23: y_23, 31: y_31, 13: y_13, 32: y_32, 21: y_21}
        #: Dictionary of interpolating spline functions (link indices as keys).
        self.interpolants = {
            link: bspline_interp(t_interp, data[link], k=self.interp_order)
            for link in LINKS
        }

    def compute_gw_response(self, t: ArrayLike, link: ArrayLike = LINKS) -> np.ndarray:
        # Interpolate strain
        t = np.asarray(t)
        link = np.asarray(link)
        if t.ndim == 1:
            responses = [self.interpolants[a_link](t) for a_link in link]
        elif t.ndim == 2:
            responses = [
                self.interpolants[a_link](t[:, i]) for i, a_link in enumerate(link)
            ]
        else:
            raise TypeError(f"invalid time array shape '{t.shape}'")
        return np.stack(responses, axis=-1)  # (N, M)


class ResponseFromStrain(Response, abc.ABC):
    """Abstract base that computes link responses from GW strain time series.

    DO NOT modify the attributes ``ra`` and ``dec`` directly, use the
    :meth:`lisagwresponse.ResponseFromStrain.set_position` method instead.

    The parameter ``shift_sun`` controls how the response is computed when
    calling :meth:`lisagwresponse.ResponseFromStrain.compute_gw_response`. If
    ``shift_sun`` is ``'always'``, the times given in ``t`` are shifted to the
    equivalent times at the Sun, such that there is no phase shift of the
    response w.r.t. the strain time series (given at the Sun). If ``shift_sun``
    is ``'constant'``, the shift is only computed using the constellation
    barycenter position at ``t[0]``, such that Doppler effect is still accounted
    for in longer simulations. If ``shift_sun`` is ``'never'``, no shift is
    applied.

    Args:
        ra: Source right ascension (equatorial longitude) in ICRS [rad].
        dec: Source declination (equatorial latitude) in ICRS [rad].
        x: Spacecraft x-position interpolants in ICRS (when set, overrides
            ``orbits`` argument) [m].
        y: Spacecraft y-position interpolants in ICRS (when set, overrides
            ``orbits`` argument) [m].
        z: Spacecraft z-position interpolants in ICRS (when set, overrides
            ``orbits`` argument) [m].
        ltt: Light travel time interpolants (when set, overrides``orbits``
            argument) [s].
        shift_sun: Method to shift times to the Sun (either "never",
            "constant", "always").
        **kwargs: All other args from :class:`lisagwresponse.Response`.
    """

    def __init__(
        self,
        ra: float,
        dec: float,
        x: None | dict[int, Interpolant | float] = None,
        y: None | dict[int, Interpolant | float] = None,
        z: None | dict[int, Interpolant | float] = None,
        ltt: None | dict[int, Interpolant | float] = None,
        *,
        shift_sun: Literal["never"] | Literal["constant"] | Literal["always"] = "never",
        **kwargs,
    ) -> None:

        super().__init__(**kwargs)

        #: Source right ascension (equatorial longitude) in ICRS [rad].
        self.ra: float | None = None
        #: Source declination (equatorial latitude) in ICRS [rad].
        self.dec: float | None = None
        #: Wave propagation unit vector in ICRS.
        self.k: np.ndarray | None = None
        #: Wave propagation unit vector in ICRS.
        self.u: np.ndarray | None = None
        #: Wave propagation unit vector in ICRS.
        self.v: np.ndarray | None = None

        #: Whether to shift times to the Sun.
        #: Refer to the class docstring for more information.
        if shift_sun not in ["never", "constant", "always"]:
            raise ValueError(
                f"invalid shift_sun value '{shift_sun}', "
                "must be 'never', 'constant', or 'always'"
            )
        self.shift_sun = shift_sun

        # Compute source-localization vector basis
        self.set_position(ra, dec)

        # Handle orbits
        # If interpolating functions are already provided, use them
        if x is not None or y is not None or z is not None or ltt is not None:
            logger.info("Using provided functions for orbits")
            assert x is not None
            assert y is not None
            assert z is not None
            assert ltt is not None
            self._set_orbits(x, y, z, ltt)
        else:
            logger.info("Reading orbits from file '%s'", self.orbits_path)
            self._interpolate_orbits()

    def _write_metadata(self, hdf5: h5py.Group, prefix: str = "") -> None:
        super()._write_metadata(hdf5, prefix)
        self._write_attr(hdf5, prefix, "ra", "dec")

    def set_position(self, ra: float, dec: float) -> None:
        """Set the source position in the sky.

        This triggers the computation of the sour-localization basis vectors.

        Args:
            ra: Source right ascension (equatorial longitude) in ICRS [rad].
            dec: Source declination (equatorial latitude) in ICRS [rad].
        """
        self.ra = float(ra)
        self.dec = float(dec)

        # Compute source-localization vector basis
        self.k = np.array(
            [
                -cos(dec) * cos(ra),
                -cos(dec) * sin(ra),
                -sin(dec),
            ]
        )
        self.u = np.array([sin(ra), -cos(ra), 0])
        self.v = np.array(
            [
                -sin(dec) * cos(ra),
                -sin(dec) * sin(ra),
                cos(dec),
            ]
        )

    def _interpolate_orbits(self) -> None:
        """Interpolate orbital information from an orbit file.

        Raises:
            ValueError: If orbit file is not supported.
        """
        logger.info("Computing spline interpolation for orbits")

        def interpolate(t, data) -> Interpolant:
            return bspline_interp(t, data, k=self.orbit_interp_order, ext="raise")

        with h5py.File(self.orbits_path, "r") as orbitf:

            # Warn for orbit file development version
            version = Version(orbitf.attrs["version"])
            logger.debug("Using orbit file version %s", version)
            if version.is_devrelease or version.local is not None:
                logger.warning("You are using an orbit file in a development version")
            if version > Version("3.0"):
                logger.warning(
                    "You are using an orbit file in a version "
                    "that might not be fully supported"
                )

            if version >= Version("2.0.dev"):
                times = (
                    orbitf.attrs["t0"]
                    + np.arange(orbitf.attrs["size"]) * orbitf.attrs["dt"]
                )
                self.x = {
                    sc: interpolate(times, orbitf["tcb/x"][:, i, 0])
                    for i, sc in enumerate(SC)
                }
                self.y = {
                    sc: interpolate(times, orbitf["tcb/x"][:, i, 1])
                    for i, sc in enumerate(SC)
                }
                self.z = {
                    sc: interpolate(times, orbitf["tcb/x"][:, i, 2])
                    for i, sc in enumerate(SC)
                }
                self.ltt = {
                    link: interpolate(times, orbitf["tcb/ltt"][:, i])
                    for i, link in enumerate(LINKS)
                }
            else:
                self.x = {
                    sc: interpolate(orbitf["tcb/t"], orbitf[f"tcb/sc_{sc}"]["x"])
                    for sc in SC
                }
                self.y = {
                    sc: interpolate(orbitf["tcb/t"], orbitf[f"tcb/sc_{sc}"]["y"])
                    for sc in SC
                }
                self.z = {
                    sc: interpolate(orbitf["tcb/t"], orbitf[f"tcb/sc_{sc}"]["z"])
                    for sc in SC
                }
                self.ltt = {
                    link: interpolate(orbitf["tcb/t"], orbitf[f"tcb/l_{link}"]["tt"])
                    for link in LINKS
                }

    def _set_orbits(
        self,
        x: dict[int, Interpolant | float],
        y: dict[int, Interpolant | float],
        z: dict[int, Interpolant | float],
        ltt: dict[int, Interpolant | float],
    ) -> None:
        """Set user-provided interpolating functions as orbital information.

        We also accept floats in the dictionaries, standing for constant values.

        Args:
            x: Spacecraft x-position interpolants in ICRS [m].
            y: Spacecraft y-position interpolants in ICRS [m].
            z: Spacecraft z-position interpolants in ICRS [m].
            ltt: Light travel time interpolants [s].
        """
        # pylint: disable=cell-var-from-loop
        # We use default values for `val` in lambdas to capture the values

        def ascallable(a: Interpolant | float) -> Interpolant:
            """Return a callable.

            Scalar values are returned as constant functions.

            Args:
                a: Input value.

            Returns:
                A callable.
            """
            if callable(a):
                return a

            def func(t: np.ndarray) -> np.ndarray:
                return np.full_like(t, float(a))

            return func

        self.x = {sc: ascallable(x[sc]) for sc in SC}
        self.y = {sc: ascallable(y[sc]) for sc in SC}
        self.z = {sc: ascallable(z[sc]) for sc in SC}
        self.ltt = {link: ascallable(ltt[link]) for link in LINKS}

    @abc.abstractmethod
    def compute_hplus(self, t: ArrayLike) -> np.ndarray:
        """Compute gravitational-wave strain :math:`h_+(t)`.

        Args:
            t: TCB times [s], as the number of seconds elapsed since the LISA
                epoch, of shape (N,).
        """
        raise NotImplementedError

    @abc.abstractmethod
    def compute_hcross(self, t: ArrayLike) -> np.ndarray:
        """Compute gravitational-wave strain :math:`h_\\times(t)`.

        Args:
            t: TCB times [s], as the number of seconds elapsed since the LISA
                epoch, of shape (N,).
        """
        raise NotImplementedError

    def compute_gw_response(
        self,
        t: ArrayLike,
        link: ArrayLike = LINKS,
    ) -> np.ndarray:
        """Compute the link responses to the gravitational-wave strain.

        See :doc:`model` to see the derivation of the link response function.

        The link responses are expressed as dimensionless relative frequency
        fluctuations, or Doppler shifts, or strain units.

        If ``t`` is of shape ``(N,)``, the same time array is used for all
        links; otherwise a different time array is used for each link, and ``t``
        should have the shape ``(N, M)``, if ``(M,)`` is the shape of ``link``.

        Args:
            t: TCB times [s], as the number of seconds elapsed since the LISA
                epoch, of shape (N,) or (N, M).
            link: Link indices, of shape (M,).

        Returns:
            Link responses [strain, a.k.a. relative frequency shifts], as an
            array of shape (N, M).

        Raises:
            ValueError: If orbit information is missing, often caused when the
                orbit file does not have enough margins (at the beginning and
                end of the simulation) to account for the Sun-to-constellation
                phase or the inter-satellite light travel time.
            ValueError: When an invalid option for ``shift_sun`` is provided.
        """
        # pylint: disable=too-many-locals,too-many-statements
        logger.info("Computing gravitational-wave response for links %s", link)
        assert self.k is not None
        assert self.u is not None
        assert self.v is not None

        # Broadcast times if needed
        t = np.asarray(t)
        link = np.asarray(link)
        if t.ndim == 1:
            t = np.tile(t[:, np.newaxis], len(link))  # (N, M)

        # Compute emission and reception time at spacecraft
        logger.debug("Computing emission time at spacecraft")
        trec = t  # (N, M)
        temi = np.copy(t)  # (N, M)
        for link_index, a_link in enumerate(link):
            temi[:, link_index] -= self.ltt[a_link](t[:, link_index])  # (N, M)

        # Compute spacecraft positions at emission and reception
        try:
            logger.debug("Computing receiver position at reception time")
            xrec = np.empty((*t.shape, 3))  # (N, M, 3)
            for i, (a_link, a_receiver) in enumerate(zip(link, receiver(link))):
                xrec[:, i, 0] = self.x[a_receiver](trec[:, i])  # (N,)
                xrec[:, i, 1] = self.y[a_receiver](trec[:, i])  # (N,)
                xrec[:, i, 2] = self.z[a_receiver](trec[:, i])  # (N,)
            logger.debug("Computing emitter position at emission time")
            xemi = np.empty((*t.shape, 3))  # (N, M, coord)
            for i, (a_link, an_emitter) in enumerate(zip(link, emitter(link))):
                xemi[:, i, 0] = self.x[an_emitter](temi[:, i])  # (N,)
                xemi[:, i, 1] = self.y[an_emitter](temi[:, i])  # (N,)
                xemi[:, i, 2] = self.z[an_emitter](temi[:, i])  # (N,)
        except ValueError as error:
            logger.error("Missing orbit information")
            raise ValueError(
                "missing orbit information, use longer orbit file or adjust sampling"
            ) from error

        # Compute link unit vector
        logger.debug("Computing link unit vector")
        n = xrec - xemi  # (N, M, 3)
        n /= norm(n)[..., np.newaxis]  # (N, M, 3)

        if self.shift_sun == "never":
            # Compute equivalent emission and reception time at the Sun
            logger.debug("Computing equivalent reception time at the Sun")
            trec_sun = trec - dot(xrec, self.k) / c  # (N, M)
            logger.debug("Computing equivalent emission time at the Sun")
            temi_sun = temi - dot(xemi, self.k) / c  # (N, M)
        elif self.shift_sun == "constant":
            # Compute constant shift from constellation barycenter at t[0]
            logger.debug("Computing constant shift from constellation barycenter")
            xbary = np.mean(xrec[0, :, :], axis=0)  # (3,)
            shift = dot(xbary, self.k) / c  # ()
            logger.debug("Computing equivalent reception time at the Sun")
            trec_sun = trec + shift - dot(xrec, self.k) / c  # (N, M)
            logger.debug("Computing equivalent emission time at the Sun")
            temi_sun = temi + shift - dot(xemi, self.k) / c  # (N, M)
        elif self.shift_sun == "always":
            # Use temi and trec as equivalent times at the Sun
            logger.debug(
                "Using emission and reception times as equivalent times at the Sun"
            )
            trec_sun = trec  # (N, M)
            temi_sun = temi  # (N, M)
        else:
            raise ValueError(f"invalid shift_sun value '{self.shift_sun}'")

        # Compute antenna pattern functions
        logger.debug("Computing antenna pattern functions")
        xiplus = dot(n, self.u) ** 2 - dot(n, self.v) ** 2  # (N, M)
        xicross = 2 * dot(n, self.u) * dot(n, self.v)  # (N, M)

        # Compute hplus and hcross contributions
        logger.debug("Computing gravitational-wave response")
        termplus = np.empty_like(temi_sun)  # (N, M)
        termcross = np.empty_like(trec_sun)  # (N, M)
        for i in range(len(link)):
            termplus[:, i] = self.compute_hplus(temi_sun[:, i]) - self.compute_hplus(
                trec_sun[:, i]
            )  # (N,)
            termcross[:, i] = self.compute_hcross(temi_sun[:, i]) - self.compute_hcross(
                trec_sun[:, i]
            )  # (N,)
        return (termplus * xiplus + termcross * xicross) / (2 * (1 - dot(n, self.k)))

    def plot(
        self, t: ArrayLike, output: str | None = None, title: str | None = None
    ) -> None:
        """Plot gravitational-wave response and strain.

        Args:
            t: TCB times [s], as the number of seconds elapsed since the LISA
                epoch, of shape (N,) or (N, 6).
            output: Output filename, or ``None`` to only show the plots.
            title: Optional plot title.
        """
        # Initialize the plot
        _, axes = plt.subplots(2, 1, figsize=(12, 8))
        axes[1].set_xlabel("Time [s]")
        if title is not None:
            axes[0].set_title(title)
        # Computing and plotting response
        logger.info("Plotting gravitational-wave response")
        axes[0].set_ylabel("Link response")
        response = self.compute_gw_response(t, LINKS)  # (N, 6)
        for link_index, link in enumerate(LINKS):
            axes[0].plot(t, response[:, link_index], label=link)
        # Computing and plotting strain
        logger.info("Plotting gravitational-wave strain")
        axes[1].set_ylabel("Gravitational-wave strain")
        hplus = self.compute_hplus(t)  # (N,)
        hcross = self.compute_hcross(t)  # (N,)
        axes[1].plot(t, hplus, label=r"$h_+$")
        axes[1].plot(t, hcross, label=r"$h_\times$")
        # Add legend and grid
        for axis in axes:
            axis.legend()
            axis.grid()
        # Save or show glitch
        if output is not None:
            logger.info("Saving plot to %s", output)
            plt.savefig(output, bbox_inches="tight")
        else:
            plt.show()


class ReadStrain(ResponseFromStrain):
    r"""Interpolate user-provided strain, and compute the link responses.

    To honor the source's sampling parameters, the input strain time series may
    be resampled using spline interpolation. If you do not wish to interpolate,
    make sure to use this class with sampling parameters matching your input
    data.

    Args:
        t_interp: TCB times [s], as the number of seconds elapsed since the LISA
            epoch, of shape (N,).
        hplus: Strain :math:`h_+` time series, of shape (N,).
        hcross: Strain :math:`h_\times` time series, of shape (N,).
        strain_interp_order: Strain spline-interpolation order.
        **kwargs: All other args from :class:`lisagwresponse.Response`.
    """

    def __init__(
        self,
        t_interp: ArrayLike,
        hplus: ArrayLike,
        hcross: ArrayLike,
        strain_interp_order: int = 5,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        # Strain interpolation order.
        self.strain_interp_order = int(strain_interp_order)
        #: Strain :math:`h_+` interpolating function.
        self.hplus: Callable[[ArrayLike], np.ndarray] | None = None
        #: Strain :math:`h_\\times` interpolating function.
        self.hcross: Callable[[ArrayLike], np.ndarray] | None = None

        self.set_strain(t_interp, hplus, hcross)

    def set_strain(
        self, t_interp: ArrayLike, hplus: ArrayLike, hcross: ArrayLike
    ) -> None:
        """Set new strain time series.

        Strain is interpolated if necessary (see class documentation).
        Other attributes are not affected.

        Args:
            t_interp: TCB times [s], of shape (N,).
            hplus: Strain :math:`h_+` time series, of shape (N,).
            hcross: Strain :math:`h_\\times` time series, of shape (N,).
        """
        logger.info("Computing spline interpolation for gravitational-wave strain")
        self.hplus = bspline_interp(t_interp, hplus, k=self.strain_interp_order)
        self.hcross = bspline_interp(t_interp, hcross, k=self.strain_interp_order)

    def _write_metadata(self, hdf5: h5py.Group, prefix: str = "") -> None:
        super()._write_metadata(hdf5, prefix)
        self._write_attr(hdf5, prefix, "strain_interp_order")

    def compute_hplus(self, t: ArrayLike) -> np.ndarray:
        assert self.hplus is not None
        return self.hplus(t)

    def compute_hcross(self, t: ArrayLike) -> np.ndarray:
        assert self.hcross is not None
        return self.hcross(t)


class GalacticBinary(ResponseFromStrain):
    """Represent a chirping Galactic binary.

    Args:
        A: Strain amplitude.
        f: Frequency at :attr:`t_init` [Hz].
        df: Frequency derivative [Hz/s].
        phi0: Initial phase at :attr:`t_init` [rad].
        iota: Inclination angle [rad].
        psi: Polarization angle [rad].
        t_init: TCB time for initial conditions [s], as the number of seconds
            elapsed since the LISA epoch.
        **kwargs: All other args from :class:`lisagwrespons.ResponseFromStrain`.
    """

    def __init__(
        self,
        A: float,
        f: float,
        df: float = 0,
        phi0: float = 0,
        iota: float = 0,
        psi: float = 0,
        t_init: float = 0.0,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        #: Strain amplitude.
        self.A = float(A)
        #: Frequency at :attr:`t_init` [Hz].
        self.f = float(f)
        #: Frequency derivative [Hz/s].
        self.df = float(df)
        #: Initial phase at :attr:`t_init` [rad].
        self.phi0 = float(phi0)
        #: Inclination angle [rad].
        self.iota = float(iota)
        #: Polarization angle [rad].
        self.psi = float(psi)
        #: TCB time for initial conditions [s].
        self.t_init = float(t_init)

    def _write_metadata(self, hdf5: h5py.Group, prefix: str = "") -> None:
        super()._write_metadata(hdf5, prefix)
        self._write_attr(hdf5, prefix, "A", "f", "df", "phi0", "iota", "psi", "t_init")

    def compute_strain_in_source_frame(
        self, t: ArrayLike
    ) -> tuple[np.ndarray, np.ndarray]:
        """Compute strain for plus and cross polarizations in the source frame.

        Args:
            t: TCB times [s], of shape (N,).

        Returns:
            Strain time series for plus and cross polarizations ``(hplus,
            hcross)``, in the source frame, as arrays of shape (N,).
        """
        logger.info("Compute gravitational-wave strain in the source frame")
        t_elapsed = np.asarray(t) - self.t_init
        phase = pi * self.df * t_elapsed**2 + 2 * pi * self.f * t_elapsed - self.phi0
        hplus = -self.A * (1 + cos(self.iota) ** 2) * cos(phase)
        hcross = -2 * self.A * cos(self.iota) * sin(phase)
        return (hplus, hcross)

    def compute_hplus(self, t: ArrayLike) -> np.ndarray:
        logger.info("Compute +-polarized gravitational-wave strain")
        hplus_source, hcross_source = self.compute_strain_in_source_frame(t)
        return hplus_source * cos(2 * self.psi) - hcross_source * sin(2 * self.psi)

    def compute_hcross(self, t: ArrayLike) -> np.ndarray:
        logger.info("Compute x-polarized gravitational-wave strain")
        hplus_source, hcross_source = self.compute_strain_in_source_frame(t)
        return hplus_source * sin(2 * self.psi) + hcross_source * cos(2 * self.psi)


class VerificationBinary(GalacticBinary):
    """Represent a verification Galactic binary.

    This class inherits from :class:`lisagwresponse.GalacticBinary`, and
    provides an initializer using the verification binary parametrization. All
    parameters are converted to those of the
    :class:`lisagwresponse.GalacticBinary`.

    Args:
        period: System period [s].
        distance: Luminosity distance [pc].
        masses: Object masses [solar mass].
        glong: Galactic longitude [deg].
        glat: Galactic latitude [deg].
        **kwargs: All other args from :class:`lisagwresponse.GalacticBinary`.

    Raises:
        ValueError: If ICRS coordinates are provided instead of Galactic
            coordinates.
    """

    def __init__(
        self,
        period: float,
        distance: float,
        masses: tuple[float, float],
        glong: float,
        glat: float,
        **kwargs,
    ) -> None:
        #: System period [s].
        self.period = float(period)
        #: Luminosity distance [pc].
        self.distance = float(distance)
        #: Object masses [solar mass].
        self.masses = tuple(sorted([float(masses[0]), float(masses[1])]))
        #: Galactic longitude [deg].
        self.glong = float(glong)
        #: Galactic latitude [deg].
        self.glat = float(glat)

        # Check that we use Galactic coordinates
        if ("ra" in kwargs) or ("dec" in kwargs):
            raise ValueError("Cannot use ICRS coordinates for verification binary")

        # Convert sky location
        galactic_coords = SkyCoord(glong, glat, unit="deg", frame="galactic")
        icrs_coords = galactic_coords.icrs
        assert isinstance(icrs_coords, SkyCoord)
        assert isinstance(icrs_coords.ra, astropy.coordinates.angles.core.Longitude)
        assert isinstance(icrs_coords.dec, astropy.coordinates.angles.core.Latitude)
        kwargs["ra"] = icrs_coords.ra.rad
        kwargs["dec"] = icrs_coords.dec.rad

        # Compute masses
        total_mass = (masses[0] + masses[1]) * GM_SUN / c**3
        reduced_mass = masses[0] * masses[1] / (masses[0] + masses[1]) ** 2
        chirp_mass = total_mass * reduced_mass ** (3 / 5)

        # Convert parameters
        f = 2.0 / period  # Hz
        light_dist = distance * PARSEC / c  # light-second
        df = (
            (96 / 5) * chirp_mass ** (5 / 3) * np.pi ** (8 / 3) * f ** (11 / 3)
        )  # Hz / s
        A = (
            2
            * (total_mass ** (5 / 3) * reduced_mass / light_dist)
            * (np.pi * f) ** (2 / 3)
        )

        super().__init__(A, f, df, **kwargs)

    def _write_metadata(self, hdf5: h5py.Group, prefix: str = "") -> None:
        super()._write_metadata(hdf5, prefix)
        self._write_attr(hdf5, prefix, "period", "distance", "masses", "glong", "glat")
