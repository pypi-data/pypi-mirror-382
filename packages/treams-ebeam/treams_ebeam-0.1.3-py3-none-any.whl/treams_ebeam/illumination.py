import scipy.constants as spc
import treams

def ebeam(
    k0, vel, impact=None, *,material=None, modetype=None, poltype=None
):
    m = 0
    pol = 1
    kz = k0/vel
    gamma = 1 / (1 - vel**2)**0.5
    a_0_kz = 1j * spc.e * kz / (4 * spc.c * spc.epsilon_0 * gamma)
    if impact is None:
        basis = treams.CylindricalWaveBasis.default([kz], m)
    else:
        basis = treams.CylindricalWaveBasis.default([kz], m, positions = [[impact[0], impact[1], 0]])
    if modetype == 'regular':
        raise ValueError("modetype must be singular")
        if poltype == 'helicity':
            raise ValueError("poltype must be parity")
    res = [0] * len(basis)
    res[basis.index((0, kz, m, pol))] = a_0_kz
    
    return treams.PhysicsArray(
        res, basis=basis, k0=k0, material=material, modetype='singular', poltype='parity'
    )