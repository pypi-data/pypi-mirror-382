import numpy as np
import matplotlib.pyplot as plt
from . import extraction as ex
from . import utils

class AnalysisObject:
    """Hold image, find points, quick plots."""

    def __init__(self, im):
        """Load image + stash metadata."""
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
        """Compute geometric + threshold centers (simple mask centroid)."""
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

    # --- helper: circle center from points (Kasa fit) ---
    @staticmethod
    def _fit_circle_center(points):
        """Least-squares circle center from (N,2) points. Falls back to their mean."""
        pts = np.asarray(points, float)
        if pts.ndim != 2 or pts.shape[1] != 2 or len(pts) < 3:
            return float(np.mean(pts[:, 0])), float(np.mean(pts[:, 1]))
        x, y = pts[:, 0], pts[:, 1]
        A = np.c_[2 * x, 2 * y, np.ones_like(x)]
        b = x**2 + y**2
        sol, *_ = np.linalg.lstsq(A, b, rcond=None)
        xc, yc, _ = sol
        return float(xc), float(yc)

    def plot_angle_profiles(
        self,
        n_angles=20,
        center="fit",            # <<< main change: default to *fitted* center from bright points
        normalize=True,
        *,
        threshold_factor=0.01,   # for bright-point extraction
        mask_mult=5.0,
        reuse_points=True,
    ):
        """
        Make 3 panels using bright points and a *fitted* ring center:
        left=image+points, middle=radius vs angle, right=brightness vs angle.

        Center options:
          - "fit" (default): circle-center from *all* bright points (robust + centered)
          - "q25": threshold center
          - "geo": geometric center
          - "ring"/"est": center from estimate_ring_parameters
          - (x,y) tuple: explicit pixel coords
        Angles are clock-style: 12→0°, 3→90°, 6→180°, 9→270°.
        """
        data = self.data

        # ring stats (to seed bright-point extraction + brightness normalization)
        r_est, w_est, pmax, bkg, (xc_est, yc_est) = ex.estimate_ring_parameters(self.image)

        # ensure we have lots of bright points around the ring
        need_points = (self.bright_points is None) or (not reuse_points) or (len(self.bright_points) == 0)
        if need_points:
            thr = bkg + float(threshold_factor) * (pmax - bkg)
            mask_r = max(1.0, float(mask_mult) * w_est)
            self.find_bright_points(threshold=thr, radius=mask_r)
        if self.bright_points is None or len(self.bright_points) == 0:
            fig, ax = plt.subplots(1, 1, figsize=(5, 4))
            ax.text(0.5, 0.5, "No bright points found", ha="center", va="center")
            ax.set_axis_off()
            return fig

        pts = np.asarray(self.bright_points, float)
        x_all, y_all = pts[:, 0], pts[:, 1]

        # --- choose the center (KEY FIX) ---
        if isinstance(center, (tuple, list, np.ndarray)) and len(center) == 2:
            xs, ys = float(center[0]), float(center[1])
        else:
            key = str(center).lower()
            if key in ("q25", "threshold", "thresh"):
                xs, ys = self.q25_c
            elif key in ("geo", "geometric"):
                xs, ys = self.geo_c
            elif key in ("ring", "est", "mid", "image"):
                xs, ys = float(xc_est), float(yc_est)
            else:
                # default: fit a circle center from *all* bright points
                xs, ys = self._fit_circle_center(pts)

        # compute angles/radii/brightness for all bright points wrt chosen center
        dx_all, dy_all = x_all - xs, y_all - ys           # origin='lower' → y increases upward
        theta_deg_all = np.degrees(np.arctan2(dy_all, dx_all))   # 0°=right, 90°=up
        angles_clock_all = (90.0 - theta_deg_all) % 360.0
        radii_px_all = np.hypot(dx_all, dy_all)

        xi_all = np.clip(np.rint(x_all).astype(int), 0, data.shape[1] - 1)
        yi_all = np.clip(np.rint(y_all).astype(int), 0, data.shape[0] - 1)
        bright_all = data[yi_all, xi_all].astype(float)

        # bin 0..360° into n slices; keep the brightest point per slice (spreads coverage)
        n_bins = int(max(1, n_angles))
        edges = np.linspace(0.0, 360.0, n_bins + 1)
        centers_deg = 0.5 * (edges[:-1] + edges[1:])

        pick_angles, pick_radii, pick_bright, pick_xy = [], [], [], []
        for i in range(n_bins):
            a0, a1 = edges[i], edges[i + 1]
            sel = (angles_clock_all >= a0) & (angles_clock_all < a1) if i < n_bins - 1 else (angles_clock_all >= a0) & (angles_clock_all <= a1)
            if not np.any(sel):
                continue
            j_local = np.argmax(bright_all[sel])
            j = np.flatnonzero(sel)[j_local]
            pick_angles.append(centers_deg[i])
            pick_radii.append(radii_px_all[j])
            pick_bright.append(bright_all[j])
            pick_xy.append((x_all[j], y_all[j]))

        # normalize brightness panel using ring background/peak
        if normalize and len(pick_bright) > 0:
            pb = (np.asarray(pick_bright) - bkg) / max(pmax - bkg, 1e-12)
            pick_bright = np.clip(pb, 0.0, 1.0).tolist()

        # --- figure ---
        fig, (ax_img, ax_r, ax_b) = plt.subplots(1, 3, figsize=(12, 4), constrained_layout=True)

        # left: all bright points (cyan), selected per-bin (white circles), chosen center (white X)
        ax_img.imshow(data, origin="lower", cmap="afmhot")
        ax_img.scatter(x_all, y_all, s=10, c="c")
        if pick_xy:
            selxy = np.asarray(pick_xy)
            ax_img.scatter(selxy[:, 0], selxy[:, 1], s=30, facecolors="none", edgecolors="w")
        ax_img.plot([xs], [ys], "wx", ms=12, mew=2)
        ax_img.set_xticks([]); ax_img.set_yticks([])

        # middle: radius vs angle
        if pick_angles:
            ax_r.scatter(pick_angles, pick_radii, s=30)
        ax_r.set_xlim(0, 360)
        ax_r.set_xticks([0, 90, 180, 270, 360])
        ax_r.set_xlabel("Angle [deg]")   # 12→0, 3→90, 6→180, 9→270
        ax_r.set_ylabel("Radius [px]")

        # right: brightness vs angle
        if pick_angles:
            ax_b.scatter(pick_angles, pick_bright, s=30)
        ax_b.set_xlim(0, 360)
        ax_b.set_xticks([0, 90, 180, 270, 360])
        ax_b.set_xlabel("Angle [deg]")
        ax_b.set_ylabel("Brightness" + (" [norm]" if normalize else ""))

        return fig
