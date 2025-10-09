from gemini_framework.abstract.unit_module_abstract import UnitModuleAbstract


class PreProcessor(UnitModuleAbstract):
    filters = {}
    filtersinput = {}

    def __init__(self, unit):
        super().__init__(unit)

    def link(self):
        self.logger.error(
            print(f'Module {self.__class__.__name__} did not implement a link method'))
