from flekspy import FLEKSTP
import matplotlib.pyplot as plt
#tp = FLEKSTP("test_particles", iSpecies=1)
#tp = FLEKSTP("tp_debug2", iSpecies=1)
tp = FLEKSTP("tests/data/test_particles_PBEG", iSpecies=1)
pid = tp.getIDs()[0]
pt = tp[pid]
pt[:,4:7]
tp.get_ExB_drift(pid)
tp.get_curvature_drift(pid)
tp.get_gradient_drift(pid)


tp._calculate_curvature(pt)

# tp.plot_trajectory(pid, type="full")
# plt.show()