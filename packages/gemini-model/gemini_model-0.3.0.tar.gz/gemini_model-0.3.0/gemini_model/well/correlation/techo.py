"""Techo single-phase friction factor correlation (Darcy–Weisbach).

The friction coefficient proposed in the publication:
"R. Techo, RR. Tickner, R.E. James, An Accurate Equation
for the Computation of the Friction Factor for
Smooth Pipes from the Reynolds Number, Journal of Applied Mechanics, Vol.32, p.443, 1965."
"""

import math


class Techo:
    """Single-phase dp using Darcy–Weisbach with Techo friction correlation."""

    @staticmethod
    def calculate_dp(us_l, rho_l, theta, eta_l, d_tube, K, l_cel):
        """Calculate single phase pressure drop using Techo correlation.

        Parameters
        ----------
        us_l : float
            superficial liquid flow velocity (m/s)
        rho_l : float
            liquid density (kg/m3)
        theta : float
            Inclination of 1 cell (rad)
        eta_l : float
            liquid vicosity (Pa s)
        d_tube : float
            well diameter of 1 cell (m)
        K : float
            roughness of 1 cell (m)
        l_cel : float
            length of 1 cell (m)

        Returns
        -------
        dp_fric: float
            pressure drop due to friction (Pa)
        dp_grav: float
            pressure drop due to gravity (Pa)
        """
        # constants
        g = 9.81  # acceleration due to gravity (m/s2)

        # friction
        Rem = abs(us_l) * rho_l * d_tube / eta_l
        lambdam = (-0.8685 * math.log(
            (1.964 * math.log(Rem) - 3.8215) / Rem + (K / (d_tube * 3.71)))) ** (-2)

        # friction
        dp_fric = (0.5 * rho_l * us_l * abs(us_l)) * lambdam * l_cel / d_tube
        # gravity
        dp_grav = rho_l * g * l_cel * math.sin(theta)

        return dp_fric, dp_grav
