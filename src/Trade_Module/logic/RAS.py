import numpy as np
import pandas as pd
from joblib import Parallel, delayed

from src.Trade_Module.core.OutputManager import OutputManager
from src.Trade_Module.utils.helper import get_ras_parameters

import logging
logger = logging.getLogger(__name__)
 
 
class RAS: 
    def __init__(self):
        self.__dict__.update(get_ras_parameters())
        self.om = OutputManager()

    def fit(self, df):
        groups = list(df.groupby(self.commodity_col, sort=True))
        logger.debug(f"  Start RAS for {len(groups)} commodities in '{self.output_dir}'")
 
        out = Parallel(n_jobs=self.n_jobs)(
            delayed(self._fit_commodity)(c, g) for c, g in groups
        )

        results, diagnostics = ([o[i] for o in out] for i in (0, 1))

        for d in diagnostics:
            if d["converged"]:
                logger.debug(
                    f"  Commodity: {d['Commodity']}; Converging after {d['iterations']} "
                    f"iterations (error = {d['max_row_error']:.2e})"
                )
            else:
                logger.warning(
                    f"  Commodity: {d['Commodity']}; Max. iterations ({d['iterations']}) "
                    f"reached before converging ({d['max_row_error']:.2e} > error tolerance of {self.tol:.2e})"
                )
        combined_res = pd.concat(results, ignore_index=True)

        return combined_res
 
    def _fit_commodity(self, commodity, df):
        rc, pc, bc, tol = self.reporter_col, self.partner_col, self.bilateral_col, self.tol
        countries = sorted((set(df[rc].dropna()) | set(df[pc].dropna())) - {self.row_col})
 
        n = len(countries)
        N = n + 1                      # RoW
        R = n
        nodes = pd.Index(countries + [self.row_col])

        def targets(key, col):
            s = (df.groupby(key)[col].first().reindex(countries)
                 .fillna(0.0).clip(lower=0.0))
            return s.where(s >= self.cutoff, 0.0).to_numpy()
 
        tr, tc = np.zeros(N), np.zeros(N)
        tr[:n], tc[:n] = targets(rc, self.row_target_col), targets(pc, self.col_target_col)
 
        pos = df[bc] > 0
        for t, key in ((tr, rc), (tc, pc)):
            shift = (t[:n] > tol) & ~nodes[:n].isin(df.loc[pos, key])
            t[R] += t[:n][shift].sum()
            t[:n][shift] = 0.0
 
        rpos, cpos = tr > tol, tc > tol
        rpos[R] = cpos[R] = False

        ri, pi_ = nodes.get_indexer(df[rc]), nodes.get_indexer(df[pc])
        vals = df[bc].to_numpy(float)
        valid = (~np.isnan(vals) & (vals >= 0) & (ri != pi_) & (ri >= 0) & (pi_ >= 0))
        ri, pi_, vals = ri[valid], pi_[valid], vals[valid]
 
        orig = np.full((N, N), np.nan)
        orig[ri, pi_] = vals
 
        T = np.zeros((N, N))
        adj = np.zeros((N, N), dtype=bool)
        m = rpos[ri] & cpos[pi_]
        T[ri[m], pi_[m]] = vals[m]
        adj[ri[m], pi_[m]] = True

        T[:n, R], adj[:n, R] = rpos[:n].astype(float), rpos[:n]
        T[R, :n], adj[R, :n] = cpos[:n].astype(float), cpos[:n]
 
        imb = tr.sum() - tc.sum()
        if imb > tol:
            tc[R] += imb
        elif imb < -tol:
            tr[R] -= imb

        if tr[R] > tol and not adj[R].any():
            T[R, :n] = cpos[:n].astype(float)
            adj[R, :n] = cpos[:n]
        if tc[R] > tol and not adj[:, R].any():
            T[:n, R] = rpos[:n].astype(float)
            adj[:n, R] = rpos[:n]
 
        # validation
        for target, ax, label in ((tr, 1, "Reporter"), (tc, 0, "Partner")):
            bad = (target > tol) & ~adj.any(axis=ax)
            if bad.any():
                raise ValueError(
                    f"Commodity {commodity}: {label} {list(nodes[bad])} got targets, "
                    f"but no bilateral trade in cells."
                )
 
        zero_rows = np.where((T.sum(axis=1) <= 1e-12) & (tr > tol))[0]
        if zero_rows.size:
            w = tc / tc.sum() if tc.sum() > 0 else np.full(N, 1.0 / N)
            W = np.tile(w, (zero_rows.size, 1))
            W[np.arange(zero_rows.size), zero_rows] = 0.0
            s = W.sum(axis=1, keepdims=True)
            W = np.divide(W, s, out=W, where=s > 0)
            T[zero_rows] = tr[zero_rows, None] * W
 
        T_ras, iters, converged = self._ras(T, tr, tc, commodity, nodes)
 
        rr, cc = np.repeat(nodes.to_numpy(object), N), np.tile(nodes.to_numpy(object), N)
        non_row = np.arange(N) != R
        out_vals = np.where(np.isnan(orig) & np.outer(non_row, non_row), np.nan, T_ras)
        result = pd.DataFrame({
            rc: rr, pc: cc, self.commodity_col: commodity, self.period_col: df[self.period_col].iloc[0],
            self.row_target_col: np.repeat(tr, N), self.col_target_col: np.tile(tc, N),
            bc: out_vals.ravel(),
            "Export_bilateral_original": orig.ravel(),
            "RAS_adjusted": ~np.isnan(orig).ravel(),
        })
 
        diag = {
            "Commodity": commodity,
            "n_countries": n,
            "n_original_bilateral_cells": int((~np.isnan(orig)).sum()),
            "total_X_q_o": tr[:n].sum(),
            "total_M_q_p": tc[:n].sum(),
            "RoW_exports": tr[R],
            "RoW_imports": tc[R],
            "iterations": iters,
            "converged": converged,
            "max_row_error": np.abs(T_ras.sum(axis=1) - tr).max(),
            "max_col_error": np.abs(T_ras.sum(axis=0) - tc).max(),
        }
        return result, diag

    def _ras(self, T0, tr, tc, commodity, nodes):
        T, tol = T0.copy(), self.tol
 
        def scale(sums, target, axis_name, it):
            bad = (sums <= tol) & (target > tol)
            if bad.any():
                raise ValueError(
                    f"Commodity {commodity}: RAS aborted (Iteration {it}). "
                    f"{axis_name} without value for target: {list(nodes[bad])}"
                )
            return np.divide(target, sums, out=np.ones_like(sums), where=sums > 0)
 
        rs = T.sum(axis=1)
        for i in range(1, self.max_iter + 1):
            T *= scale(rs, tr, "row", i)[:, None]
            T *= scale(T.sum(axis=0), tc, "column", i)
            rs = T.sum(axis=1)
            err = np.abs(rs - tr).max()
            if err < tol:
                return T, i, True
 
        return T, self.max_iter, False
 