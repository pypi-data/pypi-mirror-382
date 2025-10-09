import xarray as xr
from py_wake import np
from numpy import newaxis as na
from scipy.interpolate._interpolate import interp1d
from py_wake.rotor_avg_models.rotor_avg_model import EllipSysPolygonRotorAvg
import os
from pathlib import Path
from py_wake.utils.most import phi, psi, phi_eps


class RANSLUTModel():

    def get_lut(self, lut, varname):
        if isinstance(lut, (str, Path)):
            lut = xr.load_dataset(lut)
        if isinstance(lut, xr.Dataset):
            lut = lut[varname]
        return lut

    def get_input(self, dw_ijlk, hcw_ijlk, z_ijlk, D_src_il, h_ilk, TI_eff_ilk, ct_ilk, type_il, **kwargs):
        kwargs = dict(x=dw_ijlk / D_src_il[:, na, :, na],
                      y=hcw_ijlk / D_src_il[:, na, :, na],
                      z=(z_ijlk - h_ilk[:, na]) / D_src_il[:, na, :, na],
                      ti=TI_eff_ilk[:, na],
                      ct=ct_ilk[:, na],
                      type_i=type_il[:, na, :, na])

        return [kwargs[k] for k in self.da_lst[0].dims]


class ADControl():
    def __init__(self, UAD_CTstar_CPstar_lst, generate_args=None):
        self.U_CT_CP_AD = UAD_CTstar_CPstar_lst
        self.generate_args = generate_args
        self.fint_CTstar = []
        self.fint_CPstar = []
        for UAD, CTstar, CPstar in UAD_CTstar_CPstar_lst:
            assert len(UAD) == len(CTstar) == len(CPstar)
            self.fint_CPstar.append(interp1d(UAD, CPstar, fill_value=0.0, bounds_error=False))
            self.fint_CTstar.append(interp1d(UAD, CTstar, fill_value=0.0, bounds_error=False))

    @staticmethod
    def from_files(ADcontrolfiles):
        # RANS based calibrated control file for CPstar and CTstar as function of
        # the disk averaged velocity UAD provided by the user
        UAD_CTstar_CPstar_lst = [np.genfromtxt(ADcontrolfile, skip_header=True).T[:3]
                                 for ADcontrolfile in ADcontrolfiles]
        return ADControl(UAD_CTstar_CPstar_lst)

    def save(self, folder='.'):
        assert self.generate_args is not None
        windTurbines, cal_TI, ws_lst = self.generate_args

        for type_, U_CT_CP_AD in enumerate(self.U_CT_CP_AD):
            Dref = windTurbines.diameter(type_)
            cal_TI = cal_TI
            ws = ws_lst[type_]
            outfile = os.path.join(folder, 'lutcal_WT%g_Ti%g_%i.dat' % (Dref, cal_TI, type_))
            with open(outfile, 'w') as f:
                f.write('%s %s\n' % (str(ws.size + 2), ' 4'))
                # f.write('%16.14f %16.14f %16.14f %16.14f\n' %
                #        (0.95 * U_CT_CP_AD[0, 0], U_CT_CP_AD[0, 1], U_CT_CP_AD[0, 2], 0.95 * ws[0]))
                for (U, CT, CP), ws_ in zip(U_CT_CP_AD.T, ws):
                    f.write('%16.14f %16.14f %16.14f %16.14f\n' % (U, CT, CP, ws_))
                # f.write('%16.14f %16.14f %16.14f %16.14f\n' % (ws[-1], 0.0, 0.0, ws[-1]))

    @staticmethod
    def from_lut(lut, windTurbines, ws_cutin, ws_cutout, dws, cal_TI, cal_zeta=0.0,
                 rotorAvgModel=EllipSysPolygonRotorAvg(n_r=9, n_theta=32),
                 density=1.225, cmu=0.03, kappa=0.4, Cm1=5.0, Cm2=-16.0):
        """Calculcate ADControl object containing CPstar, CTstar = f(UAD) directly from single wake RANS-LUT


        Parameters
        ----------
        deficit_lut : xarray.DataArray
            Dataset or DataArray containing deficits or list of Datasets/DataArray (one for each wt type)
        windTurbines : WindTurbines object

        ws_cutin : list
            List of cutin wind speeds with length equal to number of different wts,
            only used to when ADcontrolfiles is None.
        ws_cutin : list
            List of cutin wind speeds with length equal to number of different wts,
            only used to when ADcontrolfiles is None.
        dws : float
            Wind speed interval for lut calculated CTstar, CPstar = f(U_AD) relationship,
            only used to when ADcontrolfiles is None.
        cal_TI : float
            Reference Ti value to calculate shear for CTstar, CPstar = f(U_AD) relationship,
            only used to when ADcontrolfiles is None.
        rotorAvgModel : RotorAvgModel, optional
            rotorAvgModel used to sample UAD
        """
        if not isinstance(lut, (list, tuple)):
            lut = [lut]
        lut_lst = lut

        def get_lut_U(lut):
            if isinstance(lut, xr.Dataset):
                lut = lut.deficits
            return 1 - lut.interp(x=0, ti=cal_TI)
        lut_U = [get_lut_U(lut) for lut in lut_lst]
        weights = rotorAvgModel.nodes_weight[na, :]

        phim = phi(cal_zeta, Cm1=Cm1, Cm2=Cm2)
        psim = psi(cal_zeta, Cm1=Cm1, Cm2=Cm2)
        phieps = phi_eps(cal_zeta, Cm1=Cm1)
        uStar_UH = cal_TI * np.sqrt(1.5 * np.sqrt(cmu)) * phieps ** -0.25 * phim ** 0.25

        types = np.arange(len(lut_U))
        ws_cutin, ws_cutout = np.zeros(len(types)) + ws_cutin, np.zeros(len(types)) + ws_cutout
        ws_lst = [np.r_[ws_cutin[t],  # below cut-in interpolation point
                        np.arange(ws_cutin[t], ws_cutout[t] + dws, dws),
                        ws_cutout[t]  # cut-out interpolation point
                        ] for t in types]

        def get_UAD_CTstar_CPstar(type):
            if 'type' in windTurbines.powerCtFunction.required_inputs:
                _kwargs = {'type': type}
            else:
                _kwargs = {}

            Dref = windTurbines.diameter(type)
            zH = windTurbines.hub_height(type)

            y_j = rotorAvgModel.nodes_x / 2
            z_j = rotorAvgModel.nodes_y / 2
            h_j = z_j * Dref + zH
            Udata = lut_U[type].interp(y=('i', y_j), z=('i', z_j))
            ws = ws_lst[type]
            cts = windTurbines.ct(ws=ws, **_kwargs)
            cps = (windTurbines.power(ws=ws, **_kwargs) / (0.125 * density * Dref ** 2 * np.pi * ws ** 3))

            # PWE: z0 is added to h_j and zH
            z0 = zH / (np.exp(kappa / uStar_UH + psim) - 1)
            L_inv = cal_zeta / zH  # 1 / Obukhov length
            mostshear = (np.log(h_j / z0) - psi(h_j * L_inv, Cm1=Cm1, Cm2=Cm2)) / (np.log(zH / z0) - psim)
            U = mostshear[na, :] - 1.0 + Udata.interp(ct=cts, kwargs={"fill_value": "extrapolate"}).values
            UAD = ws * np.sum(np.reshape(U, (len(ws), -1)) * weights, axis=1)
            ratio = ws / UAD
            UAD_CTstar_CPstar = np.array([UAD, cts * ratio ** 2, cps * ratio ** 3])
            UAD_CTstar_CPstar[0, 0] = 0.95 * UAD[1]
            UAD_CTstar_CPstar[:, -1] = ws[-1], 0.0, 0.0

            return UAD_CTstar_CPstar
        return ADControl([get_UAD_CTstar_CPstar(t) for t in types], (windTurbines, cal_TI, ws_lst))


def get_Ellipsys_equivalent_output(sim_res, aDControl, flowmap_maxpoints=None,
                                   rotorAvgModel=EllipSysPolygonRotorAvg(n_r=9, n_theta=32)):
    """
    Recalculate wt power and thrust by the integrating rotor averaged wind speed
    including induction and interpolation with a CPstar, CTstar = f(U_AD) relation,
    as done in EllipSys. flow_map is used to interpolate the integration points;
    this method requires a lot of memory when many points are extracted at the same time in
    combination with a large wind farm. The variable flowmap_maxpoints can be used to reduce
    the number of points per flow_map call for the cost of computational speed.


    power_as_RANS : bool
            If True, the turbine power is calculated as a post step following
            a RANS approach using CPstar = CPstar * (U_inf / U_AD) ** 3 = func(U_AD),
            where UAD a rotor averaged wind speed including the turbine induction
            In addition, an alternative thrust coefficient is calculated
            CTstar = CT * (U_inf / U_AD) ** 2 = func(U_AD).

    flowmap_maxpoints: int
            Maximum number of interpolation points during post turbine step
            to reduce memomry usage

    """

    power_ilk_org = sim_res.Power.values
    wts = sim_res.windFarmModel.windTurbines

    type_i = sim_res.type.values
    uniquetypes = np.sort(np.unique(type_i))

    # Calculate ad integration parameters
    weights = rotorAvgModel.nodes_weight[na, :, na]
    nr = rotorAvgModel.n_rnodes
    ntheta = rotorAvgModel.n_theta
    shape = sim_res.WS_eff_ilk.shape
    I, L, K = shape

    pos = np.array([sim_res.x, sim_res.y, sim_res.h])
    theta_wd = np.deg2rad(270.0 - sim_res.wd).values

    o3_l = np.array([np.cos(theta_wd), np.sin(theta_wd), theta_wd * 0])
    o2 = np.array([0.0, 0.0, 1.0])  # rotor center to rotor top
    D_i = sim_res.windFarmModel.windTurbines.diameter(type_i)
    nx_in, ny_in, nz_in = np.array([rotorAvgModel.nodes_y * 0,
                                    rotorAvgModel.nodes_x,
                                    rotorAvgModel.nodes_y])[:, na] * .5 * D_i[na, :, na]
    power_ilk = np.zeros(shape)
    ct_star_ilk = np.zeros(shape)
    Cnsts = 0.5 * 1.225 * D_i ** 2 * 0.25 * np.pi
    flowmap_maxpoints = flowmap_maxpoints or I * ntheta * nr

    # Loop over wind directions because flow_map cannot include interpolation points (x_j, y_j, h_j) vectorized over wds
    # since they change orientation per wind direction

    def get_WS_eff_ik(l):
        # project rotorAvgModel node positions to plane perpendicular to current wind direction
        o3 = o3_l[:, l]
        o1 = np.cross(o2, o3)
        cxyzg_xij = nx_in[na] * o3[:, na, na] + ny_in[na] * o1[:, na, na] + nz_in[na] * o2[:, na, na] + pos[:, :, na]
        cxyzg_xj = cxyzg_xij.reshape((3, -1))
        J = cxyzg_xj.shape[1]

        nflowmaps = int(np.ceil(J / flowmap_maxpoints))
        sim_res_wd = sim_res.isel(wd=l)
        for k in sim_res.__slots__:
            setattr(sim_res_wd, k, getattr(sim_res, k))
        WS_eff_jlk = np.concatenate([sim_res.windFarmModel._flow_map(*pos_j.T, sim_res_wd)[1]
                                     for pos_j in np.array_split(cxyzg_xj.T, nflowmaps)])

        # Integrate U over AD
        return np.sum(np.reshape(WS_eff_jlk, (I, ntheta * (nr - 1), K)) * weights, axis=1)
    WS_eff_star_ilk = np.concatenate([get_WS_eff_ik(l)[:, na] for l in range(L)], 1)

    U_tab_lst = [U_CT_CP_AD[0, :] for U_CT_CP_AD in aDControl.U_CT_CP_AD]

    Prated = [wts.power(U_tab,
                        **{k: t for k in ['type']
                           if k in wts.powerCtFunction.required_inputs + wts.powerCtFunction.optional_inputs}).max()
              for t, U_tab in enumerate(U_tab_lst)]
    Prated_i = np.array([Prated[t] for t in type_i])

    def get_cp_ct_power(i, t):
        WS_eff_star_1lk = WS_eff_star_ilk[i]
        cp_star = aDControl.fint_CPstar[t](WS_eff_star_1lk)
        ct_star = aDControl.fint_CTstar[t](WS_eff_star_1lk)
        power = cp_star * Cnsts[i, na, na] * WS_eff_star_1lk ** 3
        return ct_star, power

    if np.all(type_i == 0):
        ct_star_ilk, power_ilk = map(np.array, get_cp_ct_power(slice(None), 0))
    else:
        ct_star_ilk, power_ilk = map(np.array, zip(*[get_cp_ct_power(i, type_i[i]) for i in range(I)]))

    power_ilk = np.minimum(power_ilk, Prated_i[:, na, na])

    # Set power and ct to zero for wts that were originally shut down
    operating = power_ilk_org > 0
    ct_star_ilk *= operating
    power_ilk *= operating
    # print('power_ilk', power_ilk, 'WS_eff_star_ilk', WS_eff_star_ilk)
    return power_ilk, WS_eff_star_ilk, ct_star_ilk
