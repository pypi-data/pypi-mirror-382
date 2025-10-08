"""Maximum allowable annulus surface pressure (MAASP) calculator."""

from gemini_model.model_abstract import Model


class AnnulusPressure(Model):
    """Calculate MAASP from equivalent mud weight and geometry."""

    def __init__(self):
        """Model initialization."""
        self.parameters = {}
        self.output = {}

    def update_parameters(self, parameters):
        """To update model parameters.

        Parameters
        ----------
        parameters: dict
            parameters dict as defined by the model
        """
        for key, value in parameters.items():
            self.parameters[key] = value

    def initialize_state(self, x):
        """Generate an initial state based on user parameters."""
        pass

    def update_state(self, u, x):
        """Update the state based on input u and state x."""
        pass

    def calculate_output(self, u, x):
        """Calculate output based on input u and state x."""
        # get input
        EMW = self.parameters['EMW']
        RKB = self.parameters['RKB']
        SCS = self.parameters['SCS']

        # calculate model
        MAASP = self._calculate_MAASP(EMW, RKB, SCS)

        # write output
        self.output['MAASP'] = MAASP

    def get_output(self):
        """Get output of the model."""
        return self.output

    def _calculate_MAASP(self, EMW, RKB, SCS):
        """Calculate MAASP.

        Parameters
        ----------
        EMW: float
            Equivalent Mud Weight (kg/m3)
        RKB: float
            RKB Tubing Hanger (m TVD)
        SCS: float
            Surface Casing Shoe (m)
        """
        # convert from m to ft
        RKB = RKB * 3.28084
        SCS = SCS * 3.28084

        # convert from kg/m3 to ppg
        EMW = EMW / 119.82643

        # MAASP using formula in psi
        MAASP = (EMW * SCS * 0.052) - (8.6 * 0.052 * (SCS - RKB))

        # convert from psi to bar
        MAASP = MAASP * 0.0689476

        return MAASP
