# PGMI
# Copyright (C) 2025 Davis V. Garrad
from PGMInt.AbstractSample import *
import numpy as np
import matplotlib.pyplot as plt

class Slit(Sample):
    def __init__(self, width):
        super().__init__()
        self.width = width

    def get_spectrum(self, wavelength, momentum_range):
        return self.rect_grating_spectrum(wavelength, momentum_range)

    def rect_grating_spectrum(self, wavelength, momentum_range):
        '''Period is period of the grating, phase shift is basically alpha=2pi n h/lambda (the amount of phase shift induced by this material for the peaks of the grating'''   
        sample_width = 10
        C = self.width * sample_width / np.pi * momentum_range[1] 
        sample_N = np.minimum(int(C + 1 + np.sqrt(C*C + 2*C))+1, 401)
        
        kxs = np.fft.fftfreq(sample_N, d=self.width * 2*sample_width / (sample_N-1)) * 2*np.pi

        amps = np.sinc(kxs/(2*np.pi) * self.width)

        return kxs, amps

