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
        Bright-points version (simple and deterministic):
        - Use `rbp_find_bright_points` to get candidates on the ring.
        - Choose center (default: threshold center `q25`).
        - Convert each point to a clock-style angle relative to center:
            12 o'clock = 0°, 3 o'clock = 90°, 6 o'clock = 180°, 9 o'clock = 270°.
        - Bin angles into `n_angles` equal slices; for each bin keep the *brightest* point.
        - Make three panels: image+all points(+center) | Radius vs Angle | Brightness vs Angle.
          Scatter only, axes labeled; x ticks at [0, 90, 180, 270, 360].
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

        # pick center
        if isinstance(center, (tuple, list, np.ndarray)) and len(center) == 2:
            xs, ys = float(center[0]), float(center[1])
        elif str(center).lower() in ("q25", "threshold", "thresh"):
            xs, ys = self.q25_c
        else:
            xs, ys = self.geo_c

        pts = np.asarray(self.bright_points, float)
        x = pts[:, 0]
        y = pts[:, 1]

        # clock-style angle: y goes up, 12→0°, 3→90°, 6→180°, 9→270°
        dx = x - xs
        dy_up = -(y - ys)
        theta_deg = np.degrees(np.arctan2(dy_up, dx))     # 0°=right, 90°=up
        angles_clock = (90.0 - theta_deg) % 360.0

        # radius (pixels) and brightness at point pixels
        radii_px = np.hypot(dx, y - ys)
        xi = np.clip(np.rint(x).astype(int), 0, data.shape[1] - 1)
        yi = np.clip(np.rint(y).astype(int), 0, data.shape[0] - 1)
        bright_vals = data[yi, xi].astype(float)

        # angle binning → keep brightest per bin for spacing/coverage
        n_bins = int(max(1, n_angles))
        edges = np.linspace(0.0, 360.0, n_bins + 1)
        centers_deg = 0.5 * (edges[:-1] + edges[1:])

        pick_angles = []
        pick_radii = []
        pick_bright = []
        pick_xy = []

        for i in range(n_bins):
            a0, a1 = edges[i], edges[i + 1]
            # include left edge, exclude right edge (last bin handles 360)
            if i < n_bins - 1:
                sel = (angles_clock >= a0) & (angles_clock < a1)
            else:
                sel = (angles_clock >= a0) & (angles_clock <= a1)
            if not np.any(sel):
                continue
            idx = np.argmax(bright_vals[sel])  # brightest in this slice
            sel_idx = np.flatnonzero(sel)[idx]
            pick_angles.append(centers_deg[i])
            pick_radii.append(radii_px[sel_idx])
            pick_bright.append(bright_vals[sel_idx])
            pick_xy.append((x[sel_idx], y[sel_idx]))

        # normalize brightness for right-hand panel
        if normalize and len(pick_bright) > 0:
            pb = np.asarray(pick_bright, float)
            bmin, bmax = float(pb.min()), float(pb.max())
            denom = bmax - bmin if bmax > bmin else 1.0
            pick_bright = ((pb - bmin) / denom).tolist()

        # figure: image+points | radius vs angle | brightness vs angle
        fig, (ax_img, ax_r, ax_b) = plt.subplots(1, 3, figsize=(12, 4), constrained_layout=True)

        # left: show all bright points (cyan), chosen center (white X), and selected per-bin points (white circles)
        ax_img.imshow(data, origin="lower", cmap="afmhot")
        ax_img.scatter(x, y, s=10, c="c")
        ax_img.plot([xs], [ys], "wx", ms=10, mew=2)
        if pick_xy:
            pxy = np.asarray(pick_xy)
            ax_img.scatter(pxy[:, 0], pxy[:, 1], s=28, facecolors="none", edgecolors="w")
        ax_img.set_xticks([])
        ax_img.set_yticks([])

        # middle: radius vs angle
        if pick_angles:
            ax_r.scatter(pick_angles, pick_radii, s=28)
        ax_r.set_xlim(0, 360)
        ax_r.set_xticks([0, 90, 180, 270, 360])
        ax_r.set_xlabel("Angle [deg]")   # 12→0, 3→90, 6→180, 9→270
        ax_r.set_ylabel("Radius [px]")

        # right: brightness vs angle
        if pick_angles:
            ax_b.scatter(pick_angles, pick_bright, s=28)
        ax_b.set_xlim(0, 360)
        ax_b.set_xticks([0, 90, 180, 270, 360])
        ax_b.set_xlabel("Angle [deg]")
        ax_b.set_ylabel("Brightness" + (" [norm]" if normalize else ""))

        return fig
