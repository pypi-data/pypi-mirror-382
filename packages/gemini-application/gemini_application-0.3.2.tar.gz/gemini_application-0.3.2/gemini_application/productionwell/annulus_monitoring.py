"""Production well annulus pressure monitoring application."""

from gemini_application.application_abstract import ApplicationAbstract
from gemini_model.well.annulus_pressure import AnnulusPressure
import numpy as np
import pytz
from datetime import datetime, timezone

tzobject = pytz.timezone('Europe/Amsterdam')


class AnnulusMonitoring(ApplicationAbstract):
    """Annulus monitoring for production wells."""

    def __init__(self):
        """Initialize annulus monitoring."""
        super().__init__()
        self.model = AnnulusPressure()

    def init_parameters(self, parameters):
        """Initialize parameters for annulus monitoring."""
        annulus_param = dict()
        annulus_param['EMW'] = parameters['annulus_EMW']
        annulus_param['RKB'] = parameters['annulus_RKB']
        annulus_param['SCS'] = parameters['annulus_SCS']

        self.model.update_parameters(annulus_param)

    def calculate(self):
        """Calculate annulus pressure."""
        u = {}
        x = {}

        self.model.calculate_output(u, x)
        y = self.model.get_output()

        self.outputs['MAASP'] = y['MAASP']

    def get_data(self):
        """Get annulus monitoring data."""
        start_time = datetime.strptime(self.inputs['start_time'], '%Y-%m-%d %H:%M:%S')
        start_time = tzobject.localize(start_time)
        start_time = start_time.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        end_time = datetime.strptime(self.inputs['end_time'], '%Y-%m-%d %H:%M:%S')
        end_time = tzobject.localize(end_time)
        end_time = end_time.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        timestep = 3600  # hardcoded 1 hour

        result, time = self.plant.database.read_internal_database(
            self.unit.plant.name,
            self.unit.name,
            'productionwell_annulus_a_pressure.measured',
            start_time,
            end_time,
            timestep
        )
        self.inputs['annulus_a_pressure'] = np.array(result)  # bar
        self.inputs['time'] = np.array(time)

        result, time = self.plant.database.read_internal_database(
            self.unit.plant.name,
            self.unit.name,
            'productionwell_annulus_b_pressure.measured',
            start_time,
            end_time,
            timestep
        )
        self.inputs['annulus_b_pressure'] = np.array(result)  # bar
