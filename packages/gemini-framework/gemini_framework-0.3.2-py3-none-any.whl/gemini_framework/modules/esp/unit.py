"""ESP unit: ESP-related calculation modules."""

from gemini_framework.abstract.unit_abstract import UnitAbstract
from gemini_framework.modules.esp.calculate_theoretical_head \
    import CalculateTheoreticalHead
from gemini_framework.modules.esp.calculate_theoretical_power \
    import CalculateTheoreticalPower
from gemini_framework.modules.esp.calculate_theoretical_outlet_pressure \
    import CalculateTheoreticalOutletPressure
from gemini_framework.modules.esp.calculate_vlp_ipr_inlet_pressure \
    import CalculateVLPIPRInletPressure
from gemini_framework.modules.esp.calculate_vlp_outlet_pressure \
    import CalculateVLPOutletPressure
from gemini_framework.modules.esp.calculate_vlp_head \
    import CalculateVLPHead


class ESPUnit(UnitAbstract):
    """ESP unit that includes theoretical and VLP calculations."""

    def __init__(self, unit_id, unit_name, plant):
        """Initialize ESP unit."""
        super().__init__(unit_id=unit_id, unit_name=unit_name, plant=plant)

        # define unit modules
        self.modules['preprocessor'] = []
        self.modules['model'].append(CalculateTheoreticalHead(self))
        self.modules['model'].append(CalculateTheoreticalPower(self))
        self.modules['model'].append(CalculateTheoreticalOutletPressure(self))
        self.modules['model'].append(CalculateVLPIPRInletPressure(self))
        self.modules['model'].append(CalculateVLPOutletPressure(self))
        self.modules['model'].append(CalculateVLPHead(self))
        self.modules['postprocessor'] = []
