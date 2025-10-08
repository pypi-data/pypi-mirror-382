import matplotlib.pyplot as plt
import numpy as np
import treams
treams.config.POLTYPE = 'parity'
import scipy.constants as spc

import treams_ebeam as tre

def test_cl_eels():
    pts = 200
    hw = np.linspace(2, 5, pts)
    hbar_eV = spc.hbar/spc.e
    k0s = hw / hbar_eV / spc.c * 1e-9
    materials = (treams.Material(16+0.5j), treams.Material())
    lmax = 5
    radius = 50
    b = [60, 0]
    vel = 0.7

    cl = np.zeros(pts)
    eels = np.zeros(pts)

    for i, k0 in enumerate(k0s):
        kz = k0/vel
        tm = treams.TMatrix.sphere(lmax, k0, radius, materials) 
        inc = tre.ebeam(k0, vel, b) 
        cwb = treams.CylindricalWaveBasis.default(kz,lmax)
        inc = inc.expand(cwb, 'regular') 
        inc = inc.expand(tm.basis)
        cl[i] = tre.cl(tm, inc)
        eels[i] = tre.eels(tm, inc)  
        
    #TODO check against reference data instead of just plotting
    plt.plot(hw, eels, label ='EELS')
    plt.plot(hw, cl, label ='CL')
    plt.xlabel(r"$\hbar\omega$ (eV)")
    plt.legend()
    plt.savefig("tests/out/test_cl_eels.png", dpi=300)

if __name__ == "__main__":
    test_cl_eels()