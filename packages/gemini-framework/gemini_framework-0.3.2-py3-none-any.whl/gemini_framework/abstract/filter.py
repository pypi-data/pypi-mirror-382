from abc import ABC
import numpy as np
import gemini_framework.framework.filter.statuscode as statuscode


class Filter(ABC):

    def __init__(self):
        self.status = statuscode.NO_DATA
        self.output = np.nan

    def update(self, u, status):
        self.output = u
        self.status = status
