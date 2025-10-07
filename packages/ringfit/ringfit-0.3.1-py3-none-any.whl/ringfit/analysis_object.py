import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
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

    def plot_angle_profiles(self, n_angles=20, center="auto", step=1.0, normalize=True):
        """
        Simple + robust:
        - Center: 'auto' fits a circle to bright points; else use 'geo'/'q25'/tuple.
        - Cast n equal-angle rays from that center.
        - Search a thin ring band and take the brightest pixel on each ray.
        - Panels: image+points, Radius vs Angle (scatter), Brightness vs Angle (scatter).
        """
        data = self.data
        h, w = data.shape
        eps = 1e-12

        # ensure points (used for center + display)
        if self.bright_points is None:
            self.find_bright_points(threshold=None, radius=None)

        # -------- choose center --------
        r_fit = None  # initialize so it's always defined
        if isinstance(center, (tuple, list, np.ndarray)) and len(center) == 2:
            xs, ys = float(center[0]), float(center[1])
        elif str(center).lower() == "q25":
            xs, ys = self.q25_c
        elif str(center).lower() == "geo":
            xs, ys = self.geo_c
        else:  # auto
            if self.bright_points is not None and len(self.bright_points) >= 3:
                pts = np.asarray(self.bright_points, float)
                x, y = pts[:, 0], pts[:, 1]
                A = np.c_[2 * x, 2 * y, np.ones_like(x)]
                b = x**2 + y**2
                sol, *_ = np.linalg.lstsq(A, b, rcond=None)
                xs, ys, c0 = sol
                r_fit = float(np.sqrt(max(c0 + xs**2 + ys**2, 0.0)))

                # small refinement: minimize radius variance
                def cost(c):
                    r = np.hypot(x - c[0], y - c[1])
                    return np.var(r)
                res = minimize(cost, x0=[xs, ys], method="Powell")
                if res.success:
                    xs, ys = res.x
            else:
                xs, ys = self.q25_c

        # -------- ring band via extraction helpers --------
        try:
            bkg = ex._estimate_background(data)
            r_prof, p_prof = ex._radial_profile(data, xs, ys, bin_size=1.0)
            ps = ex._smooth_profile(p_prof)
            idx = int(np.nanargmax(ps))
            r0_prof = float(r_prof[idx])
            w0 = float(ex._fwhm_width(r_prof, ps, idx, bkg))
            pmax_prof = float(ps[idx])
        except Exception:
            bkg = float(np.percentile(data, 10))
            r0_prof = min(h, w) * 0.3
            w0 = max(1.0, min(h, w) * 0.05)
            pmax_prof = float(np.percentile(data, 99))

        r0 = float(r_fit) if r_fit is not None else r0_prof
        w0 = max(w0, 1.0)
        rmax_img = float(np.hypot(h, w))
        r_lo = max(0.0, r0 - 2.5 * w0)
        r_hi = min(rmax_img, r0 + 2.5 * w0)

        # -------- rays + peak pick --------
        n = int(max(1, n_angles))
        thetas = 2.0 * np.pi * (np.arange(n) / n)
        k = np.array([1, 2, 3, 2, 1], float); k /= k.sum()

        angles_deg, radii_px, peaks, peak_xy = [], [], [], []
        for th in thetas:
            rs = np.arange(r_lo, r_hi, float(max(step, 1.0)))
            if rs.size < 3:
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
            prof_s = np.convolve(prof, k, mode="same")

            j = int(np.argmax(prof_s))
            r_peak = float(rr[j])
            I_peak = float(prof_s[j])

            if normalize:
                # normalize to [0,1] using background and profile peak
                denom = max(pmax_prof - bkg, eps)
                I_peak = (I_peak - bkg) / denom
                I_peak = float(np.clip(I_peak, 0.0, 1.0))

            angles_deg.append(np.degrees(th))
            radii_px.append(r_peak)
            peaks.append(I_peak)
            peak_xy.append((xs + r_peak * np.cos(th), ys + r_peak * np.sin(th)))

        # -------- figure --------
        fig, (ax_img, ax_r, ax_b) = plt.subplots(1, 3, figsize=(12, 4), constrained_layout=True)

        ax_img.imshow(data, origin="lower", cmap="afmhot")
        if self.bright_points is not None and len(self.bright_points) > 0:
            pts = np.asarray(self.bright_points)
            ax_img.scatter(pts[:, 0], pts[:, 1], s=10, c="c")
        if len(peak_xy) > 0:
            pp = np.asarray(peak_xy)
            ax_img.scatter(pp[:, 0], pp[:, 1], s=22, facecolors="none", edgecolors="w")
        ax_img.set_xticks([]); ax_img.set_yticks([])

        if len(angles_deg) > 0:
            ax_r.scatter(angles_deg, radii_px, s=28)
            ax_b.scatter(angles_deg, peaks, s=28)
        ax_r.set_xlabel("Angle [deg]"); ax_r.set_ylabel("Radius [px]")
        ax_b.set_xlabel("Angle [deg]"); ax_b.set_ylabel("Brightness" + (" [norm]" if normalize else ""))

        return fig
