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
        Robust & simple:
        - Get a good center (auto: optimize from bright points; else 'geo'/'q25'/tuple).
        - Cast n equal-angle rays; within a thin annulus, take the brightest pixel.
        - Show: [image + bright points + ray-peak dots] | [Radius vs Angle] | [Brightness vs Angle]
        - Scatter only. Axes labeled only.
        """
        data = self.data
        h, w = data.shape

        # ensure bright points exist (used for auto-center and display)
        if self.bright_points is None:
            self.find_bright_points(threshold=None, radius=None)

        # ---------- choose center ----------
        if isinstance(center, (tuple, list, np.ndarray)) and len(center) == 2:
            xs, ys = float(center[0]), float(center[1])
        elif str(center).lower() == "geo":
            xs, ys = self.geo_c
        elif str(center).lower() == "q25":
            xs, ys = self.q25_c
        else:
            # auto: start from points centroid if available, else threshold center
            if self.bright_points is not None and len(self.bright_points) > 0:
                pts = np.asarray(self.bright_points, float)
                x0, y0 = np.median(pts[:, 0]), np.median(pts[:, 1])

                # refine center by minimizing radius variance (circle-ness)
                def cost(c):
                    r = np.hypot(pts[:, 0] - c[0], pts[:, 1] - c[1])
                    return np.var(r)
                res = minimize(cost, x0=[x0, y0], method="Powell")
                xs, ys = (res.x if res.success else (x0, y0))
            else:
                xs, ys = self.q25_c  # fallback that tracks the ring better than raw geometric

        # ---------- ring band from radial profile (around chosen center) ----------
        bkg = ex._estimate_background(data)
        r_prof, p_prof = ex._radial_profile(data, xs, ys, bin_size=1.0)
        ps = ex._smooth_profile(p_prof)
        peak_idx = int(np.nanargmax(ps))
        r0 = float(r_prof[peak_idx])
        w0 = float(ex._fwhm_width(r_prof, ps, peak_idx, bkg))
        rmax_img = float(np.hypot(h, w))
        r_lo = max(0.0, r0 - 2.0 * w0)
        r_hi = min(rmax_img, r0 + 2.0 * w0)

        # ---------- rays & peak picking ----------
        n = int(max(1, n_angles))
        thetas = 2.0 * np.pi * (np.arange(n) / n)
        k = np.array([1, 2, 3, 2, 1], float); k /= k.sum()  # tiny smooth
        eps = 1e-12

        angles_deg, radii_px, peaks = [], [], []
        ray_peaks_xy = []

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

            angles_deg.append(np.degrees(th))
            radii_px.append(r_peak)
            peaks.append(I_peak)
            ray_peaks_xy.append((xs + r_peak * np.cos(th), ys + r_peak * np.sin(th)))

        # normalize brightness 0..1 if requested
        if normalize and len(peaks) > 0:
            p = np.asarray(peaks, float)
            pmin, pmax = p.min(), p.max()
            denom = max(pmax - pmin, eps)
            peaks = ((p - pmin) / denom).tolist()

        # ---------- figure ----------
        fig, (ax_img, ax_r, ax_b) = plt.subplots(1, 3, figsize=(12, 4), constrained_layout=True)

        # image with points + ray peaks
        ax_img.imshow(data, origin="lower", cmap="afmhot")
        if self.bright_points is not None and len(self.bright_points) > 0:
            pts = np.asarray(self.bright_points)
            ax_img.scatter(pts[:, 0], pts[:, 1], s=8, c="c")
        if len(ray_peaks_xy) > 0:
            rp = np.asarray(ray_peaks_xy)
            ax_img.scatter(rp[:, 0], rp[:, 1], s=18, facecolors="none", edgecolors="w")
        ax_img.set_xticks([]); ax_img.set_yticks([])

        # radius vs angle (scatter)
        if len(angles_deg) > 0:
            ax_r.scatter(angles_deg, radii_px, s=26)
        ax_r.set_xlabel("Angle [deg]")
        ax_r.set_ylabel("Radius [px]")

        # brightness vs angle (scatter)
        if len(angles_deg) > 0:
            ax_b.scatter(angles_deg, peaks, s=26)
        ax_b.set_xlabel("Angle [deg]")
        ax_b.set_ylabel("Brightness" + (" [norm]" if normalize else ""))

        return fig
