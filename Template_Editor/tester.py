import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Surface 615 parameters
b1, c1, r1 = -5.715, 0, 0.7432  # center and radius
# Surface 719 parameters
a2, c2, r2 = 87.63, 76.36, 175.26  # center and radius

# Create coordinate grid
theta = np.linspace(0, 2.*np.pi, 100)  # angular coordinate
z = np.linspace(-2, 2, 100)  # x-coordinate range, adjust as needed

# Make grids for each cylinder
Theta1, Z1 = np.meshgrid(theta, z)
Theta2, Z2 = np.meshgrid(theta, z)

# Convert to Cartesian coordinates
# For CX cylinder
X1 = Z1
Y1 = b1 + r1*np.cos(Theta1)
Z1 = c1 + r1*np.sin(Theta1)

# For CY cylinder
X2 = a2 + r2*np.cos(Theta2)
Y2 = Z2
Z2 = c2 + r2*np.sin(Theta2)

fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# Plot surfaces
ax.plot_surface(X1, Y1, Z1, color='b', alpha=0.8)
ax.plot_surface(X2, Y2, Z2, color='r', alpha=0.8)

ax.set_title('3D Plot of CX and CY Cylinders', fontsize=14)
ax.set_xlabel('x', fontsize=12)
ax.set_ylabel('y', fontsize=12)
ax.set_zlabel('z', fontsize=12)

plt.show()