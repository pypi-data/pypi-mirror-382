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
        """Compute easy reference centers."""
        self.geo_c = utils.geometric_centroid(self.data)
        self.q25_c = utils.threshold_center(self.data, q=25)

    def find_bright_points(self, threshold=0.5, radius=5.0, margin=None, max_it=999):
        """Grab bright points with recursive blanking."""
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

    # ---------- super simple circle helpers (no SciPy needed) ----------

    @staticmethod
    def _kasa_center(points):
        """Least-squares (Kåsa) circle center from points."""
        pts = np.asarray(points, float)
        x, y = pts[:, 0], pts[:, 1]
        A = np.c_[2 * x, 2 * y, np.ones_like(x)]
        b = x * x + y * y
        sol, *_ = np.linalg.lstsq(A, b, rcond=None)
        cx, cy, _ = sol
        return float(cx), float(cy)

    @staticmethod
    def _even_by_angle(points, values, center, nbins):
        """
        Keep the *brightest* point in each angle bin around `center`.
        This forces even angular coverage and kills bias from a single bright arc.
        """
        pts = np.asarray(points, float)
        vals = np.asarray(values, float)
        cx, cy = center
        ang = (90.0 - np.degrees(np.arctan2(pts[:, 1] - cy, pts[:, 0] - cx))) % 360.0
        edges = np.linspace(0.0, 360.0, int(max(1, nbins)) + 1)
        keep_idx = []
        for i in range(len(edges) - 1):
            a0, a1 = edges[i], edges[i + 1]
            sel = (ang >= a0) & (ang < a1) if i < len(edges) - 2 else (ang >= a0) & (ang <= a1)
            if np.any(sel):
                loc = np.argmax(vals[sel])
                keep_idx.append(np.flatnonzero(sel)[loc])
        if not keep_idx:
            return pts[:0], vals[:0]
        keep_idx = np.asarray(keep_idx, int)
        return pts[keep_idx], vals[keep_idx]

    # ---------- main plot (new center logic kept dead simple) ----------

    def plot_angle_profiles(
        self,
        n_angles=20,
        center="auto",          # <- new default: robust center (bin -> fit -> bin -> fit)
        normalize=True,
        *,
        threshold_factor=0.01,  # for bright-point extraction
        mask_mult=5.0,
        reuse_points=True,
    ):
        """
        Make 3 panels: image+points | Radius vs Angle | Brightness vs Angle.
        Angles are "clock style": 12→0°, 3→90°, 6→180°, 9→270°. Scatter only.

        Center picking (simple and robust):
          auto  = start at image middle, pick brightest per angle bin, fit circle (Kåsa),
                  re-bin with that center and fit once more. Done.
          q25   = threshold center from `utils.threshold_center`
          geo   = geometric centroid
          ring  = (xc,yc) from `estimate_ring_parameters`
          (x,y) = explicit pixels
        """
        data = self.data
        H, W = data.shape

        # --- seed ring params (also gives bkg/pmax for brightness norm) ---
        r_est, w_est, pmax, bkg, (xc_est, yc_est) = ex.estimate_ring_parameters(self.image)

        # --- make sure we have lots of bright points ---
        if self.bright_points is None or (not reuse_points) or len(self.bright_points) == 0:
            thr = bkg + float(threshold_factor) * (pmax - bkg)
            self.find_bright_points(threshold=thr, radius=max(1.0, float(mask_mult) * w_est))
        if self.bright_points is None or len(self.bright_points) == 0:
            fig, ax = plt.subplots(1, 1, figsize=(5, 4))
            ax.text(0.5, 0.5, "No bright points found", ha="center", va="center")
            ax.set_axis_off()
            return fig

        pts = np.asarray(self.bright_points, float)
        # per-point brightness (for bin selection and the right panel)
        xi = np.clip(np.rint(pts[:, 0]).astype(int), 0, W - 1)
        yi = np.clip(np.rint(pts[:, 1]).astype(int), 0, H - 1)
        vals = data[yi, xi].astype(float)

        # --- choose center (keep it *very* simple) ---
        if isinstance(center, (tuple, list, np.ndarray)) and len(center) == 2:
            cx, cy = float(center[0]), float(center[1])
        else:
            k = str(center).lower()
            if k == "geo":
                cx, cy = self.geo_c
            elif k in ("q25", "threshold", "thresh"):
                cx, cy = self.q25_c
            elif k in ("ring", "est"):
                cx, cy = float(xc_est), float(yc_est)
            else:
                # --- AUTO: image middle → even-angle subset → Kåsa fit (x2) ---
                c0 = ((W - 1) / 2.0, (H - 1) / 2.0)
                sub1, v1 = self._even_by_angle(pts, vals, c0, nbins=max(24, n_angles))
                c1 = self._kasa_center(sub1) if len(sub1) >= 3 else c0
                sub2, v2 = self._even_by_angle(pts, vals, c1, nbins=max(24, n_angles))
                c2 = self._kasa_center(sub2) if len(sub2) >= 3 else c1
                cx, cy = c2

        # --- final per-bin selection for the plots using the chosen center ---
        angles = (90.0 - np.degrees(np.arctan2(pts[:, 1] - cy, pts[:, 0] - cx))) % 360.0
        radii = np.hypot(pts[:, 0] - cx, pts[:, 1] - cy)

        # pick brightest in each of the requested bins (n_angles)
        edges = np.linspace(0.0, 360.0, int(max(1, n_angles)) + 1)
        mid_deg = 0.5 * (edges[:-1] + edges[1:])
        pick_ang, pick_rad, pick_val, pick_xy = [], [], [], []
        for i in range(len(edges) - 1):
            a0, a1 = edges[i], edges[i + 1]
            sel = (angles >= a0) & (angles < a1) if i < len(edges) - 2 else (angles >= a0) & (angles <= a1)
            if np.any(sel):
                jloc = np.argmax(vals[sel])
                j = np.flatnonzero(sel)[jloc]
                pick_ang.append(mid_deg[i])
                pick_rad.append(radii[j])
                pick_val.append(vals[j])
                pick_xy.append((pts[j, 0], pts[j, 1]))

        # normalize brightness for right panel (simple 0..1 using bkg/pmax)
        if normalize and pick_val:
            pv = (np.asarray(pick_val) - bkg) / max(pmax - bkg, 1e-12)
            pick_val = np.clip(pv, 0.0, 1.0).tolist()

        # --- plot: image | radius vs angle | brightness vs angle ---
        fig, (ax_img, ax_r, ax_b) = plt.subplots(1, 3, figsize=(12, 4), constrained_layout=True)

        ax_img.imshow(data, origin="lower", cmap="afmhot")
        ax_img.scatter(pts[:, 0], pts[:, 1], s=10, c="c")
        if pick_xy:
            sel = np.asarray(pick_xy)
            ax_img.scatter(sel[:, 0], sel[:, 1], s=30, facecolors="none", edgecolors="w")
        ax_img.plot([cx], [cy], "wx", ms=12, mew=2)  # the center actually used
        ax_img.set_xticks([]); ax_img.set_yticks([])

        if pick_ang:
            ax_r.scatter(pick_ang, pick_rad, s=30)
            ax_b.scatter(pick_ang, pick_val, s=30)
        for ax in (ax_r, ax_b):
            ax.set_xlim(0, 360)
            ax.set_xticks([0, 90, 180, 270, 360])
            ax.set_xlabel("Angle [deg]")
        ax_r.set_ylabel("Radius [px]")
        ax_b.set_ylabel("Brightness" + (" [norm]" if normalize else ""))

        return fig
