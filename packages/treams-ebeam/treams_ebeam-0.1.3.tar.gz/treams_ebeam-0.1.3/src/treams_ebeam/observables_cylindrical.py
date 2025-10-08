import numpy as np
import scipy.constants as spc
import treams

def cl(tmat: treams.TMatrixC, illu):
    r"""Cathodoluminescence (photon emission) probability.

    Possible for all T-matrices (global and local) in non-absorbing embedding. The
    values are calculated by

    .. math::

        \lambda_\mathrm{sca}
        = \frac{1}{2 I}
        a_{sk_zm}^\ast T_{s'{k_z}'m',sk_zm}^\ast k_{s'}^{-2}
        C_{s'l'm',s''l''m''}^{(1)}
        T_{s''l''m'',s'''l'''m'''} a_{s'''l'''m'''} \\
        \sigma_\mathrm{ext}
        = \frac{1}{2 I}
        a_{slm}^\ast k_s^{-2} T_{slm,s'l'm'} a_{s'l'm'}

    where :math:`a_{slm}` are the expansion coefficients of the illumination,
    :math:`T` is the T-matrix, :math:`C^{(1)}` is the (regular) translation
    matrix and :math:`k_s` are the wave numbers in the medium. All repeated indices
    are summed over. The incoming flux is :math:`I`.

    Args:
        illu (complex, array): Illumination coefficients
    Returns:
        \Gamma_\mathrm{CL} in units 1 / (eV * nm)
    """
    if not tmat.material.isreal:
        raise NotImplementedError
    illu = treams.PhysicsArray(illu)
    illu_basis = illu.basis
    illu_basis = illu_basis[-2] if isinstance(illu_basis, tuple) else illu_basis
    if not isinstance(illu_basis, treams.CylindricalWaveBasis):
        illu = illu.expand(tmat.basis)
    hbar_eV = spc.hbar/spc.e 
    p = tmat @ illu
    p_invksq = p * np.power(tmat.ks[tmat.basis.pol], -2) 
    del illu.modetype
    return (
        np.real(p[tmat.basis.kz**2 <= tmat.k0**2].conjugate().T @ p_invksq.expand(p.basis)[tmat.basis.kz**2 <= tmat.k0**2]) * 4 * spc.epsilon_0 / (np.pi * hbar_eV ) / spc.hbar *1e-9
    )

def eels(tmat: treams.TMatrixC, illu):
    r"""Electron energy loss probability.

    Possible for all T-matrices (global and local) in non-absorbing embedding. The
    values are calculated by

    .. math::

        \lambda_\mathrm{sca}
        = \frac{1}{2 I}
        a_{sk_zm}^\ast T_{s'{k_z}'m',sk_zm}^\ast k_{s'}^{-2}
        C_{s'l'm',s''l''m''}^{(1)}
        T_{s''l''m'',s'''l'''m'''} a_{s'''l'''m'''} \\
        \sigma_\mathrm{ext}
        = \frac{1}{2 I}
        a_{slm}^\ast k_s^{-2} T_{slm,s'l'm'} a_{s'l'm'}

    where :math:`a_{slm}` are the expansion coefficients of the illumination,
    :math:`T` is the T-matrix, :math:`C^{(1)}` is the (regular) translation
    matrix and :math:`k_s` are the wave numbers in the medium. All repeated indices
    are summed over. The incoming flux is :math:`I`.

    Args:
        illu (complex, array): Illumination coefficients
    Returns:
        \Gamma_\mathrm{EEL} in units 1 / (eV * nm)
    """
    if not tmat.material.isreal:
        raise NotImplementedError
    illu = treams.PhysicsArray(illu)
    illu_basis = illu.basis
    illu_basis = illu_basis[-2] if isinstance(illu_basis, tuple) else illu_basis
    if not isinstance(illu_basis, treams.CylindricalWaveBasis):
        illu = illu.expand(tmat.basis)
    hbar_eV = spc.hbar/spc.e
    p = tmat @ illu
    p_invksq = p * np.power(tmat.ks[tmat.basis.pol], -2) 
    del illu.modetype
    return (
        np.real(illu.T @ p_invksq) * 4 * spc.epsilon_0 / (np.pi * hbar_eV ) / spc.hbar *1e-9
    )

