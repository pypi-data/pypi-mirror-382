"""CO2 corrosion meta-model (optimized implementations).

This module is similar to ``co2_corrosion`` but dispatches to optimized
implementations under ``correlations_opt``. The public behavior is the same:
set ``parameters['corrosion_model']`` to one of ``'DLD'``, ``'DLM'``, or
``'NORSOK'`` and call :meth:`calculate_output` to obtain the corrosion rate.
"""

from gemini_model.model_abstract import Model
from gemini_model.corrosion.correlations_opt.dld_model_opt import DLD
from gemini_model.corrosion.correlations_opt.dlm_model_opt import DLM
from gemini_model.corrosion.correlations_opt.norsok_model_opt import NORSOK


class CO2CorrosionOpt(Model):
    """CO2 corrosion rate model using optimized correlation implementations."""

    def __init__(self):
        """Initialize CO2 corrosion optimization model."""
        self.parameters = {}
        self.output = {}

    def update_parameters(self, parameters):
        """Update model parameters.

        Parameters
        ----------
        parameters: dict
            Parameters dict as defined by the model.
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
        self.output = self.calculate_corrosion_rate(u, x)

    def get_output(self):
        """Get output of the model."""
        return self.output

    def calculate_corrosion_rate(self, u, x):
        """Calculate the corrosion rate."""
        model = self.parameters['corrosion_model']

        if model == 'DLD':
            corrosion_model = DLD()
        elif model == "DLM":
            corrosion_model = DLM()
        elif model == 'NORSOK':
            corrosion_model = NORSOK()

        corrosion_model.update_parameters(self.parameters)
        corrosion_model.calculate_output(u, x)
        return corrosion_model.get_output()
