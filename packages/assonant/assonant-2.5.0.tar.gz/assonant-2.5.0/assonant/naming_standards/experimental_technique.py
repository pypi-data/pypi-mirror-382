"""Expermiental Technique names definitions."""

from enum import Enum


class ExperimentalTechniquesAcronyms(Enum):
    """Experimental Technique acronyms standards."""

    ARPES = "ARPES"
    CD = "CD"
    CT = "CT"
    MX = "MX"
    PDF = "PDF"
    PEEM = "PEEM"
    RIXS = "RIXS"
    SAXS = "SAXS"
    STMX = "STMX"
    USAXS = "USAXS"
    WAXS = "WAXS"
    XAS = "XAS"
    XES = "XES"
    XEOL = "XEOL"
    XMCD = "XMCD"
    XPS = "XPS"
    XPCS = "XPCS"
    XRD = "XRD"
    XRF = "XRF"


class ExperimentalTechniquesFullNames(Enum):
    """Experimental Technique full name standards."""

    ARPES = "Angle-Resolved Photoemission Spectroscopy"
    CD = "Circular Dichroism Spectroscopy"
    CT = "Computed Tomography"
    MX = "Macromolecular Crystallography"
    PDF = "Pair Distribution Function"
    PEEM = "Photoemission Electron Microscopy"
    RIXS = "Resonant Inelastic X-ray Scattering"
    SAXS = "Small Angle X-ray Scattering"
    STMX = "Scanning Transmission X-ray Microscopy"
    USAXS = "Ultra-Small Angle X-ray Scattering"
    WAXS = "Wide-Angle X-ray Scattering"
    XAS = "X-ray Absortion Spectroscopy"
    XES = "X-ray Emission Spectroscopy"
    XEOL = "X-ray Excited Optical Luminescence"
    XMCD = "X-ray Magnetic Circular Dichroism"
    XPS = "X-ray Photonelectron Spectroscopy"
    XPCS = "X-ray Photon Correlation Spectroscopy"
    XRD = "X-ray Diffraction"
    XRF = "X-ray Fluorescence"
