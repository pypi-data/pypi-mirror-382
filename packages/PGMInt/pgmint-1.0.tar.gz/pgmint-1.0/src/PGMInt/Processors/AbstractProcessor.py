# PGMI
# Copyright (C) 2025 Davis V. Garrad
class Processor:
    def __init__(self):
        '''This class acts as a multiplier for the Fourier intensity - that is, this represents a convolved filter.'''
        print('WARN: Abstraction created. Keep an eye on what you\'re simulating.')

    def get_factor(self, km):
        return 1.0

    def get_realspace_factor(self, x):
        return 1.0


