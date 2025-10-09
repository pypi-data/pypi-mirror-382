from py_wake.site.shear import PowerShear, MOSTShear, LogShear
from py_wake.utils.most import psi
from py_wake import np
from py_wake.tests import npt
from py_wake.site._site import UniformSite
import matplotlib.pyplot as plt
from numpy import newaxis as na


def test_power_shear():
    h_lst = np.arange(10, 100, 10)
    site = UniformSite([1], .1, shear=PowerShear(70, alpha=[.1, .2]))
    WS = site.local_wind(x=h_lst * 0, y=h_lst * 0, h=h_lst, wd=[0, 180], ws=[10, 12, 13]).WS

    if 0:
        plt.plot(WS.sel(wd=0, ws=10), h_lst, label='alpha=0.1')
        plt.plot((h_lst / 70)**0.1 * 10, h_lst, ':')
        plt.plot(WS.sel(wd=180, ws=12), h_lst, label='alpha=0.2')
        plt.plot((h_lst / 70)**0.2 * 12, h_lst, ':')
        plt.legend()
        plt.show()
    npt.assert_array_equal(WS.sel(wd=0, ws=10), (h_lst / 70)**0.1 * 10)
    npt.assert_array_equal(WS.sel(wd=180, ws=12), (h_lst / 70)**0.2 * 12)


def test_most_shear():

    h_lst = np.arange(10, 100, 10)
    h_zetas = [-0.5, 0.0, 0.5]
    for h_zeta in h_zetas:
        L_inv = h_zeta / 70.0
        site = UniformSite([1], .1, shear=MOSTShear(70, h_zeta=h_zeta, z0=[.02, 2], Cm1=5.0, Cm2=-16.0))
        WS = site.local_wind(x=h_lst * 0, y=h_lst * 0, h=h_lst, wd=[0, 180], ws=[10, 12]).WS

        if 0:
            plt.plot(WS.sel(wd=0, ws=10), h_lst, label='z0=0.02, h_zeta=%g' % h_zeta)
            plt.plot((np.log(h_lst / 0.02) - psi(h_lst * L_inv, Cm1=5.0, Cm2=-16.0)) / (np.log(70.0 / 0.02) - psi(h_zeta, Cm1=5.0, Cm2=-16.0)) * 10.0, h_lst, ':')
            plt.plot(WS.sel(wd=180, ws=12), h_lst, label='z0=2, h_zeta=%g' % h_zeta)
            plt.plot((np.log(h_lst / 2) - psi(h_lst * L_inv, Cm1=5.0, Cm2=-16.0)) / (np.log(70.0 / 2) - psi(h_zeta, Cm1=5.0, Cm2=-16.0)) * 12.0, h_lst, ':')
            if h_zeta == h_zetas[-1]:
                plt.legend()
                plt.show()
        npt.assert_array_equal(WS.sel(wd=0, ws=10), (np.log(h_lst / 0.02) - psi(h_lst * L_inv, Cm1=5.0, Cm2=-16.0)) / (np.log(70.0 / 0.02) - psi(h_zeta, Cm1=5.0, Cm2=-16.0)) * 10)
        npt.assert_array_equal(WS.sel(wd=180, ws=12), (np.log(h_lst / 2) - psi(h_lst * L_inv, Cm1=5.0, Cm2=-16.0)) / (np.log(70.0 / 2) - psi(h_zeta, Cm1=5.0, Cm2=-16.0)) * 12)


def test_log_shear():

    h_lst = np.arange(10, 100, 10)
    site = UniformSite([1], .1, shear=LogShear(70, z0=[.02, 2]))
    WS = site.local_wind(x=h_lst * 0, y=h_lst * 0, h=h_lst, wd=[0, 180], ws=[10, 12]).WS

    if 0:
        plt.plot(WS.sel(wd=0, ws=10), h_lst, label='z0=0.02')
        plt.plot(np.log(h_lst / 0.02) / np.log(70 / 0.02) * 10, h_lst, ':')
        plt.plot(WS.sel(wd=180, ws=12), h_lst, label='z0=2')
        plt.plot(np.log(h_lst / 2) / np.log(70 / 2) * 12, h_lst, ':')
        plt.legend()
        plt.show()
    npt.assert_array_equal(WS.sel(wd=0, ws=10), np.log(h_lst / 0.02) / np.log(70 / 0.02) * 10)
    npt.assert_array_equal(WS.sel(wd=180, ws=12), np.log(h_lst / 2) / np.log(70 / 2) * 12)


def test_log_shear_constant_z0():
    h_lst = np.arange(10, 100, 10)
    site = UniformSite([1], .1, shear=LogShear(70, z0=.02))
    WS = site.local_wind(x=h_lst * 0, y=h_lst * 0, h=h_lst, wd=[0, 180], ws=[10, 12, 13]).WS

    if 0:
        plt.plot(WS.sel(ws=10), WS.h, label='z0=0.02')
        plt.plot(np.log(h_lst / 0.02) / np.log(70 / 0.02) * 10, h_lst, ':')
        plt.legend()
        plt.show()
    npt.assert_array_equal(WS.sel(ws=10), np.log(h_lst / 0.02) / np.log(70 / 0.02) * 10)


def test_custom_shear():
    def my_shear(localWind, WS, h):
        return WS * (0.02 * (h[:, na, na] - 70) + 1) * (localWind.wd[na, :, na] * 0 + 1)
    h_lst = np.arange(10, 100, 10)

    site = UniformSite([1], .1, shear=my_shear)
    WS = site.local_wind(x=h_lst * 0, y=h_lst * 0, h=h_lst, wd=[0, 180], ws=[10, 12]).WS

    if 0:
        plt.plot(WS.sel(wd=0, ws=10), WS.h, label='2z-2')
        plt.plot((h_lst - 70) * 0.2 + 10, h_lst, ':')
        plt.legend()
        plt.show()
    npt.assert_array_almost_equal(WS.sel(wd=0, ws=10), (h_lst - 70) * 0.2 + 10)


if __name__ == '__main__':
    test_power_shear()
