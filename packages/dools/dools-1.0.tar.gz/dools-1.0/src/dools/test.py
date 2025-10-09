import davis_plots as dp
import numpy as np
import matplotlib.pyplot as plt

dp.init_plots_for_paper()

fig, ax = dp.init_plot()
ax.plot(np.linspace(0.0, 10.0, 100), np.pow(np.linspace(0.0, 10.0, 100), 2))
ax.set_xlabel('X label, $x$')
ax.set_ylabel('Y label, $y$')
plt.show()

fig, axs = dp.init_plot((2, 2))
axs[0][0].plot(np.linspace(0.0, 10.0, 100), np.pow(np.linspace(0.0, 10.0, 100), 2))
axs[0][1].plot(np.linspace(2.0, 10.0, 100), np.pow(np.linspace(2.0, 10.0, 100), 2))
axs[1][0].plot(np.linspace(4.0, 10.0, 100), np.pow(np.linspace(4.0, 10.0, 100), 2))
axs[1][1].plot(np.linspace(8.0, 10.0, 100), np.pow(np.linspace(8.0, 10.0, 100), 2))
fig.supxlabel('X labe wooo')
fig.supylabel('Y label woooo')
plt.show()
