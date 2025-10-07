import numpy as np
import matplotlib.pyplot as plt
from . import extraction as ex
from . import utils

class AnalysisObject:
    """Wrapper to handle image data and run ring fitting analysis."""

    def __init__(self, im):
        """Load image and set up data/metadata."""
        self.image = im
        self.data = im.imarr()
        self.xdim = im.xdim
        self.ydim = im.ydim
        self.cell = im.psize
        self.ra = im.ra
        self.dec = im.dec
        self.peak = getattr(im, 'peak', None)
        self.total_flux = im.total_flux()
        self.compute_centers()
        self.bright_points = None

    def compute_centers(self):
        """Compute geometric and threshold centers (flux center removed)."""
        self.geo_c = utils.geometric_centroid(self.data)
        self.q25_c = utils.threshold_center(self.data, q=25)

    def find_bright_points(self, threshold=0.5, radius=5.0, margin=None, max_it=999):
        """Grab bright points using recursive blanking method."""
        self.bright_points = ex.rbp_find_bright_points(self.image, threshold, radius, margin, max_it)
        return self.bright_points

    def plot_centers(self):
        """Plot image with centers overlaid (no flux center)."""
        fig, ax = plt.subplots(figsize=(6,6))
        extent = [0, self.xdim*self.cell, 0, self.ydim*self.cell]
        ax.imshow(self.data, origin='lower', cmap='afmhot', extent=extent)

        gx, gy = self.geo_c
        tx, ty = self.q25_c
        ax.plot(gx*self.cell, gy*self.cell, 'wo', label='Geometric')
        ax.plot(tx*self.cell, ty*self.cell, 'bo', label='Threshold Center')
        ax.legend()
        ax.set_xlabel('x [radian]')
        ax.set_ylabel('y [radian]')
        return fig

    def plot_angle_profiles(self, n_angles=20, center="geo", step=0.5):
        """Side-by-side: radius vs angle and brightness vs angle."""
        data = self.data
        h, w = data.shape

        # pick center
        if isinstance(center, (tuple, list, np.ndarray)) and len(center) == 2:
            xs, ys = float(center[0]), float(center[1])
        elif str(center).lower() == "q25":
            xs, ys = self.q25_c
        else:
            xs, ys = self.geo_c

        # angles and sampling setup
        thetas = np.linspace(0.0, 2.0 * np.pi, int(n_angles), endpoint=False)
        rmax = float(np.hypot(h, w))
        k = np.array([1, 2, 3, 2, 1], dtype=float); k /= k.sum()

        ang_deg = []
        radii = []
        peaks = []

        for th in thetas:
            rs = np.arange(0.0, rmax, float(step))
            xsamp = xs + rs * np.cos(th)
            ysamp = ys + rs * np.sin(th)

            m = (xsamp >= 0) & (xsamp <= w - 1) & (ysamp >= 0) & (ysamp <= h - 1)
            if not np.any(m):
                continue
            xs_i = np.rint(xsamp[m]).astype(int)
            ys_i = np.rint(ysamp[m]).astype(int)
            rs_i = rs[m]
            if rs_i.size < 3:
                continue

            prof = data[ys_i, xs_i]
            prof_s = np.convolve(prof, k, mode="same")

            j = int(np.nanargmax(prof_s))
            ang_deg.append(np.degrees(th))
            radii.append(rs_i[j] * self.cell)      # radius in image units
            peaks.append(float(prof_s[j]))         # brightness at peak

        # fallback if nothing collected
        if len(ang_deg) == 0:
            return plt.figure()  # empty plot, nothing to show

        # build the two-panel figure
        fig, axes = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)

        axes[0].plot(ang_deg, radii)
        axes[0].set_xlabel("Angle [deg]")
        axes[0].set_ylabel("Radius")

        axes[1].plot(ang_deg, peaks)
        axes[1].set_xlabel("Angle [deg]")
        axes[1].set_ylabel("Brightness")

        return fig
