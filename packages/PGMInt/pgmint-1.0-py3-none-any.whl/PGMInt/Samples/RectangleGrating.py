# PGMI
# Copyright (C) 2025 Davis V. Garrad
from PGMInt.Samples.AbstractSample import *
import numpy as np

from PGMInt.PGMI import Nbc

class RectangleGrating(Sample):
    def __init__(self, period, height=0.0, phase=None, shift=0.0):
        super().__init__()
        self.period = period
        self.height = height
        self.phase = phase
        self.shift = shift

    def get_spectrum(self, wavelength, momentum_range):
        return self.rect_grating_spectrum(wavelength, momentum_range)

    def rect_grating_spectrum(self, wavelength, momentum_range):
        '''Period is period of the grating, phase shift is basically alpha=2pi n h/lambda (the amount of phase shift induced by this material for the peaks of the grating'''   
        wavevector = 2*np.pi/self.period
        max_num_orders = int(momentum_range[1]/wavevector)
        if(self.phase is not None):
            alpha = self.phase
        else:
            alpha = Nbc * wavelength * self.height

        ms = np.array(list(range(-max_num_orders, max_num_orders+1)))
        kxs = ms.astype(complex) * wavevector
        amps = np.zeros(len(kxs), dtype=complex)

        for i in range(len(ms)):
            if(ms[i] == 0):
                amps[i] = np.cos(alpha/2.0)
            elif(ms[i] % 2 == 0):
                amps[i] = 0.0
            else:
                amps[i] = np.sin(alpha/2.0) * 2.0 * np.exp(-1j*wavevector*ms[i]*self.shift)/(np.pi * ms[i])

        #import matplotlib.pyplot as plt
        #plt.plot(ms, np.abs(amps))
        #plt.title('grating')
        #plt.plot(ms, np.abs(np.sinc(alpha/2) * 2/(np.pi * ms)))
        #plt.show()

        return kxs, amps

