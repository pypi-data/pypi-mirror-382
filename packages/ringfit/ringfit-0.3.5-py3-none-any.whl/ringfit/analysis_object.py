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
        """Compute geometric + threshold centers."""
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

    def plot_angle_profiles(
        self,
        n_angles=20,
        center="ring",              # <- use ring-estimated (image-mid) center by default
        normalize=True,
        *,
        threshold_factor=0.01,      # passed to bright point extractor
        mask_mult=5.0,
        reuse_points=True,
    ):
        """
        Bright-points driven version (simple + covers full ring).

        - Center:
            "ring"/"mid"/"image"/"est" -> (xc,yc) from estimate_ring_parameters (image middle)
            "q25"/"threshold"          -> threshold center
            "geo"                       -> geometric center
            (x,y) tuple                 -> use directly
        - Build bright points using estimate_ring_parameters to set threshold+mask.
        - Convert each point to a clock-style angle: 12→0°, 3→90°, 6→180°, 9→270°.
        - Bin the 0..360° range into `n_angles` slices, keep the *brightest* point per slice.
        - Plots: image+points+center | Radius vs Angle (px) | Brightness vs Angle (norm).
        """
        data = self.data

        # --- ring params (also gives us the desired center (xc,yc)) ---
        r_est, w_est, pmax, bkg, (xc, yc) = ex.estimate_ring_parameters(self.image)

        # --- choose center ---
        key = str(center).lower() if not isinstance(center, (tuple, list, np.ndarray)) else "tuple"
        if key == "tuple":
            xs, ys = float(center[0]), float(center[1])
        elif key in ("q25", "threshold", "thresh"):
            xs, ys = self.q25_c
        elif key in ("geo", "geometric"):
            xs, ys = self.geo_c
        else:
            # default: ring-estimated center (image middle)
            xs, ys = float(xc), float(yc)

        # --- ensure we have bright points (tuned to cover whole ring) ---
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
        x = pts[:, 0]
        y = pts[:, 1]

        # --- radius (px) and clock-style angle with origin="lower" (y increases up) ---
        dx = x - xs
        dy = y - ys                      # y-up in display with origin='lower'
        theta_deg = np.degrees(np.arctan2(dy, dx))  # 0°=right, 90°=up
        angles_clock = (90.0 - theta_deg) % 360.0   # shift so 0°=up
        radii_px = np.hypot(dx, dy)

        # brightness at those pixels
        xi = np.clip(np.rint(x).astype(int), 0, data.shape[1] - 1)
        yi = np.clip(np.rint(y).astype(int), 0, data.shape[0] - 1)
        bright_vals = data[yi, xi].astype(float)

        # --- angle binning: keep the brightest per slice to spread points around ---
        n_bins = int(max(1, n_angles))
        edges = np.linspace(0.0, 360.0, n_bins + 1)
        centers_deg = 0.5 * (edges[:-1] + edges[1:])

        pick_angles, pick_radii, pick_bright, pick_xy = [], [], [], []
        for i in range(n_bins):
            a0, a1 = edges[i], edges[i + 1]
            sel = (angles_clock >= a0) & (angles_clock < a1) if i < n_bins - 1 else (angles_clock >= a0) & (angles_clock <= a1)
            if not np.any(sel):
                continue
            j_local = np.argmax(bright_vals[sel])
            j = np.flatnonzero(sel)[j_local]
            pick_angles.append(centers_deg[i])
            pick_radii.append(radii_px[j])
            pick_bright.append(bright_vals[j])
            pick_xy.append((x[j], y[j]))

        # normalize brightness on the panel using ring background/peak
        if normalize and len(pick_bright) > 0:
            pb = np.asarray(pick_bright, float)
            pb = (pb - bkg) / max(pmax - bkg, 1e-12)
            pick_bright = np.clip(pb, 0.0, 1.0).tolist()

        # --- figure ---
        fig, (ax_img, ax_r, ax_b) = plt.subplots(1, 3, figsize=(12, 4), constrained_layout=True)

        # image + all bright points (cyan) + selected per-bin (white circles) + chosen center (white X)
        ax_img.imshow(data, origin="lower", cmap="afmhot")
        ax_img.scatter(x, y, s=10, c="c")
        if pick_xy:
            pxy = np.asarray(pick_xy)
            ax_img.scatter(pxy[:, 0], pxy[:, 1], s=30, facecolors="none", edgecolors="w")
        ax_img.plot([xs], [ys], "wx", ms=12, mew=2)
        ax_img.set_xticks([]); ax_img.set_yticks([])

        # radius vs angle (scatter only)
        if pick_angles:
            ax_r.scatter(pick_angles, pick_radii, s=30)
        ax_r.set_xlim(0, 360)
        ax_r.set_xticks([0, 90, 180, 270, 360])
        ax_r.set_xlabel("Angle [deg]")   # 12→0, 3→90, 6→180, 9→270
        ax_r.set_ylabel("Radius [px]")

        # brightness vs angle (scatter only)
        if pick_angles:
            ax_b.scatter(pick_angles, pick_bright, s=30)
        ax_b.set_xlim(0, 360)
        ax_b.set_xticks([0, 90, 180, 270, 360])
        ax_b.set_xlabel("Angle [deg]")
        ax_b.set_ylabel("Brightness" + (" [norm]" if normalize else ""))

        return fig
