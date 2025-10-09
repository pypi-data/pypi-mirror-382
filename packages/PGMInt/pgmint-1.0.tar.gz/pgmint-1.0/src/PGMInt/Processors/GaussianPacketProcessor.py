# PGMI
# Copyright (C) 2025 Davis V. Garrad
from PGMInt.AbstractProcessor import *

import numpy as np

class GaussianPacketProcessor(Processor):
    def __init__(self, width):
        self.width = width

    def get_factor(self, km):
        return np.exp(-np.square(km) * np.square(self.width)/2) * np.sqrt(2*np.pi) * self.width
    def get_realspace_factor(self, x):
        return np.exp(-np.square(x) / (2*np.square(self.width))) / (np.sqrt(2*np.pi) * self.width)
