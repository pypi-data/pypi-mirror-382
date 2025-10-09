# PGMI
# Copyright (C) 2025 Davis V. Garrad
from PGMInt.AbstractProcessor import *

import numpy as np

class SlitProcessor(Processor):
    def __init__(self, width):
        self.width = width

    def get_factor(self, km):
        return np.sinc(self.width * km/2 / np.pi)

    def get_realspace_factor(self, x):
        return np.where(np.abs(x) <= self.width/2, 1, 0)
