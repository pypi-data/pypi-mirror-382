from gemini_framework.framework.preprocessor import PreProcessor


class PreProcessor(PreProcessor):

    def __init__(self, unit):
        super().__init__(unit)

        self.link_input(unit, 'measured', 'esp_inlet_pressure')
        self.link_output(unit, 'filtered', 'esp_inlet_pressure')

        self.link_input(unit, 'measured', 'esp_outlet_pressure')
        self.link_output(unit, 'filtered', 'esp_outlet_pressure')

        self.link_input(unit, 'measured', 'esp_inlet_temperature')
        self.link_output(unit, 'filtered', 'esp_inlet_temperature')

        self.link_input(unit, 'measured', 'esp_outlet_temperature')
        self.link_output(unit, 'filtered', 'esp_outlet_temperature')

        self.link_input(unit, 'measured', 'esp_current')
        self.link_output(unit, 'filtered', 'esp_current')

        self.link_input(unit, 'measured', 'esp_voltage')
        self.link_output(unit, 'filtered', 'esp_voltage')

        self.link_input(unit, 'measured', 'esp_power_consumption')
        self.link_output(unit, 'filtered', 'esp_power_consumption')

        self.link_input(unit, 'measured', 'esp_frequency')
        self.link_output(unit, 'filtered', 'esp_frequency')

        self.link_input(unit, 'measured', 'esp_flowrate')
        self.link_output(unit, 'filtered', 'esp_flowrate')

        self.link_input(unit, 'measured', 'esp_vibration_x')
        self.link_output(unit, 'filtered', 'esp_vibration_x')

        self.link_input(unit, 'measured', 'esp_vibration_y')
        self.link_output(unit, 'filtered', 'vibration_y')

        self.link_input(unit, 'measured', 'esp_head')
        self.link_output(unit, 'filtered', 'esp_head')
