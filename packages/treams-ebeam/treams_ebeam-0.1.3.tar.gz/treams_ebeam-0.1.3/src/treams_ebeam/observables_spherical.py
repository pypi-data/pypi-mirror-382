import numpy as np
import scipy.constants as spc
import treams

def cl(tmat: treams.TMatrix, illu):
    r"""Cathodoluminescence (photon emission) probability.

    Possible for all T-matrices (global and local) in non-absorbing embedding. The
    values are calculated by

    .. math::

        \Gamma_\mathrm{CL}
        = \frac{1}{pi hw Z}
        a_{slm}^\ast T_{s'l'm',slm}^\ast k_{s'}^{-2} C_{s'l'm',s''l''m''}^{(1)}
        T_{s''l''m'',s'''l'''m'''} a_{s'''l'''m'''} \\

    where :math:`hw` is the photon energy, :math:`Z` is the impedance of the enbedding medium,
    :math:`a_{slm}` are the expansion coefficients of the illumination,
    :math:`T` is the T-matrix, :math:`C^{(1)}` is the (regular) translation
    matrix and :math:`k_s` are the wave numbers in the medium. All repeated indices
    are summed over. The result is coverted to [1/eV] by dividing with hbar in SI units.

    Args:
        illu (complex, array): Illumination coefficients
    Returns:
        float
    """
    if not tmat.material.isreal:
        raise NotImplementedError
    illu = treams.PhysicsArray(illu)
    illu_basis = illu.basis
    illu_basis = illu_basis[-2] if isinstance(illu_basis, tuple) else illu_basis
    if not isinstance(illu_basis, treams.SphericalWaveBasis):
        illu = illu.expand(tmat.basis)
    eps = tmat.material.epsilon
    mu = tmat.material.mu
    hbar_eV = spc.hbar/spc.e
    hw = hbar_eV*tmat.k0*1e9*spc.c  #[eV]
    Z = ((mu*spc.mu_0)/(eps*spc.epsilon_0))**0.5  #[Ohm]         
    p = tmat @ illu
    p_invksq = p * np.power(tmat.ks[tmat.basis.pol], -2) 
    del illu.modetype
    return (
        np.real(p.conjugate().T @ p_invksq.expand(p.basis)) / (np.pi * hw * Z) / spc.hbar
    )

def eels(tmat: treams.TMatrix, illu):
    r"""Electron energy-loss probability.

    Possible for all T-matrices (global and local) in non-absorbing embedding. The
    values are calculated by

    .. math::

        \Gamma_\mathrm{EEL}
        = \frac{1}{pi hw Z}
        a_{slm}^\ast k_s^{-2} T_{slm,s'l'm'} a_{s'l'm'}\\

    where :math:`hw` is the photon energy, :math:`Z` is the impedance of the enbedding medium,
    :math:`a_{slm}` are the expansion coefficients of the illumination,
    :math:`T` is the T-matrix, :math:`C^{(1)}` is the (regular) translation
    matrix and :math:`k_s` are the wave numbers in the medium. All repeated indices
    are summed over. The result is coverted to [1/eV] by dividing with hbar in SI units.

    Args:
        illu (complex, array): Illumination coefficients
    Returns:
        float
    """
    if not tmat.material.isreal:
        raise NotImplementedError
    illu = treams.PhysicsArray(illu)
    illu_basis = illu.basis
    illu_basis = illu_basis[-2] if isinstance(illu_basis, tuple) else illu_basis
    if not isinstance(illu_basis, treams.SphericalWaveBasis):
        illu = illu.expand(tmat.basis)
    eps = tmat.material.epsilon
    mu = tmat.material.mu
    hbar_eV = spc.hbar/spc.e
    hw = hbar_eV*tmat.k0*1e9*spc.c  #[eV]
    Z = ((mu*spc.mu_0)/(eps*spc.epsilon_0))**0.5  #[Ohm]   
    p = tmat @ illu
    p_invksq = p * np.power(tmat.ks[tmat.basis.pol], -2) 
    del illu.modetype
    return (
        -np.real(illu.conjugate().T @ p_invksq) / (np.pi * hw * Z) / spc.hbar
    )