from PGMInt.PGMI import WavelengthDistribution, Path
from PGMInt.Samples.RectangleGrating import RectangleGrating
import numpy as np

p_g1 = 2e-6
num_orders = 10

params = {
        'wave_dist': WavelengthDistribution([5.0e-10], [1]),
        'max_momentum': 2*np.pi / (p_g1) * num_orders,
        'min_momentum': -2*np.pi / (p_g1) * num_orders,
        'processors': [],
        }

p = Path(params)

g1 = RectangleGrating(p_g1, 5e-6)
g2 = RectangleGrating(p_g1, 5e-6)

p.apply_grating(g1, 0.4) # apply G1 0.4m from the "slit"/start of the cone beam
p.apply_grating(g2, 0.425) # apply G2 0.425m from the last grating (equivalent to applying G2 immediately after G1, but with a smaller period!)
#print(p.contrast(2.5, 2*np.pi/5.0e-10))

import matplotlib.pyplot as plt
x_vals = np.linspace(-10.0e-6, 10.0e-6, 256)
V = []
zs = np.linspace(0.0, 1.0, 1024)
intensities = np.zeros((len(zs),len(x_vals)))
for zi in range(len(zs)):
    V += [p.contrast(zs[zi], 2*np.pi/p_g1)]
    intensities[zi,:] = p.intensity_from_momenta(x_vals, zs[zi])
plt.plot(zs, V)
plt.show()

plt.pcolormesh(zs, x_vals, intensities.T, shading='nearest')
plt.show()
