"""
Utility PSD functions.

This module provides functions for stationary noise generation.

Authors:
    Quentin Baghi <quentin.baghi@protonmail.com>
    Jean-Baptiste Bayle <j2b.bayle@gmail.com>
"""

from typing import Callable

import numpy as np
from numpy.fft import ifft

#: Type for a stochastic generator.
#:
#: It is a function of the sampling frequency [Hz] and simulation size
#: [samples], and returns a numpy array of the generated noise time series.
Generator = Callable[[float, int], np.ndarray]


def white_generator(psd: float) -> Generator:
    """Returns a Gaussian white-noise generator.

    Args:
        psd: One-sided power spectral density [X^2/Hz].

    Returns:
        A stochastic generator, as a function of the sampling frequency [Hz] and
        simulation size [samples].
    """

    def generator(fs: float, size: int) -> np.ndarray:
        stddev = np.sqrt(psd * fs / 2)
        return np.random.normal(scale=stddev, size=size)

    return generator


def ifft_generator(spectrum: Callable[[np.ndarray], np.ndarray]) -> Generator:
    """Returns a stochastic generator that uses the IFFT method.

    Args:
        spectrum: One-sided power spectral density function [X^2/Hz].

    Returns:
        A stochastic generator, as a function of the sampling frequency [Hz] and
        simulation size [samples].
    """

    def generator(fs: float, size: int) -> np.ndarray:
        fs = float(fs)
        size = int(size)

        n_psd = 2 * size
        f = np.fft.fftfreq(n_psd) * fs
        f[0] = f[1]
        psd_sqrt = np.sqrt(spectrum(np.abs(f)))
        if np.isscalar(psd_sqrt):
            psd_sqrt = np.repeat(psd_sqrt, len(f))

        n_fft = int((n_psd - 1) / 2)
        # Real part of the noise FFT: it is a gaussian random variable
        noise_tf_real = (
            np.sqrt(0.5)
            * psd_sqrt[0 : n_fft + 1]
            * np.random.normal(loc=0, scale=1, size=n_fft + 1)
        )
        # Imaginary part of the noise FFT:
        noise_tf_im = (
            np.sqrt(0.5)
            * psd_sqrt[0 : n_fft + 1]
            * np.random.normal(loc=0, scale=1, size=n_fft + 1)
        )

        # The Fourier transform must be real in f = 0
        noise_tf_im[0] = 0
        noise_tf_real[0] = noise_tf_real[0] * np.sqrt(2)

        # Create the NoiseTF complex numbers for positive frequencies
        noise_tf = noise_tf_real + 1j * noise_tf_im

        # To get a real valued signal we must have NoiseTF(-f) = NoiseTF*
        if n_psd % 2 == 0:
            # The TF at Nyquist frequency must be real in the case of an even
            # number of data
            noise_sym0 = np.array([psd_sqrt[n_fft + 1] * np.random.normal(0, 1)])
            # Add the symmetric part corresponding to negative frequencies
            noise_tf = np.hstack(
                (noise_tf, noise_sym0, np.conj(noise_tf[1 : n_fft + 1])[::-1])
            )
        else:
            noise_tf = np.hstack((noise_tf, np.conj(noise_tf[1 : n_fft + 1])[::-1]))

        tseries = ifft(np.sqrt(n_psd * fs / 2) * noise_tf)
        return tseries[0:size].real

    return generator
