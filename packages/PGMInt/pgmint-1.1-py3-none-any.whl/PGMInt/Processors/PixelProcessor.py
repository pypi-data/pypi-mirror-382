# PGMI
# Copyright (C) 2025 Davis V. Garrad
from PGMInt.AbstractProcessor import *

import numpy as np

class PixelProcessor(Processor):
    def __init__(self, width):
        self.width = width

    def get_factor(self, km):
        return np.sinc(self.width/2.0 * km / np.pi) # divide by pi because NumPy has weird conventions
    # 2025 EDIT: As this is being made public, I'd like to declare that, for legal reasons, this is a joke and by no means an act of aggression towards NumPy <3


