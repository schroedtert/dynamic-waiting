import numpy as np
# import matplotlib.pyplot as plt
import pandas as pd
#
# # definitions for the axes
# left, width = 0.1, 0.65
# bottom, height = 0.1, 0.65
# spacing = 0.005
#
# rect_scatter = [left, bottom, width, height]
# rect_histx = [left, bottom + height + spacing, width, 0.2]
# rect_histy = [left + width + spacing, bottom, 0.2, height]
#
# # start with a square Figure
# fig = plt.figure(figsize=(8, 8))
#
#
# traj =  pd.read_csv('results/platform-test/traj.csv')
# print(traj)
#
# plt.figure()
# plt.title("traj")
#
# x = traj[traj.step == traj.step.max()].x
# y = traj[traj.step == traj.step.max()].y
# plt.hist2d(x, y, bins=300)
# # plt.scatter(x, y, color='black', s=5.5)
#
# # for ped_id in traj.id.unique():
# #     df = traj.loc[traj['id'] == ped_id]
# #     df = df.sort_values('step')
# #     plt.plot(df.x, df.y, alpha=0.5, linewidth=0.2)
#
#
#
# plt.axis('equal')
# plt.gca().set_adjustable("box")
# # plt.xlim([-100000, 30000])
# plt.show()


import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

traj =  pd.read_csv('results/platform-test/traj.csv')

# Fixing random state for reproducibility
np.random.seed(19680801)


# the random data
# x = np.random.randn(1000)
# y = np.random.randn(1000)
df = traj.loc[traj.id > 40]
x = df[df.step == df.step.max()].x
y = df[df.step == df.step.max()].y



fig, axScatter = plt.subplots(figsize=(5.5, 5.5))

# the scatter plot:
axScatter.scatter(x, y)
axScatter.set_aspect(1.)

# create new axes on the right and on the top of the current axes
# The first argument of the new_vertical(new_horizontal) method is
# the height (width) of the axes to be created in inches.
divider = make_axes_locatable(axScatter)
axHistx = divider.append_axes("top", 1.2, pad=0.1, sharex=axScatter)
axHisty = divider.append_axes("right", 1.2, pad=0.1, sharey=axScatter)

# make some labels invisible
axHistx.xaxis.set_tick_params(labelbottom=False)
axHisty.yaxis.set_tick_params(labelleft=False)

# now determine nice limits by hand:
binwidth = 1000.
xymax = max(np.max(np.abs(x)), np.max(np.abs(y)))
lim = (int(xymax/binwidth) + 1)*binwidth

bins = np.arange(-lim, lim + binwidth, binwidth)
axHistx.hist(x, bins=bins)
axHisty.hist(y, bins=bins, orientation='horizontal')

# the xaxis of axHistx and yaxis of axHisty are shared with axScatter,
# thus there is no need to manually adjust the xlim and ylim of these
# axis.

# axHistx.set_yticks([0, 50, 100])
#
# axHisty.set_xticks([0, 50, 100])

plt.ylim([-10000, 10000])
plt.draw()
plt.show()