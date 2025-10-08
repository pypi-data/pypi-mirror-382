import treams
from .observables_cylindrical import cl as _cl_cyl, eels as _eels_cyl
from .observables_spherical import cl as _cl_sph, eels as _eels_sph


def cl(tmat, illu):
    if isinstance(tmat, treams.TMatrix):
        return _cl_sph(tmat, illu)
    elif isinstance(tmat, treams.TMatrixC):
        return _cl_cyl(tmat, illu)
    
    raise NotImplementedError(
        f"CL not implemented for T-matrix of type {type(tmat)}"
    )

def eels(tmat, illu):
    if isinstance(tmat, treams.TMatrix):
        return _eels_sph(tmat, illu)
    elif isinstance(tmat, treams.TMatrixC):
        return _eels_cyl(tmat, illu)
    
    raise NotImplementedError(
        f"EELS not implemented for T-matrix of type {type(tmat)}"
    )