import numpy as np
import matplotlib.pyplot as plt


psi_deg = np.arange(0, 360)
psi_rad = psi_deg*np.pi/180

psi_0 = np.zeros_like(psi_deg)

theta_deg = 20
theta_rad = theta_deg*np.pi/180

# We consider two planes with pitch 20 degrees.
# We keep one fix, and rotate the other 360 degrees
# Add them for each configuration, and calculate the resultant angle

new_angle = np.tan(theta_rad)*np.abs(2*np.cos(psi_rad - psi_0))
new_angle_deg = new_angle*180/np.pi

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(new_angle_deg)

# ax.set_title("Histogram of Mean Slope (degrees)")
ax.set_xlabel("x-value (a.u)")
ax.set_ylabel("Mean slope degree")
ax.grid()

fig.tight_layout()

# Save the figure
save_path = "test2.png"
fig.savefig(save_path)
plt.close(fig)

