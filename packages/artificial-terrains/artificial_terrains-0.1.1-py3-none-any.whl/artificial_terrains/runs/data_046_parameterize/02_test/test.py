import numpy as np
import matplotlib.pyplot as plt


# Define two angles
theta_deg = np.arange(0, 90)
theta = theta_deg*np.pi/180

alpha_deg = np.atan(2 * np.tan(theta)) * 180/np.pi

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(alpha_deg)

ax.plot(theta_deg)
ax.plot(2*theta_deg)


# ax.set_title("Histogram of Mean Slope (degrees)")
ax.set_xlabel("x-value (a.u)")
ax.set_ylabel("Mean slope degree")
ax.grid()
ax.set_ylim([0, 90])

fig.tight_layout()

# Save the figure
save_path = "test.png"
fig.savefig(save_path)
plt.close(fig)

