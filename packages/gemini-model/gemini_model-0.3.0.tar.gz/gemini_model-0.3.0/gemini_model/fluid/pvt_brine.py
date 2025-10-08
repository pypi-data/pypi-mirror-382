"""Brine PVT correlations (Batzle and Wang, 1992).

Provides density and viscosity estimates for brine as a function of pressure,
temperature, and salinity using empirical relationships.
"""

import numpy as np


class PVTConstantPTS:
    """Brine PVT model using Batzle–Wang correlations."""

    def __init__(self):
        """Initialize PVT brine model."""
        self.parameters = {}

        self.parameters['temperature_max'] = None  # 250 C
        self.parameters['RHOL'] = 1000  # H2O Liquid density (kg/m3)
        self.parameters['VISL'] = 1e-3  # H2O viscosity (Pa.s)

    def update_parameters(self, parameters):
        """Update model parameters.

        Parameters
        ----------
        parameters: dict
            Parameters dict as defined by the model.
        """
        for key, value in parameters.items():
            self.parameters[key] = value

    def cal_pvt_brine(self, P_input, T_input, S_input):
        """Compute brine density and viscosity using Batzle–Wang (1992)."""
        P = P_input * 1e-6  # Pa to MPa
        T = T_input - 273.15  # K to C
        S = S_input  # ppm

        rho_water = (1 + 1 * 1e-6 * (-80 * T - 3.3 * T ** 2 + 0.00175 * T ** 3 +
                                     489 * P - 2 * T * P + 0.016 * T ** 2 * P -
                                     1.3 * 1e-5 * T ** 3 * P - 0.333 * P ** 2 -
                                     0.002 * T * P ** 2)) * 1e3  # g/cm3 to kg/m3

        self.parameters['RHOL'] = rho_water + (
            S * (0.668 + 0.44 * S + 1e-6 * (300 * P - 2400 * P * S + T * (
                80 + 3 * T - 3300 * S - 13 * P + 47 * P * S)))) * 1e3

        self.parameters['VISL'] = 0.1 + 0.333 * S + (1.65 + 91.9 * S ** 3) * np.exp(
            - (0.42 * (S ** 0.8 - 0.17) ** 2 + 0.045) * T ** 0.8)

    def get_pvt_brine(self, P, T, S):
        """Calculate the PVT parameters based on pressure and temperature.

        Parameters
        ----------
        P : float
            Pressure (Pa).
        T : float
            Temperature (K).
        S : float
            Salinity (ppm).

        Returns
        -------
        rho_l : float
            Liquid density (kg/m3).
        eta_l : float
            Viscosity liquid (Pa.s).
        """
        self.cal_pvt_brine(P, T, S)

        rho_l = self.parameters['RHOL']  # density liquid (kg/m3)
        eta_l = self.parameters['VISL']  # viscosity liquid (Pa.s)

        return rho_l, eta_l
