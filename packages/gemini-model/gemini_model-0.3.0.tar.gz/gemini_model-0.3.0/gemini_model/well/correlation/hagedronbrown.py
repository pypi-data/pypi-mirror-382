"""Hagedorn–Brown two-phase pressure drop correlation using digitized figures.

Hagedoorn and Brown, reference: [Brill, Mukherjee "Multiphase flow in wells] p 29, equation 4.2;
acceleration is ignored.
"""

import os
import scipy.io
import numpy as np
from scipy.interpolate import interp1d


class HagedornBrown:
    """Calculate two-phase dp via Hagedorn–Brown (per Brill & Mukherjee, Eq. 4.2)."""

    @staticmethod
    def calculate_dp(us_g, us_l, rho_g, rho_l, theta, eta_g,
                     eta_l, sigma, d_tube, Krough, l_cel, pressure):
        """Calculate pressure drop based on the publication.

        [Brill, Mukherjee "Multiphase flow in wells] p 29 equation 4.2; acceleration is ignored.

        Parameters
        ----------
        us_g: float
            superficial gas flow velocity (m/s)
        us_l: float
            superficial liquid flow velocity (m/s)
        rho_g: float
            gas density (kg/m3)
        rho_l: float
            liquid density (kg/m3)
        theta: float
            Inclination of 1 cell (rad)
        eta_g: float
            gas viscosity (Pa s)
        eta_l: float
            liquid vicosity (Pa s)
        sigma: float
            surface tension (N/m)
        d_tube: float
            well diamater of 1 cell (m)
        Krough: float
            roughness of 1 cell (m)
        l_cel: float
            length of 1 cell (m)

        Returns
        --------
        dp_fric: float
            pressure drop due to friction (Pa)
        dp_grav: float
            pressure drop due to gravity (Pa)
        """
        # Load the .mat file

        HB_figs = os.path.join(os.getcwd(), 'gemini_model', 'well', 'correlation', 'HB_figs.mat')
        mat_data = scipy.io.loadmat(HB_figs)

        # Extract the data arrays
        HB_fig42 = mat_data['HB_fig42']
        HB_fig43 = mat_data['HB_fig43']
        HB_fig44 = mat_data['HB_fig44']

        # preprocessing input parameters
        um = us_l + us_g
        Ll = us_l / um
        rhon = Ll * rho_l + (1 - Ll) * rho_g

        g = 9.81  # gravitational constant [m/s2]

        # Conversion input parameters to oil field
        us_g_o = us_g / 3.048e-1  # m/s -> ft/s
        us_l_o = us_l / 3.048e-1  # m/s -> ft/s
        # rho_g_o = rho_g / 1.601846e1  # kg/m3 -> lbm/ft3
        rho_l_o = rho_l / 1.601846e1  # kg/m3 -> lbm/ft3
        eta_l_o = eta_l / 1e-3  # Pa s -> cp
        sigma_o = sigma / 1e-3  # N/m -> dyne/cm
        d_tube_o = d_tube / 3.048e-1  # m -> ft

        # preprocessing input parameters
        Nlv = 1.938 * us_l_o * (rho_l_o / sigma_o) ** 0.25
        Ngv = 1.938 * us_g_o * (rho_l_o / sigma_o) ** 0.25
        Nd = 120.872 * d_tube_o * np.sqrt(rho_l_o / sigma_o)
        Nl = 0.15726 * eta_l_o * (1 / (rho_l_o * sigma_o ** 3)) ** 0.25

        # Get NLC from HB_fig43
        if Nl < HB_fig43[:, 0].all():
            NLC = HB_fig43[0, 1]
        elif Nl > HB_fig43[:, 0].all():
            NLC = HB_fig43[-1, 1]
        else:
            NLC = interp1d(HB_fig43[:, 0], HB_fig43[:, 1])(Nl)

        # Calculate phi from HB_fig44
        par1 = (Ngv * Nl ** 0.380) / (Nd ** 2.14)
        if par1 < HB_fig44[:, 0].all():
            phi = HB_fig44[0, 1]
        elif par1 > HB_fig44[:, 0]:
            phi = HB_fig44[-1, 1]
        else:
            phi = interp1d(HB_fig44[:, 0], HB_fig44[:, 1])(par1)

        # Calculate Hl_phi from HB_fig42
        par2 = (NLC / Nd) * (Nlv / (Ngv ** 0.575)) * ((pressure / 101325) ** 0.1)
        if par2 < HB_fig42[:, 0].all():
            Hl_phi = HB_fig42[0, 1]
        elif par2 > HB_fig42[:, 0].all():
            Hl_phi = HB_fig42[-1, 1]
        else:
            Hl_phi = interp1d(HB_fig42[:, 0], HB_fig42[:, 1])(par2)

        if Nlv == 0:
            Hl_phi = 0

        # Calculate Hl and adjust if necessary
        Hl = Hl_phi * phi
        if Hl < Ll:
            Hl = Ll

        # Calculate slip density and Reynolds number
        rhos = Hl * rho_l + (1 - Hl) * rho_g
        etam = eta_l ** Hl * eta_g ** (1 - Hl)
        Rem = um * rhon * d_tube / etam

        # Calculate friction factor using the Colebrook-White equation
        lambdam = (-0.8685 * np.log((
            1.964 * np.log(abs(Rem)) - 3.8215) / abs(Rem) + Krough / (d_tube * 3.71))) ** (-2)

        # Determine pressure drops
        dp_fric = lambdam * (0.5 * rhon ** 2 * um * abs(um)) * l_cel / (rhos * d_tube)
        dp_grav = rhos * g * l_cel * np.sin(theta)

        return dp_fric, dp_grav
