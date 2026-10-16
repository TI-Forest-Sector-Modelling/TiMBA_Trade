"""RAS (iterative proportional fitting) for bilateral trade matrices.

For every commodity a square trade matrix is built (exporters = rows,
importers = columns, plus one extra node "RoW" = Rest of World). The matrix is
then scaled alternately row-wise and column-wise until

    row sums    == export targets   (e.g. FAO exports,  ``row_target_col``)
    column sums == import targets   (e.g. FAO imports,  ``col_target_col``)

Cells without observed bilateral trade stay empty (NaN) in the output, except
for the cells that involve RoW.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from joblib import Parallel, delayed

from src.timba_trade.utils.helper import get_ras_parameters

import logging
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class _Nodes:
    """Nodes of one trade matrix: all countries plus RoW as the last node."""
    countries: list        # sorted country labels (without RoW)
    index: pd.Index        # countries + RoW (position = matrix row/column)
    n_countries: int
    n_nodes: int           # n_countries + 1
    row_idx: int           # position of RoW (= n_countries)


class RAS:
    """
    Balances bilateral trade matrices to given export and import totals.
    """

    def __init__(self):
        self.__dict__.update(get_ras_parameters())

    def fit(self, df):
        """
        Runs RAS separately for every commodity in ``df``.
        """
        commodity_groups = list(df.groupby(self.commodity_col, sort=True))
        logger.debug(f"  Start RAS for {len(commodity_groups)} commodities in '{self.output_dir}'")

        outputs = Parallel(n_jobs=self.n_jobs)(
            delayed(self._fit_commodity)(commodity, group) for commodity, group in commodity_groups
        )
        results = [result for result, _ in outputs]
        diagnostics = [diag for _, diag in outputs]

        for diag in diagnostics:
            if diag["converged"]:
                logger.debug(
                    f"  Commodity: {diag['Commodity']}; Converging after {diag['iterations']} "
                    f"iterations (error = {diag['max_row_error']:.2e})"
                )
            else:
                logger.warning(
                    f"  Commodity: {diag['Commodity']}; Max. iterations ({diag['iterations']}) "
                    f"reached before converging ({diag['max_row_error']:.2e} > error tolerance of {self.tol:.2e})"
                )

        return pd.concat(results, ignore_index=True)

    def _fit_commodity(self, commodity, df):
        """
        Builds, balances and returns the trade matrix of ONE commodity.
        """
        nodes = self._define_nodes(df)
        export_targets, import_targets = self._build_targets(df, nodes)
        exporter_active, importer_active = self._active_masks(export_targets, import_targets, nodes)

        exporter_idx, importer_idx, trade_values, original = self._observed_trade(df, nodes)
        start_matrix, allowed = self._build_start_matrix(
            nodes, exporter_active, importer_active, exporter_idx, importer_idx, trade_values)

        self._balance_totals_via_row(export_targets, import_targets, nodes)
        self._add_row_fallback_cells(
            start_matrix, allowed, export_targets, import_targets,
            exporter_active, importer_active, nodes)

        self._validate_allowed_cells(commodity, nodes, allowed, export_targets, import_targets)
        self._seed_empty_rows(start_matrix, export_targets, import_targets)
        balanced, iterations, converged = self._run_ras_iterations(
            start_matrix, export_targets, import_targets, commodity, nodes)

        result = self._to_long_table(
            commodity, df, nodes, balanced, original, export_targets, import_targets)
        diagnostics = {
            "Commodity": commodity,
            "n_countries": nodes.n_countries,
            "n_original_bilateral_cells": int((~np.isnan(original)).sum()),
            "total_X_q_o": export_targets[:nodes.n_countries].sum(),
            "total_M_q_p": import_targets[:nodes.n_countries].sum(),
            "RoW_exports": export_targets[nodes.row_idx],
            "RoW_imports": import_targets[nodes.row_idx],
            "iterations": iterations,
            "converged": converged,
            "max_row_error": np.abs(balanced.sum(axis=1) - export_targets).max(),
            "max_col_error": np.abs(balanced.sum(axis=0) - import_targets).max(),
        }
        return result, diagnostics

    def _define_nodes(self, df):
        """
        Returns the nodes of the matrix: all countries (sorted) plus RoW last.
        """
        countries = sorted(
            (set(df[self.reporter_col].dropna()) | set(df[self.partner_col].dropna()))
            - {self.row_col}
        )
        n_countries = len(countries)
        return _Nodes(
            countries=countries,
            index=pd.Index(countries + [self.row_col]),
            n_countries=n_countries,
            n_nodes=n_countries + 1,
            row_idx=n_countries,
        )

    def _build_targets(self, df, nodes):
        """
        Returns export targets (row sums) and import targets (column sums).
        """
        n, row_idx, tol = nodes.n_countries, nodes.row_idx, self.tol

        export_targets = np.zeros(nodes.n_nodes)
        import_targets = np.zeros(nodes.n_nodes)
        export_targets[:n] = self._country_targets(
            df, nodes.countries, self.reporter_col, self.row_target_col)
        import_targets[:n] = self._country_targets(
            df, nodes.countries, self.partner_col, self.col_target_col)

        has_trade = df[self.bilateral_col] > 0
        for targets, country_col in ((export_targets, self.reporter_col),
                                     (import_targets, self.partner_col)):
            without_trade = (targets[:n] > tol) & ~nodes.index[:n].isin(
                df.loc[has_trade, country_col])
            targets[row_idx] += targets[:n][without_trade].sum()
            targets[:n][without_trade] = 0.0

        return export_targets, import_targets

    def _country_targets(self, df, countries, group_col, target_col):
        """
        Returns the target value per country (ordered like ``countries``).
        """
        targets = (df.groupby(group_col)[target_col].first()
                   .reindex(countries).fillna(0.0).clip(lower=0.0))
        return targets.where(targets >= self.cutoff, 0.0).to_numpy()

    def _active_masks(self, export_targets, import_targets, nodes):
        """Marks nodes with a positive target (RoW is handled separately -> False)."""
        exporter_active = export_targets > self.tol
        importer_active = import_targets > self.tol
        exporter_active[nodes.row_idx] = importer_active[nodes.row_idx] = False
        return exporter_active, importer_active

    def _observed_trade(self, df, nodes):
        """
        Extracts the valid bilateral observations.
        """
        exporter_idx = nodes.index.get_indexer(df[self.reporter_col])
        importer_idx = nodes.index.get_indexer(df[self.partner_col])
        trade_values = df[self.bilateral_col].to_numpy(float)

        is_valid = (
            ~np.isnan(trade_values) & (trade_values >= 0)
            & (exporter_idx != importer_idx)
            & (exporter_idx >= 0) & (importer_idx >= 0)
        )
        exporter_idx = exporter_idx[is_valid]
        importer_idx = importer_idx[is_valid]
        trade_values = trade_values[is_valid]

        original = np.full((nodes.n_nodes, nodes.n_nodes), np.nan)
        original[exporter_idx, importer_idx] = trade_values
        return exporter_idx, importer_idx, trade_values, original

    def _build_start_matrix(self, nodes, exporter_active, importer_active,
                            exporter_idx, importer_idx, trade_values):
        """
        Builds the start matrix and the mask of allowed (non-empty) cells.
        """
        n, row_idx = nodes.n_countries, nodes.row_idx
        start_matrix = np.zeros((nodes.n_nodes, nodes.n_nodes))
        allowed = np.zeros((nodes.n_nodes, nodes.n_nodes), dtype=bool)

        keep = exporter_active[exporter_idx] & importer_active[importer_idx]
        start_matrix[exporter_idx[keep], importer_idx[keep]] = trade_values[keep]
        allowed[exporter_idx[keep], importer_idx[keep]] = True

        start_matrix[:n, row_idx] = exporter_active[:n].astype(float)
        allowed[:n, row_idx] = exporter_active[:n]
        start_matrix[row_idx, :n] = importer_active[:n].astype(float)
        allowed[row_idx, :n] = importer_active[:n]
        return start_matrix, allowed

    def _balance_totals_via_row(self, export_targets, import_targets, nodes):
        """
        RoW absorbs the difference between total exports and total imports.
        """
        imbalance = export_targets.sum() - import_targets.sum()
        if imbalance > self.tol:
            import_targets[nodes.row_idx] += imbalance
        elif imbalance < -self.tol:
            export_targets[nodes.row_idx] -= imbalance    # imbalance < 0 -> target increases

    def _add_row_fallback_cells(self, start_matrix, allowed, export_targets, import_targets,
                                exporter_active, importer_active, nodes):
        """
        If RoW has a target but no allowed cell, allow cells to/from all active countries.
        """
        n, row_idx, tol = nodes.n_countries, nodes.row_idx, self.tol
        if export_targets[row_idx] > tol and not allowed[row_idx].any():
            start_matrix[row_idx, :n] = importer_active[:n].astype(float)
            allowed[row_idx, :n] = importer_active[:n]
        if import_targets[row_idx] > tol and not allowed[:, row_idx].any():
            start_matrix[:n, row_idx] = exporter_active[:n].astype(float)
            allowed[:n, row_idx] = exporter_active[:n]

    def _validate_allowed_cells(self, commodity, nodes, allowed, export_targets, import_targets):
        """
        Every node with a target needs at least one allowed cell in its row/column.
        """
        for targets, axis, label in ((export_targets, 1, "Reporter"),
                                     (import_targets, 0, "Partner")):
            missing = (targets > self.tol) & ~allowed.any(axis=axis)
            if missing.any():
                raise ValueError(
                    f"Commodity {commodity}: {label} {list(nodes.index[missing])} got targets, "
                    f"but no bilateral trade in cells."
                )

    def _seed_empty_rows(self, start_matrix, export_targets, import_targets):
        """
        Gives rows with a target but an empty start row a start distribution.
        """
        n_nodes = start_matrix.shape[0]
        empty_rows = np.where((start_matrix.sum(axis=1) <= 1e-12) & (export_targets > self.tol))[0]
        if not empty_rows.size:
            return

        weights = (import_targets / import_targets.sum() if import_targets.sum() > 0
                   else np.full(n_nodes, 1.0 / n_nodes))
        row_weights = np.tile(weights, (empty_rows.size, 1))
        row_weights[np.arange(empty_rows.size), empty_rows] = 0.0   # no diagonal
        weight_sums = row_weights.sum(axis=1, keepdims=True)
        row_weights = np.divide(row_weights, weight_sums, out=row_weights, where=weight_sums > 0)
        start_matrix[empty_rows] = export_targets[empty_rows, None] * row_weights

    def _to_long_table(self, commodity, df, nodes, balanced, original,
                       export_targets, import_targets):
        """
        Converts the balanced matrix into a long table (one row per node pair).
        """
        n_nodes = nodes.n_nodes
        is_country = np.arange(n_nodes) != nodes.row_idx
        output_values = np.where(
            np.isnan(original) & np.outer(is_country, is_country), np.nan, balanced)

        return pd.DataFrame({
            self.reporter_col: np.repeat(nodes.index.to_numpy(object), n_nodes),
            self.partner_col: np.tile(nodes.index.to_numpy(object), n_nodes),
            self.commodity_col: commodity,
            self.period_col: df[self.period_col].iloc[0],
            self.row_target_col: np.repeat(export_targets, n_nodes),
            self.col_target_col: np.tile(import_targets, n_nodes),
            self.bilateral_col: output_values.ravel(),
            "Export_bilateral_original": original.ravel(),
            "RAS_adjusted": ~np.isnan(original).ravel(),
        })

    def _run_ras_iterations(self, start_matrix, export_targets, import_targets, commodity, nodes):
        """
        Alternately scales rows and columns until the row sums match the targets.
        """
        matrix, tol = start_matrix.copy(), self.tol

        def scaling_factors(current_sums, target_sums, axis_name, iteration):
            """Factor per row/column: target / current sum (1 where sum is 0)."""
            unscalable = (current_sums <= tol) & (target_sums > tol)
            if unscalable.any():
                raise ValueError(
                    f"Commodity {commodity}: RAS aborted (Iteration {iteration}). "
                    f"{axis_name} without value for target: {list(nodes.index[unscalable])}"
                )
            return np.divide(target_sums, current_sums,
                             out=np.ones_like(current_sums), where=current_sums > 0)

        row_sums = matrix.sum(axis=1)
        for iteration in range(1, self.max_iter + 1):
            matrix *= scaling_factors(row_sums, export_targets, "row", iteration)[:, None]
            matrix *= scaling_factors(matrix.sum(axis=0), import_targets, "column", iteration)
            row_sums = matrix.sum(axis=1)
            max_error = np.abs(row_sums - export_targets).max()
            if max_error < tol:
                return matrix, iteration, True

        return matrix, self.max_iter, False
