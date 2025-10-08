import numpy as np
import matplotlib.pyplot as plt
from . import extraction as ex
from . import utils

class AnalysisObject:
    """Hold image, find points, make quick diagnostic plots."""

    def __init__(self, im):
        """Load image and stash basic metadata."""
        self.image = im
        self.data = im.imarr()
        self.xdim = im.xdim
        self.ydim = im.ydim
        self.cell = im.psize
        self.ra = im.ra
        self.dec = im.dec
        self.peak = getattr(im, "peak", None)
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
        ax.imshow(self.data, origin="lower", cmap="afmhot", extent=extent)
        gx, gy = self.geo_c
        tx, ty = self.q25_c
        ax.plot(gx * self.cell, gy * self.cell, "wo", label="Geometric")
        ax.plot(tx * self.cell, ty * self.cell, "bo", label="Threshold")
        ax.legend(loc="upper right")
        ax.set_xlabel("x [radian]")
        ax.set_ylabel("y [radian]")
        return fig

    def plot_angle_profiles(self, n_angles=20, center="q25", normalize=True):
        """
        Bright-points-only version (simple and stable):
        - Use threshold center by default (closest to true ring center).
        - Take bright points from extraction; for each point:
            angle = clock-style (12→0°, 3→90°, 6→180°, 9→270°)
            radius = distance to chosen center [px]
            brightness = image value at the point (optionally normalized 0..1)
        - Show three panels:
            [image + points + center] | [Radius vs Angle] | [Brightness vs Angle]
        - Scatter only; axes labeled; x-axis ticks = {0,90,180,270,360}.
        Note: `n_angles` is kept for API compatibility but not used here.
        """
        data = self.data

        # ensure bright points exist
        if self.bright_points is None or len(self.bright_points) == 0:
            self.find_bright_points(threshold=None, radius=None)

        if self.bright_points is None or len(self.bright_points) == 0:
            fig, ax = plt.subplots(1, 1, figsize=(5, 4))
            ax.text(0.5, 0.5, "No bright points found", ha="center", va="center")
            ax.set_axis_off()
            return fig

        # select center
        csel = str(center).lower()
        if isinstance(center, (tuple, list, np.ndarray)) and len(center) == 2:
            xs, ys = float(center[0]), float(center[1])
        elif csel in ("q25", "threshold", "thresh"):
            xs, ys = self.q25_c
        else:  # default fallback
            xs, ys = self.geo_c

        pts = np.asarray(self.bright_points, float)
        x = pts[:, 0]
        y = pts[:, 1]

        # distances (px)
        radii_px = np.hypot(x - xs, y - ys)

        # clock-style angles:
        # make y-up for angle math, then rotate so up = 0°
        dx = x - xs
        dy_up = -(y - ys)
        theta_deg = np.degrees(np.arctan2(dy_up, dx))  # 0° = right, 90° = up
        angle_clock = (90.0 - theta_deg) % 360.0       # 0° = up, 90° = right, ...

        # brightness at bright-point pixels
        xi = np.clip(np.rint(x).astype(int), 0, data.shape[1] - 1)
        yi = np.clip(np.rint(y).astype(int), 0, data.shape[0] - 1)
        brightness = data[yi, xi].astype(float)

        if normalize and brightness.size > 0:
            bmin, bmax = float(brightness.min()), float(brightness.max())
            denom = bmax - bmin if bmax > bmin else 1.0
            brightness = (brightness - bmin) / denom

        # figure
        fig, (ax_img, ax_r, ax_b) = plt.subplots(1, 3, figsize=(12, 4), constrained_layout=True)

        # image + points + center
        ax_img.imshow(data, origin="lower", cmap="afmhot")
        ax_img.scatter(x, y, s=12, c="c")
        ax_img.plot([xs], [ys], "wx", ms=8, mew=2)  # chosen center
        ax_img.set_xticks([]); ax_img.set_yticks([])

        # radius vs angle
        ax_r.scatter(angle_clock, radii_px, s=26)
        ax_r.set_xlim(0, 360)
        ax_r.set_xticks([0, 90, 180, 270, 360])
        ax_r.set_xlabel("Angle [deg]")     # 12→0, 3→90, 6→180, 9→270
        ax_r.set_ylabel("Radius [px]")

        # brightness vs angle
        ax_b.scatter(angle_clock, brightness, s=26)
        ax_b.set_xlim(0, 360)
        ax_b.set_xticks([0, 90, 180, 270, 360])
        ax_b.set_xlabel("Angle [deg]")
        ax_b.set_ylabel("Brightness" + (" [norm]" if normalize else ""))

        return fig
