import numpy as np
import matplotlib.pyplot as plt
from . import extraction as ex
from . import utils

class AnalysisObject:
    """Simple wrapper: hold image, find points, and make quick plots."""

    def __init__(self, im):
        """Load image and stash basic metadata."""
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
        """Compute geometric and threshold centers."""
        self.geo_c = utils.geometric_centroid(self.data)
        self.q25_c = utils.threshold_center(self.data, q=25)

    def find_bright_points(self, threshold=0.5, radius=5.0, margin=None, max_it=999):
        """Primary bright-point extraction (recursive blanking)."""
        self.bright_points = ex.rbp_find_bright_points(self.image, threshold, radius, margin, max_it)
        return self.bright_points

    def plot_centers(self):
        """Image with centers overlaid (labels only)."""
        fig, ax = plt.subplots(figsize=(6, 6))
        extent = [0, self.xdim * self.cell, 0, self.ydim * self.cell]
        ax.imshow(self.data, origin='lower', cmap='afmhot', extent=extent)

        gx, gy = self.geo_c
        tx, ty = self.q25_c
        ax.plot(gx * self.cell, gy * self.cell, 'wo', label='Geometric')
        ax.plot(tx * self.cell, ty * self.cell, 'bo', label='Threshold')
        ax.legend(loc='upper right')
        ax.set_xlabel('x [radian]')
        ax.set_ylabel('y [radian]')
        return fig

    def plot_angle_profiles(self, n_angles=20, center="geo", step=1.0, threshold=None, radius=None):
        """
        Rays from center in equal angle steps; take the peak per ray.
        Left: image + bright points. Middle: Radius vs Angle (scatter).
        Right: Brightness vs Angle (scatter). Axes labeled, no titles/lines.
        """
        data = self.data
        h, w = data.shape

        # choose center
        if isinstance(center, (tuple, list, np.ndarray)) and len(center) == 2:
            xs, ys = float(center[0]), float(center[1])
        elif str(center).lower() == "q25":
            xs, ys = self.q25_c
        else:
            xs, ys = self.geo_c

        # equal-angle rays
        n = int(max(1, n_angles))
        thetas = 2.0 * np.pi * (np.arange(n) / n)
        rmax = float(np.hypot(h, w))  # max radius in pixels

        angles_deg, radii_px, peaks = [], [], []

        for th in thetas:
            rs = np.arange(0.0, rmax, float(step))
            if rs.size < 2:
                continue

            xsamp = xs + rs * np.cos(th)
            ysamp = ys + rs * np.sin(th)

            m = (xsamp >= 0) & (xsamp <= w - 1) & (ysamp >= 0) & (ysamp <= h - 1)
            if not np.any(m):
                continue

            xi = np.rint(xsamp[m]).astype(int)
            yi = np.rint(ysamp[m]).astype(int)
            rr = rs[m]
            prof = data[yi, xi]

            j = int(np.argmax(prof))
            angles_deg.append(np.degrees(th))
            radii_px.append(float(rr[j]))   # keep in pixels to avoid tiny rad units
            peaks.append(float(prof[j]))

        # figure: image+points | radius scatter | brightness scatter
        fig, (ax_img, ax_r, ax_b) = plt.subplots(1, 3, figsize=(12, 4), constrained_layout=True)

        # left panel: image and bright points
        ax_img.imshow(data, origin="lower", cmap="afmhot")
        if self.bright_points is None:
            self.find_bright_points(threshold=threshold, radius=radius)
        if self.bright_points is not None and len(self.bright_points) > 0:
            pts = np.asarray(self.bright_points)
            ax_img.scatter(pts[:, 0], pts[:, 1], s=8, c="c")
        ax_img.set_xticks([])
        ax_img.set_yticks([])

        # middle: radius vs angle (scatter only)
        if len(angles_deg) > 0:
            ax_r.scatter(angles_deg, radii_px, s=22)
        ax_r.set_xlabel("Angle [deg]")
        ax_r.set_ylabel("Radius [px]")

        # right: brightness vs angle (scatter only)
        if len(angles_deg) > 0:
            ax_b.scatter(angles_deg, peaks, s=22)
        ax_b.set_xlabel("Angle [deg]")
        ax_b.set_ylabel("Brightness")

        return fig
