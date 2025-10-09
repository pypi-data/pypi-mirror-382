# PGMI
# Copyright (C) 2025 Davis V. Garrad
from PGMInt.AbstractProcessor import *

import numpy as np

class SourceGratingProcessor(Processor):
    def __init__(self, num_periods, duty_cycle, period):
        '''Acts as a source grating with a given duty cycle and period (duty_cycle <= 1.0). Duty cycle of 0% represents an impenetrable wall.'''
        self.n = num_periods
        self.cycle = duty_cycle
        self.period = period

    def get_factor(self, km):
        a = self.cycle*self.period
        
        shift_factor = np.exp(1j * km * complex((self.n - 1.0)/2.0) * self.period) # shift the whole thing to the left (function starts centered at 0 and expands to the right)
        sinc_factor = 1/self.n * np.sinc(a/2.0 * km / np.pi) # divide by pi for numpy stupidity
        sum_factor = 1.0
        for i in range(1, self.n):
            sum_factor += np.exp(-1j * km * self.period * i) # shift each period by a period
        return shift_factor * sinc_factor * sum_factor


