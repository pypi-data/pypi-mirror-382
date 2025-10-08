from gemini_framework.abstract.filter import Filter
import gemini_framework.framework.filter.statuscode as statuscode
import numpy as np


class MeanFilter(Filter):
    width = 1
    buffer = np.array([])

    def __init__(self, *args):
        super().__init__()

        self.width = args[0]

        self.buffer = np.full((1, self.width), np.nan)

    def update(self, u, ustatus):
        self.buffer = self.buffer[1:] + u

        if ustatus >= statuscode.OK:
            y = np.mean(self.buffer)
            if np.isnan(y):
                y = np.mean(self.buffer[~np.isnan(self.buffer)])
                if len(y) > 0:
                    ystatus = statuscode.OK
                else:
                    ystatus = statuscode.FLT_BAD
            else:
                ystatus = statuscode.OK
        else:
            y = u
            ystatus = ustatus

        self.output = y
        self.status = ystatus

        return y, ystatus
