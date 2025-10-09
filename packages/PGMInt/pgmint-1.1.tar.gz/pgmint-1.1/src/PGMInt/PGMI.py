# PGMI
# Copyright (C) 2025 Davis V. Garrad

import psutil
import numpy as np
import sys
np.set_printoptions(linewidth=np.inf, precision=3, suppress=True, threshold=sys.maxsize)
import scipy as sp
import pandas as pd
import pathos.multiprocessing as mp
import pathos as pa
import time
import math
import dools.davistools as davistools

################################ ASSORTED CONSTANTS ############################################################################################

# MEMORY LIMITS (TODO)
MAX_MEMORY = int(psutil.virtual_memory().total * 0.9) # 90% of device's memory (bytes)

# COMPUTATIONAL
simul_contrast_processes = pa.helpers.cpu_count()
floating_error_tolerance = 1.0e-10 # tolerance for "close enough" floating-point error checking. Completely arbitrary. TODO: Make not arbitrary.

# PHYSICAL CONST (Silicon phase shift)
Nbc = 5.0e28*4.149e-15

################################ PGMI CODE #####################################################################################################

def L2_norm(x):
    return np.sqrt(np.sum(np.square(np.abs(x))))

def magnification_factor(distance, previous_distance):
    return (1.0 + distance/previous_distance) if (previous_distance > 0.0) else 1.0

class Wave:
    '''Useful as a single diffraction order'''
    def __init__(self, params):
        '''Params is a dictionary with entries 'k0' (a 2-tuple of kx, kz), 'wavelength' (in meters), 'amplitude' (unitless)'''
        self.kx = params['k0'][0]
        self.kz = params['k0'][1]
        self.a = params['amplitude']
        self.wavelength = params['wavelength']
        
class Path:
    def __init__(self, params):
        self.wave_dist = params['wave_dist']
        if('kx_dist' in list(params.keys())):
            self.kx_dist = params['kx_dist']
        if not(self.wave_dist.verify_normalized()):
            print('WARN: Wavelength distribution not normalized.')
        self.diffraction_orders = []
        for (wavelength,amp) in self.wave_dist.wavelength_amplitude_pairs.items():
            if('kx_dist' in list(params.keys())):
                print('From k_x distribution')
                for (kx, kx_amp) in zip(params['kx_dist']['kxs'], params['kx_dist']['amps']):
                    k0 = 2*np.pi/wavelength
                    if(np.abs(kx) < np.abs(k0)):
                        kz = np.sqrt(np.square(k0) - np.square(kx))
                        self.diffraction_orders += [ Wave({'k0': [kx, kz], 'wavelength': wavelength, 'amplitude': amp*kx_amp})]
            else: ################## TODO: This is technically the proper way to do this with this model, but I think the other way (see intensity calculations) is more elegant, and either correct or a close approximation. Check this.
                self.diffraction_orders += [ Wave({'k0':[0.0, 2.0*np.pi/wavelength], 'wavelength':wavelength, 'amplitude':amp})]
        self.total_propagation_distance = 0.0
        self.prop_distance_scalar = 1.0
        self.momentum_range = [-params['max_momentum'], params['max_momentum']]
        self.processors = params['processors']
        
    def apply_grating(self, sample, distance):
        '''Takes a grating, and creates more diffraction orders arising from diffraction.'''
        mag = magnification_factor(distance, self.total_propagation_distance)
        self.total_propagation_distance += distance
        scaled_distance = distance*self.prop_distance_scalar # postulate 4
        self.prop_distance_scalar /= mag

        # phase shift beam
        for d in self.diffraction_orders:
            d.kx /= mag # postulate 1
            d.kz /= mag
            kz_reduced = d.kx**2 / (2 * np.sqrt(d.kx**2 + d.kz**2))
            d.a *= np.exp(-1j * kz_reduced * scaled_distance) # postulate 3, namely that the phase shift is enacted onto each MAGNIFIED order

        new_d_orders = [] # diffraction orders after the grating
        lost_orders = 0
        lost_orders_m = []
        new_orders_m = []
        
        for d in self.diffraction_orders:
            wavelength = d.wavelength # in m
            sample_kxs, sample_amps = sample.get_spectrum(wavelength, self.momentum_range)
            for m in range(len(sample_kxs)):
                k0_sqr = np.square(np.abs(d.kx)) + np.square(np.abs(d.kz))
                delta_kx = sample_kxs[m]
                kx = d.kx + delta_kx
                if(np.square(kx) < k0_sqr):
                    kz = np.sqrt(k0_sqr - np.square(np.abs(kx)))

                    amplitude = d.a*sample_amps[m]
                    if(np.abs(amplitude) > 0.0):
                        new_d_orders += [Wave({'k0':[kx,kz], 'wavelength':wavelength, 'amplitude':amplitude})]
                    else:
                        lost_orders += 1
                else:
                    lost_orders += 1
        self.diffraction_orders = new_d_orders

        # renormalize so intensities actually make sense if calculating that
        #norm = L2_norm([ d.a for d in self.diffraction_orders ])

        #for d in self.diffraction_orders:
        #    d.a /= norm
        
    def get_momentum_values(self, z=0.0):
        kxs = np.array([ d.kx for d in self.diffraction_orders ])
        kzs = np.array([ d.kz for d in self.diffraction_orders ])
        amps = np.array([ d.a for d in self.diffraction_orders ], dtype=complex)
        wavelengths = np.array([ d.wavelength for d in self.diffraction_orders ])
        
        mag_factor = magnification_factor(z, self.total_propagation_distance)
        kxs /= mag_factor # postulate 1
        kzs /= mag_factor

        scaled_z = z*self.prop_distance_scalar # postulate 4
        
        reduced_kzs = (kxs**2)/(2*np.sqrt(kxs**2 + kzs**2)) # phase change due to z (cancelling out x)
        amps *= np.exp(-1j * reduced_kzs * scaled_z) # postulate 3

        return kxs,kzs,amps,wavelengths

    def intensity_from_momenta_direct(self, x_vals, z, binsize=0):
        '''Questionable'''
        kxs,kzs,amps,wavelengths=self.get_momentum_values(z)

        import matplotlib.pyplot as plt

        print('getting IFFT')

        #plt.plot(kxs, np.real(amps))
        #plt.plot(kxs, np.imag(amps))
        #plt.show()

        wavefunction = np.zeros_like(x_vals).astype(np.complex128)
        for i in range(len(kxs)): # this is only good up to the smallest kx
            wavefunction += amps[i] * np.exp(1j * (x_vals * kxs[i]))# + z*kzs[i]))
        intensity = wavefunction*np.conj(wavefunction)

        #plt.plot(x_vals, intensity)
        #plt.show()
        
        freqs = np.fft.fftfreq(x_vals.shape[0], d=x_vals[1]-x_vals[0]) * 2*np.pi
        intensity_fft = np.fft.fft(intensity)

        for i in range(len(self.processors)):
            intensity_fft *= np.fft.fftshift(self.processors[i].get_factor(freqs))

        intensity_final = np.fft.ifft(intensity_fft)
        intensity_final /= np.sum(intensity_final)

        print('finishing/binning')

        if(binsize > 0):
            numbins = int((x_vals[-1] - x_vals[0]) // binsize) + 1
            numxs_per = len(x_vals) // numbins
            bins = np.zeros((numbins,))

            for i in range(len(bins)):
                bins[i] = np.sum(intensity_final[i*numxs_per:(i+1)*numxs_per])
                bin_xs = np.linspace(x_vals[0], binsize*numbins + x_vals[0], numbins)

            return bins, bin_xs
        return intensity_final, x_vals

    def intensity_from_momenta(self, x_vals, z):
        kxs,kzs,amps,wavelengths=self.get_momentum_values(z)

        def psi(index):
            return np.exp(-1j*x_vals*kxs[index]) * amps[index] * self.wave_dist.wavelength_amplitude_pairs[wavelengths[index]]

        total_psi = np.zeros(len(x_vals), dtype=complex)
        for i in range(len(kxs)):
            total_psi += psi(i)
        
        for i in range(len(self.processors)):
            total_psi *= self.processors[i].get_realspace_factor(x_vals)

        return np.abs(total_psi)*np.abs(total_psi)

    def intensity_from_momenta_defunct(self, x_vals, z, binsize=0):
        '''This function is potentially defunct'''
        print("WARN: USAGE OF FUNCTION THAT I HAVEN'T ANY CONFIDENCE IN")
        raise Exception
        kxs,kzs,amps,wavelengths=self.get_momentum_values(z)

        ############################################################## TODO Check model paper to make sure i'm actually doing this right. 
        #1) Should I actually need a gaussian input, or should i be adjusting coordinates as above (mf)? 
        #2) Could I need one for wavelength dependence and one for L dependence?
        #3) what the hell is going on with the weird patterns in sigma vs wavelength plots? sinc, square wave, etc.
    
        import matplotlib.pyplot as plt
        # get autocorrelation function first.
        print('correlating')

        dk_min = np.min(np.abs(kxs[1:]-kxs[:-1])) if len(kxs)>1 else 1
        def cts_extension_amps(k):
            return amps[np.argmin(np.abs(k - kxs))] if np.min(np.abs(k - kxs))<dk_min/2 else 0
        
        js = int((np.max(np.abs(kxs)))/dk_min)+1 if len(kxs)>1 else 0
        kxs_extended = np.real(dk_min) * np.linspace(-js, js, 2*js+1, endpoint=True)

        autocor = np.zeros_like(kxs_extended).astype(np.complex128)

        for i in range(2*js+1):
            for j in range(2*js+1):
                autocor[i] += cts_extension_amps(kxs_extended[i]+kxs_extended[j]) * (cts_extension_amps(kxs_extended[j]))
        kxs = kxs_extended
        plt.scatter(kxs, autocor)
        plt.scatter(kxs, np.imag(autocor))
        plt.show()

        nz = np.argwhere((np.abs(autocor) > 1e-9))[:,0]
        autocor = autocor[nz]/np.sum(np.abs(autocor[nz]))
        kxs = kxs[nz]

        print('processing')
        # autocor is intensity in k-space. multiply with filters next
        for ip in range(len(self.processors)):
            autocor *= self.processors[ip].get_factor(kxs)

        print('inverse fourier-ing')
        # inverse fourier transform
        end_intensity = np.zeros_like(x_vals).astype(np.complex128)
        for ikx in range(len(kxs)):
            end_intensity += autocor[ikx]*np.exp(1j * (kxs[ikx] * x_vals + kzs[ikx] * z))

        plt.plot(x_vals, end_intensity)
        plt.title('intensity')
        plt.show()
        #batchN=500
        #last_kx = 0
        #for ikx in range(len(kxs)//batchN):
        #    end_intensity += np.sum(autocor[ikx*batchN:(ikx+1)*batchN,None] * np.exp(-1j * kxs[ikx*batchN:(ikx+1)*batchN,None] * x_vals[None,:]), axis=0)
        #    last_kx = (ikx+1)*batchN
        #end_intensity += np.sum(autocor[last_kx:,None] * np.exp(-1j * kxs[last_kx:,None] * x_vals[None,:]), axis=0)
        end_intensity = np.abs(end_intensity).astype(np.float64)
        end_intensity_normalized = end_intensity# / np.sum(end_intensity)

        #plt.plot(kxs, np.real(autocor))
        #plt.plot(kxs, np.imag(autocor))
        #plt.plot(kxs, np.abs(autocor))
        #plt.show()

        print('finishing/binning')

        if(binsize > 0):
            numbins = int((x_vals[-1] - x_vals[0]) // binsize) + 1
            numxs_per = len(x_vals) // numbins
            bins = np.zeros((numbins,))

            for i in range(len(bins)):
                bins[i] = np.sum(end_intensity_normalized[i*numxs_per:(i+1)*numxs_per])
                bin_xs = np.linspace(x_vals[0], binsize*numbins + x_vals[0], numbins)

            return bins, bin_xs
        return end_intensity_normalized, x_vals
    
    def autocorrelation(self, m, z, wavevector, multiprocess=True, progress_report=True, amps=None, kxs=None):
        '''Finds the value of the autocorrelation function H(m*km)=psi(km) (convolution) psi*(km)'''
        if(amps is None):
            kxs,kzs,amps,wavelengths=self.get_momentum_values(z)
        else:
            _,_,amp_mod,wavelengths=self.get_momentum_values(z)
            amps *= amp_mod

        indices = []
        indices_conj = []

        total_autocorrelation = 0.0
        
        unique_wavelengths, counts = np.unique(wavelengths, return_counts=True)
        
        st_begin = time.time()
        def single_wavelength(index):
            kx_begin_index = np.sum(counts[:index])
            kx_end_index = kx_begin_index + counts[index]
            kx_indices = np.linspace(kx_begin_index, kx_end_index-1, counts[index]).astype(int)
            kxs_clipped = kxs[kx_indices]/wavevector
            indices = np.nonzero(np.abs(-kxs_clipped - (-kxs_clipped[:,np.newaxis] - m)) <= 1.0e-2)
            amps_normal = amps[kx_indices[indices[0]]]
            amps_conj = amps[kx_indices[indices[1]]].conj()
            if(time.time() - st_begin > 1.0 and progress_report):
                davistools.progress_statement(index, unique_wavelengths.shape[0], time.time()-st_begin)
            return np.sum(amps_normal*amps_conj)

        if(multiprocess):
            total = 0
            progress_report=False
            with mp.ProcessPool(simul_contrast_processes) as pool:
                total_autocorrelation = np.sum(pool.map(single_wavelength, range(unique_wavelengths.shape[0])))

        else:                
            for i in range(unique_wavelengths.shape[0]):
                if(progress_report):
                    davistools.progress_statement(i, unique_wavelengths.shape[0], label='Autocorrelation (m={})'.format(m))
                total_autocorrelation += single_wavelength(i)
       
        return total_autocorrelation


    def contrast(self, z, wavevector, debug=False, multiprocess=True, progress_report=True):
        '''Takes moire wavevector'''
        if(wavevector == 0.0):
            return 0.0 # edge case
        
        zero_intensity = self.autocorrelation(0, z, wavevector, multiprocess, progress_report)
        fringe_intensity = self.autocorrelation(1, z, wavevector, multiprocess, progress_report) # important: autocorrelation function takes both +/- 1 by virtue of its symmetry
        
        if(zero_intensity == 0.0):
            return 0.0

        total_factor = np.prod([i.get_factor(wavevector) for i in self.processors])
        contrast = 2*np.abs(fringe_intensity/zero_intensity * total_factor)

        return contrast

class WavelengthDistribution:
    def __init__(self, wavelengths=[], amps=[], force_normalize=False):
        self.wavelength_amplitude_pairs = {}
        for l,a in zip(wavelengths, amps):
            self.wavelength_amplitude_pairs[l] = a
        if(force_normalize):
            total_amp = np.sum(np.square(np.array(list(self.wavelength_amplitude_pairs.values()))))
            for i in self.wavelength_amplitude_pairs.keys():
                self.wavelength_amplitude_pairs[i] /= np.sqrt(total_amp)

    def set_boltzmann(self,temperature, resolution):
        kT = temperature * 1.38065e-23 # boltzmann constant * temperature
        h = 6.626e-34 # thanks, Planck
        m = 1.6749275e-27 # neutron mass
        a = np.sqrt(kT/m)
        peak = h/(m*np.sqrt(2)*a)

        def bz(v):
            return np.sqrt(2/(np.pi)) * v**2 / a**3 * np.exp(-v**2/(2*a**2))

        sd = h/(m*(a * np.sqrt((3*np.pi - 8)/np.pi)))
        x1 = np.maximum(peak-sd, 0.1e-10)
        lambda_values = np.linspace(x1, x1+2*sd, resolution)
        amplitudes = np.sqrt(bz(h/(m*lambda_values)))

        norm = np.sum(amplitudes**2)
        amplitudes/=np.sqrt(norm)

        for l,a in zip(lambda_values, amplitudes):
            self.add_wavelength(l, a)
    
    def verify_normalized(self):
        s = 0
        for (wavelength, amp) in self.wavelength_amplitude_pairs.items():
            s += amp**2
        if(np.abs(s-1.0) < floating_error_tolerance):
            return True, None
        return False, s

    def mono_wavelength(self):
        '''Gets the maximum-amplitude wavelength'''
        max_l = 0
        max_amp = 0
        for (l,amp) in self.wavelength_amplitude_pairs.items():
            if(amp > max_amp):
                max_l = l
        return max_l

    def add_wavelength(self, wavelength, proportion):
        self.wavelength_amplitude_pairs[wavelength] = proportion

    def plot(self):
        import matplotlib.pyplot as plt
        plt.scatter(list(self.wavelength_amplitude_pairs.keys()), np.square(list(self.wavelength_amplitude_pairs.values())))
        plt.ylabel('Probability')
        plt.xlabel('Wavelength')
        plt.show()
