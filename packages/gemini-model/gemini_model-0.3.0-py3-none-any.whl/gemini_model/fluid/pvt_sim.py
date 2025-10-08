"""Tabulated PVT (PVTsim .tab) loader and interpolator.

Reads PVT tables exported from PVTsim (KEY format) and provides 2D
interpolators over pressure and temperature for common properties.
"""

import numpy as np
from scipy import interpolate


class PVT:
    """PVT table model with interpolation over P and T."""

    def __init__(self):
        """Initialize PVT simulation model."""
        self.parameters = {}
        self.parameters['pressure_max'] = None
        self.parameters['pressure_min'] = None
        self.parameters['temperature_max'] = None
        self.parameters['temperature_min'] = None

    def update_parameters(self, parameters):
        """Update model parameters.

        Parameters
        ----------
        parameters: dict
            Parameters dict as defined by the model.
        """
        for key, value in parameters.items():
            self.parameters[key] = value

    def load_pvt_tables(self, pvt_file):
        """Load a PVTsim .tab file generated using the table format KEY."""
        f = open(pvt_file, "r")
        tlines = f.readlines()

        kk = 1
        nP = int(tlines[kk].split()[0])
        nT = int(tlines[kk].split()[1])

        PT = []
        while len(PT) < nP:
            kk += 1
            PT.extend(tlines[kk].split())
        PT = [float(x) for x in PT]
        self.PT = np.array(PT)

        TM = []
        while len(TM) < nT:
            kk += 1
            TM.extend(tlines[kk].split())
        TM = [float(x) for x in TM]
        self.TM = np.array(TM)

        spare = []
        while len(spare) < 2 * nT:
            kk += 1
            spare.extend(tlines[kk].split())

        # GAS DENSITY (KG/M3)
        kk += 1
        # print(tlines[kk])
        RHOG = []
        while len(RHOG) < nP * nT:
            kk += 1
            RHOG.extend(tlines[kk].split())
        RHOG = [float(x) for x in RHOG]
        self.RHOG = np.array(RHOG)
        self.RHOG = self.RHOG.reshape(nP, nT)

        # LIQUID DENSITY (KG/M3)
        kk += 1
        # print(tlines[kk])
        RHOL = []
        while len(RHOL) < nP * nT:
            kk += 1
            RHOL.extend(tlines[kk].split())
        RHOL = [float(x) for x in RHOL]
        self.RHOL = np.array(RHOL)
        self.RHOL = self.RHOL.reshape(nP, nT)

        # WATER DENSITY (KG/M3)
        kk += 1
        # print(tlines[kk])
        RHOW = []
        while len(RHOW) < nP * nT:
            kk += 1
            RHOW.extend(tlines[kk].split())
        RHOW = [float(x) for x in RHOW]
        self.RHOW = np.array(RHOW)
        self.RHOW = self.RHOW.reshape(nP, nT)

        # PRES. DERIV. OF GAS DENS.
        kk += 1
        # print(tlines[kk])
        RHOGP = []
        while len(RHOGP) < nP * nT:
            kk += 1
            RHOGP.extend(tlines[kk].split())
        RHOGP = [float(x) for x in RHOGP]
        self.RHOGP = np.array(RHOGP)
        self.RHOGP = self.RHOGP.reshape(nP, nT)

        # PRES. DERIV. OF LIQUID DENS.
        kk += 1
        # print(tlines[kk])
        RHOLP = []
        while len(RHOLP) < nP * nT:
            kk += 1
            RHOLP.extend(tlines[kk].split())
        RHOLP = [float(x) for x in RHOLP]
        self.RHOLP = np.array(RHOLP)
        self.RHOLP = self.RHOLP.reshape(nP, nT)

        # PRES. DERIV. OF WATER DENS.
        kk += 1
        # print(tlines[kk])
        RHOWP = []
        while len(RHOWP) < nP * nT:
            kk += 1
            RHOWP.extend(tlines[kk].split())
        RHOWP = [float(x) for x in RHOWP]
        self.RHOWP = np.array(RHOWP)
        self.RHOWP = self.RHOWP.reshape(nP, nT)

        # TEMP. DERIV. OF GAS DENS.
        kk += 1
        # print(tlines[kk])
        RHOGT = []
        while len(RHOGT) < nP * nT:
            kk += 1
            RHOGT.extend(tlines[kk].split())
        RHOGT = [float(x) for x in RHOGT]
        self.RHOGT = np.array(RHOGT)
        self.RHOGT = self.RHOGT.reshape(nP, nT)

        # TEMP. DERIV. OF LIQUID DENS.
        kk += 1
        # print(tlines[kk])
        RHOLT = []
        while len(RHOLT) < nP * nT:
            kk += 1
            RHOLT.extend(tlines[kk].split())
        RHOLT = [float(x) for x in RHOLT]
        self.RHOLT = np.array(RHOLT)
        self.RHOLT = self.RHOLT.reshape(nP, nT)

        # TEMP. DERIV. OF WATER DENS.
        kk += 1
        # print(tlines[kk])
        RHOWT = []
        while len(RHOWT) < nP * nT:
            kk += 1
            RHOWT.extend(tlines[kk].split())
        RHOWT = [float(x) for x in RHOWT]
        self.RHOWT = np.array(RHOWT)
        self.RHOWT = self.RHOWT.reshape(nP, nT)

        # GAS MASS FRACTION OF GAS + OIL
        kk += 1
        # print(tlines[kk])
        GMF = []
        while len(GMF) < nP * nT:
            kk += 1
            GMF.extend(tlines[kk].split())
        GMF = [float(x) for x in GMF]
        self.GMF = np.array(GMF)
        self.GMF = self.GMF.reshape(nP, nT)

        # WATER MASS FRACTION OF GAS + OIL
        kk += 1
        # print(tlines[kk])
        WMF = []
        while len(WMF) < nP * nT:
            kk += 1
            WMF.extend(tlines[kk].split())
        WMF = [float(x) for x in WMF]
        self.WMF = np.array(WMF)
        self.WMF = self.WMF.reshape(nP, nT)

        # GAS VISCOSITY (N S/M2)
        kk += 1
        # print(tlines[kk])
        VISG = []
        while len(VISG) < nP * nT:
            kk += 1
            VISG.extend(tlines[kk].split())
        VISG = [float(x) for x in VISG]
        self.VISG = np.array(VISG)
        self.VISG = self.VISG.reshape(nP, nT)

        # LIQUID VISCOSITY (N S/M2)
        kk += 1
        # print(tlines[kk])
        VISL = []
        while len(VISL) < nP * nT:
            kk += 1
            VISL.extend(tlines[kk].split())
        VISL = [float(x) for x in VISL]
        self.VISL = np.array(VISL)
        self.VISL = self.VISL.reshape(nP, nT)

        # WATER VISCOSITY (N S/M2)
        kk += 1
        # print(tlines[kk])
        VISW = []
        while len(VISW) < nP * nT:
            kk += 1
            VISW.extend(tlines[kk].split())
        VISW = [float(x) for x in VISW]
        self.VISW = np.array(VISW)
        self.VISW = self.VISW.reshape(nP, nT)

        # GAS SPECIFIC HEAT (J/KG K)
        kk += 1
        # print(tlines[kk])
        CPG = []
        while len(CPG) < nP * nT:
            kk += 1
            CPG.extend(tlines[kk].split())
        CPG = [float(x) for x in CPG]
        self.CPG = np.array(CPG)
        self.CPG = self.CPG.reshape(nP, nT)

        # LIQUID SPECIFIC HEAT (J/KG K)
        kk += 1
        # print(tlines[kk])
        CPL = []
        while len(CPL) < nP * nT:
            kk += 1
            CPL.extend(tlines[kk].split())
        CPL = [float(x) for x in CPL]
        self.CPL = np.array(CPL)
        self.CPL = self.CPL.reshape(nP, nT)

        # WATER SPECIFIC HEAT (J/KG K)
        kk += 1
        # print(tlines[kk])
        CPW = []
        while len(CPW) < nP * nT:
            kk += 1
            CPW.extend(tlines[kk].split())
        CPW = [float(x) for x in CPW]
        self.CPW = np.array(CPW)
        self.CPW = self.CPW.reshape(nP, nT)

        # GAS ENTHALPY (J/KG)
        kk += 1
        # print(tlines[kk])
        HG = []
        while len(HG) < nP * nT:
            kk += 1
            HG.extend(tlines[kk].split())
        HG = [float(x) for x in HG]
        self.HG = np.array(HG)
        self.HG = self.HG.reshape(nP, nT)

        # LIQUID ENTHALPY (J/KG)
        kk += 1
        # print(tlines[kk])
        HL = []
        while len(HL) < nP * nT:
            kk += 1
            HL.extend(tlines[kk].split())
        HL = [float(x) for x in HL]
        self.HL = np.array(HL)
        self.HL = self.HL.reshape(nP, nT)

        # WATER ENTHALPY (J/KG)
        kk += 1
        # print(tlines[kk])
        HW = []
        while len(HW) < nP * nT:
            kk += 1
            HW.extend(tlines[kk].split())
        HW = [float(x) for x in HW]
        self.HW = np.array(HW)
        self.HW = self.HW.reshape(nP, nT)

        # GAS THERMAL COND. (W/M K)
        kk += 1
        # print(tlines[kk])
        TCG = []
        while len(TCG) < nP * nT:
            kk += 1
            TCG.extend(tlines[kk].split())
        TCG = [float(x) for x in TCG]
        self.TCG = np.array(TCG)
        self.TCG = self.TCG.reshape(nP, nT)

        # LIQUID THERMAL COND. (W/M K)
        kk += 1
        # print(tlines[kk])
        TCL = []
        while len(TCL) < nP * nT:
            kk += 1
            TCL.extend(tlines[kk].split())
        TCL = [float(x) for x in TCL]
        self.TCL = np.array(TCL)
        self.TCL = self.TCL.reshape(nP, nT)

        # WATER THERMAL COND. (W/M K)
        kk += 1
        # print(tlines[kk])
        TCW = []
        while len(TCW) < nP * nT:
            kk += 1
            TCW.extend(tlines[kk].split())
        TCW = [float(x) for x in TCW]
        self.TCW = np.array(TCW)
        self.TCW = self.TCW.reshape(nP, nT)

        # SURFACE TENSION GAS/OIL (N/M)
        kk += 1
        # print(tlines[kk])
        SIGMAGO = []
        while len(SIGMAGO) < nP * nT:
            kk += 1
            SIGMAGO.extend(tlines[kk].split())
        SIGMAGO = [float(x) for x in SIGMAGO]
        self.SIGMAGO = np.array(SIGMAGO)
        self.SIGMAGO = self.SIGMAGO.reshape(nP, nT)

        # SURFACE TENSION GAS/WATER (N/M)
        kk += 1
        # print(tlines[kk])
        SIGMAGW = []
        while len(SIGMAGW) < nP * nT:
            kk += 1
            SIGMAGW.extend(tlines[kk].split())
        SIGMAGW = [float(x) for x in SIGMAGW]
        self.SIGMAGW = np.array(SIGMAGW)
        self.SIGMAGW = self.SIGMAGW.reshape(nP, nT)

        # SURFACE TENSION WATER/OIL (N/M)
        kk += 1
        # print(tlines[kk])
        SIGMAWO = []
        while len(SIGMAWO) < nP * nT:
            kk += 1
            SIGMAWO.extend(tlines[kk].split())
        SIGMAWO = [float(x) for x in SIGMAWO]
        self.SIGMAWO = np.array(SIGMAWO)
        self.SIGMAWO = self.SIGMAWO.reshape(nP, nT)

        # GAS ENTROPY (J/KG/C)
        kk += 1
        # print(tlines[kk])
        SG = []
        while len(SG) < nP * nT:
            kk += 1
            SG.extend(tlines[kk].split())
        SG = [float(x) for x in SG]
        self.SG = np.array(SG)
        self.SG = self.SG.reshape(nP, nT)

        # LIQUID ENTROPY (J/KG/C)
        kk += 1
        # print(tlines[kk])
        SL = []
        while len(SL) < nP * nT:
            kk += 1
            SL.extend(tlines[kk].split())
        SL = [float(x) for x in SL]
        self.SL = np.array(SL)
        self.SL = self.SL.reshape(nP, nT)

        # WATER ENTROPY (J/KG/C)
        kk += 1
        # print(tlines[kk])
        SW = []
        while len(SW) < nP * nT:
            kk += 1
            SW.extend(tlines[kk].split())
        SW = [float(x) for x in SW]
        self.SW = np.array(SW)
        self.SW = self.SW.reshape(nP, nT)

        f.close()

        self.parameters['pressure_max'] = max(self.PT)
        self.parameters['pressure_min'] = min(self.PT)
        self.parameters['temperature_max'] = max(self.TM)
        self.parameters['temperature_min'] = min(self.TM)

        self.create_fit_fuction()

    def create_fit_fuction(self):
        """Create 2D interpolants for each PVT property."""
        self.f_RHOG = interpolate.interp2d(self.PT, self.TM, np.transpose(self.RHOG))
        self.f_VISG = interpolate.interp2d(self.PT, self.TM, np.transpose(self.VISG))
        self.f_RHOL = interpolate.interp2d(self.PT, self.TM, np.transpose(self.RHOL))
        self.f_RHOW = interpolate.interp2d(self.PT, self.TM, np.transpose(self.RHOW))
        self.f_SL = interpolate.interp2d(self.PT, self.TM, np.transpose(self.SL))
        self.f_SW = interpolate.interp2d(self.PT, self.TM, np.transpose(self.SW))
        self.f_VISL = interpolate.interp2d(self.PT, self.TM, np.transpose(self.VISL))
        self.f_VISW = interpolate.interp2d(self.PT, self.TM, np.transpose(self.VISW))
        self.f_GMF = interpolate.interp2d(self.PT, self.TM, np.transpose(self.GMF))
        self.f_CPG = interpolate.interp2d(self.PT, self.TM, np.transpose(self.CPG))
        self.f_CPL = interpolate.interp2d(self.PT, self.TM, np.transpose(self.CPL))
        self.f_TCG = interpolate.interp2d(self.PT, self.TM, np.transpose(self.TCG))
        self.f_TCL = interpolate.interp2d(self.PT, self.TM, np.transpose(self.TCL))
        self.f_SIGMAGW = interpolate.interp2d(self.PT, self.TM, np.transpose(self.SIGMAGW))

    def get_pvt(self, P, T):
        """Interpolate PVT properties at pressure P (Pa) and temperature T (K).

        Parameters
        ----------
        P : float
            Pressure (Pa).
        T : float
            Temperature (K).

        Returns
        -------
        rho_g : float
            Gas density (kg/m3).
        rho_l : float
            Liquid density (kg/m3).
        gmf : float
            Gas mass fraction (-).
        eta_g : float
            Viscosity gas (Pa.s).
        eta_l : float
            Viscosity liquid (Pa.s).
        cp_g : float
            Heat capacity gas (J/Kg/K).
        cp_l : float
            Heat capacity liquid (J/Kg/K).
        K_g : float
            Thermal conductivity gas (W/m/K).
        K_l : float
            Thermal conductivity liquid (W/m/K).
        sigma : float
            Surface tension (N/m).
        """
        rho_g = self.f_RHOG(P, T)
        rho_l = self.f_RHOL(P, T)
        gmf = self.f_GMF(P, T)
        eta_g = self.f_VISG(P, T)
        eta_l = self.f_VISL(P, T)
        cp_g = self.f_CPG(P, T)
        cp_l = self.f_CPL(P, T)
        K_g = self.f_TCG(P, T)
        K_l = self.f_TCL(P, T)
        sigma = self.f_SIGMAGW(P, T)

        return rho_g, rho_l, gmf, eta_g, eta_l, cp_g, cp_l, K_g, K_l, sigma
