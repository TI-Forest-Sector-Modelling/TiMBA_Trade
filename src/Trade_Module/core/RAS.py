import os
import numpy as np
import pandas as pd


class RAS:
    """
    Biproportionale Anpassung (RAS) bilateraler Handelsdaten.
    """

    def __init__(
        self,
        reporter_col="Reporter",
        partner_col="Partner",
        commodity_col="Commodity",
        period_col="Period",
        row_target_col="X_q_o",
        col_target_col="M_q_p",
        bilateral_col="Export_bilateral",
        output_dir="ras_output",
        max_iter=10000,
        tol=1e-10,
        row_col="RoW",
        cutoff=1e-1,
        verbose=True,
    ):
        self.reporter_col = reporter_col
        self.partner_col = partner_col
        self.commodity_col = commodity_col
        self.period_col = period_col
        self.row_target_col = row_target_col
        self.col_target_col = col_target_col
        self.bilateral_col = bilateral_col
        self.output_dir = output_dir
        self.max_iter = max_iter
        self.tol = tol
        self.row_col = row_col
        self.cutoff = cutoff
        self.verbose = verbose

        os.makedirs(self.output_dir, exist_ok=True)

    # ==================================================================
    # PUBLIC API
    # ==================================================================

    def fit(self, df):
        df = df.copy()
        required_cols = [
            self.reporter_col,
            self.partner_col,
            self.commodity_col,
            self.row_target_col,
            self.col_target_col,
            self.bilateral_col,
        ]
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            raise ValueError(f"Folgende Spalten fehlen im DataFrame: {missing}")

        if self.period_col not in df.columns:
            df[self.period_col] = 0

        commodities = sorted(df[self.commodity_col].dropna().unique())
        if self.verbose:
            print(f"Starte RAS für {len(commodities)} Commodities in '{self.output_dir}'")

        results, diagnostics = [], []

        for idx, commodity in enumerate(commodities, start=1):
            if self.verbose:
                print(f"[{idx}/{len(commodities)}] Commodity: {commodity}")

            commodity_df = df[df[self.commodity_col] == commodity].copy()
            result, diag = self._fit_commodity(commodity_df, commodity)

            results.append(result)
            diagnostics.append(diag)

            commodity_str = str(commodity).replace(".", "_")
            output_file = os.path.join(self.output_dir, f"RAS_Commodity_{commodity_str}.csv")
            result.to_csv(output_file, index=False)

        diagnostics_df = pd.DataFrame(diagnostics)
        diagnostics_file = os.path.join(self.output_dir, "RAS_diagnostics.csv")
        diagnostics_df.to_csv(diagnostics_file, index=False)

        if self.verbose:
            print(f"\nDiagnostik gespeichert unter: {diagnostics_file}\nRAS erfolgreich abgeschlossen.")

        return results

    # ==================================================================
    # COMMODITY FIT
    # ==================================================================

    def _fit_commodity(self, df, commodity):
        reporters = set(df[self.reporter_col].dropna().unique())
        partners = set(df[self.partner_col].dropna().unique())
        countries = sorted((reporters | partners) - {self.row_col})

        if not countries:
            raise ValueError(f"Commodity {commodity}: Keine gültigen Länder gefunden.")

        # Randsummen extrahieren
        row_targets = (
            df.groupby(self.reporter_col)[self.row_target_col]
            .first()
            .reindex(countries)
            .fillna(0.0)
            .clip(lower=0.0)
        )
        col_targets = (
            df.groupby(self.partner_col)[self.col_target_col]
            .first()
            .reindex(countries)
            .fillna(0.0)
            .clip(lower=0.0)
        )

        # Cutoff für extrem kleine Zielwerte anwenden
        row_targets = row_targets.where(row_targets >= self.cutoff, 0.0)
        col_targets = col_targets.where(col_targets >= self.cutoff, 0.0)

        # --------------------------------------------------------------
        # 1. PRÜFUNG & ZIEL-VERSCHIEBUNG NACH RoW
        # --------------------------------------------------------------
        row_targets_row_val = 0.0
        col_targets_row_val = 0.0

        for c in countries:
            has_row_mass = ((df[self.reporter_col] == c) & (df[self.bilateral_col] > 0)).any()
            if row_targets.get(c, 0.0) > self.tol and not has_row_mass:
                row_targets_row_val += row_targets.loc[c]
                row_targets.loc[c] = 0.0

            has_col_mass = ((df[self.partner_col] == c) & (df[self.bilateral_col] > 0)).any()
            if col_targets.get(c, 0.0) > self.tol and not has_col_mass:
                col_targets_row_val += col_targets.loc[c]
                col_targets.loc[c] = 0.0

        all_nodes = countries + [self.row_col]
        N = len(all_nodes)
        node_idx = {c: i for i, c in enumerate(all_nodes)}
        row_idx_row = node_idx[self.row_col]

        # Gültige bilaterale Handelsbeziehungen identifizieren
        valid_bilateral = (
            df[self.bilateral_col].notna()
            & (df[self.reporter_col] != df[self.partner_col])
            & (df[self.bilateral_col] >= 0)
        )

        # Matrix T und Masken initialisieren
        T = np.zeros((N, N), dtype=float)
        adjustable = np.zeros((N, N), dtype=bool)
        original_values = {}

        # 2. Bilaterale Werte eintragen
        for _, row in df[valid_bilateral].iterrows():
            r, p, val = row[self.reporter_col], row[self.partner_col], float(row[self.bilateral_col])
            if r in node_idx and p in node_idx:
                if row_targets.get(r, 0.0) > self.tol and col_targets.get(p, 0.0) > self.tol:
                    i, j = node_idx[r], node_idx[p]
                    T[i, j] = val
                    adjustable[i, j] = True
                original_values[(r, p)] = val

        # --------------------------------------------------------------
        # 3. RoW Support-Zellen hinzufügen
        # --------------------------------------------------------------
        for country in countries:
            i = node_idx[country]
            if row_targets.loc[country] > self.tol:
                T[i, row_idx_row] = 1.0
                adjustable[i, row_idx_row] = True

            if col_targets.loc[country] > self.tol:
                T[row_idx_row, i] = 1.0
                adjustable[row_idx_row, i] = True

        T[row_idx_row, row_idx_row] = 0.0
        adjustable[row_idx_row, row_idx_row] = False

        # Target-Vektoren aufbauen
        target_rows = np.zeros(N)
        target_cols = np.zeros(N)
        for country in countries:
            i = node_idx[country]
            target_rows[i] = row_targets.loc[country]
            target_cols[i] = col_targets.loc[country]

        target_rows[row_idx_row] = row_targets_row_val
        target_cols[row_idx_row] = col_targets_row_val

        # RoW Target-Anpassung über Ausgleichsbilanz
        imbalance = target_rows.sum() - target_cols.sum()
        if imbalance > self.tol:
            target_cols[row_idx_row] += imbalance
        elif imbalance < -self.tol:
            target_rows[row_idx_row] += -imbalance

        # --------------------------------------------------------------
        # 4. Fallback Schutz für RoW (Verhindert 0.0 Spalten-/Zeilensumme)
        # --------------------------------------------------------------
        if target_rows[row_idx_row] > self.tol and not adjustable[row_idx_row, :].any():
            for country in countries:
                i = node_idx[country]
                T[row_idx_row, i] = 1.0
                adjustable[row_idx_row, i] = True

        if target_cols[row_idx_row] > self.tol and not adjustable[:, row_idx_row].any():
            for country in countries:
                i = node_idx[country]
                T[i, row_idx_row] = 1.0
                adjustable[i, row_idx_row] = True

        # Validierung der Anpassbarkeit
        for i, node in enumerate(all_nodes):
            if target_rows[i] > self.tol and not adjustable[i, :].any():
                raise ValueError(
                    f"Commodity {commodity}: Reporter '{node}' hat X_q_o={target_rows[i]}, aber keine zulässigen RAS-Zellen."
                )
            if target_cols[i] > self.tol and not adjustable[:, i].any():
                raise ValueError(
                    f"Commodity {commodity}: Partner '{node}' hat M_q_p={target_cols[i]}, aber keine zulässigen RAS-Zellen."
                )

        # --------------------------------------------------------------
        # 5. Null-Zeilen-Auffüllung (Behandelt Exporteure ohne Matrix-Masse)
        # --------------------------------------------------------------
        zero_rows = (T.sum(axis=1) <= 1e-12) & (target_rows > self.tol)

        if np.any(zero_rows):
            col_weights = target_cols.copy()
            col_weights_sum = col_weights.sum()

            if col_weights_sum > 0:
                col_weights /= col_weights_sum
            else:
                col_weights = np.ones_like(col_weights) / len(col_weights)

            for idx in np.where(zero_rows)[0]:
                weights = col_weights.copy()
                weights[idx] = 0.0  # Eigenhandel vermeiden

                if weights.sum() > 0:
                    weights /= weights.sum()

                T[idx, :] = target_rows[idx] * weights

        # --------------------------------------------------------------
        # 6. RAS Ausführung
        # --------------------------------------------------------------
        T_ras, iterations, converged = self._ras(
            T, target_rows, target_cols, commodity, node_names=all_nodes
        )

        # Ergebnis-DataFrame erstellen
        result = self._matrix_to_dataframe(
            T_ras, all_nodes, countries, commodity, target_rows, target_cols, original_values
        )

        final_row_sums = T_ras.sum(axis=1)
        final_col_sums = T_ras.sum(axis=0)

        diag = {
            "Commodity": commodity,
            "n_countries": len(countries),
            "n_original_bilateral_cells": len(original_values),
            "total_X_q_o": target_rows[: len(countries)].sum(),
            "total_M_q_p": target_cols[: len(countries)].sum(),
            "RoW_exports": target_rows[row_idx_row],
            "RoW_imports": target_cols[row_idx_row],
            "iterations": iterations,
            "converged": converged,
            "max_row_error": np.max(np.abs(final_row_sums - target_rows)),
            "max_col_error": np.max(np.abs(final_col_sums - target_cols)),
        }

        return result, diag

    # ==================================================================
    # VEKTORISIERTER RAS-ALGORITHMUS
    # ==================================================================

    def _ras(self, matrix, target_rows, target_cols, commodity, node_names=None):
        T = matrix.copy()

        for iteration in range(1, self.max_iter + 1):
            # 1. Zeilenanpassung
            row_sums = T.sum(axis=1)
            row_mask = target_rows > self.tol
            problem_rows = (row_sums <= self.tol) & row_mask

            if np.any(problem_rows):
                prob_indices = np.where(problem_rows)[0]
                print(
                    f"\n[FEHLER-DIAGNOSE] Commodity {commodity} bei Zeilenanpassung in Iteration {iteration}:"
                )
                for idx in prob_indices:
                    node_label = node_names[idx] if node_names else f"Index {idx}"
                    print(f"  -> Problem-Land (Zeile/Exporter): '{node_label}'")
                    print(
                        f"     Soll-Zielwert: {target_rows[idx]}, Ist-Zeilensumme: {row_sums[idx]}"
                    )

                raise ValueError(
                    f"Commodity {commodity}: RAS abgebrochen. Zeile besitzt keine Masse für Zielwert."
                )

            row_factors = np.where(
                row_sums > 0, target_rows / np.maximum(row_sums, 1e-15), 1.0
            )
            T *= row_factors[:, np.newaxis]

            # 2. Spaltenanpassung
            col_sums = T.sum(axis=0)
            col_mask = target_cols > self.tol
            problem_cols = (col_sums <= self.tol) & col_mask

            if np.any(problem_cols):
                prob_indices = np.where(problem_cols)[0]
                print(
                    f"\n[FEHLER-DIAGNOSE] Commodity {commodity} bei Spaltenanpassung in Iteration {iteration}:"
                )
                for idx in prob_indices:
                    node_label = node_names[idx] if node_names else f"Index {idx}"
                    print(f"  -> Problem-Land (Spalte/Importer): '{node_label}'")
                    print(
                        f"     Soll-Zielwert: {target_cols[idx]}, Ist-Spaltensumme: {col_sums[idx]}"
                    )

                raise ValueError(
                    f"Commodity {commodity}: RAS abgebrochen. Spalte besitzt keine Masse für Zielwert."
                )

            col_factors = np.where(
                col_sums > 0, target_cols / np.maximum(col_sums, 1e-15), 1.0
            )
            T *= col_factors[np.newaxis, :]

            # 3. Konvergenzprüfung
            row_error = np.max(np.abs(T.sum(axis=1) - target_rows))
            col_error = np.max(np.abs(T.sum(axis=0) - target_cols))
            error = max(row_error, col_error)

            if error < self.tol:
                if self.verbose:
                    print(f"    Konvergiert nach {iteration} Iterationen (Fehler={error:.3e})")
                return T, iteration, True

        if self.verbose:
            print(f"    WARNUNG: Max. Iterationen ({self.max_iter}) erreicht.")
        return T, self.max_iter, False

    # ==================================================================
    # DATAFRAME ERSTELLUNG (VEKTORISIERT)
    # ==================================================================

    def _matrix_to_dataframe(
        self, T_ras, all_nodes, countries, commodity, target_rows, target_cols, original_values
    ):
        grid_r, grid_p = np.meshgrid(all_nodes, all_nodes, indexing="ij")
        rep_flat = grid_r.ravel()
        part_flat = grid_p.ravel()
        vals_flat = T_ras.ravel()

        df_res = pd.DataFrame(
            {
                self.reporter_col: rep_flat,
                self.partner_col: part_flat,
                self.commodity_col: commodity,
                self.period_col: 0,
                self.bilateral_col: vals_flat,
            }
        )

        node_map_r = dict(zip(all_nodes, target_rows))
        node_map_c = dict(zip(all_nodes, target_cols))
        df_res[self.row_target_col] = df_res[self.reporter_col].map(node_map_r)
        df_res[self.col_target_col] = df_res[self.partner_col].map(node_map_c)

        orig_map = pd.Series(original_values)
        if not orig_map.empty:
            orig_map.index = pd.MultiIndex.from_tuples(
                orig_map.index, names=[self.reporter_col, self.partner_col]
            )
            df_res = df_res.merge(
                orig_map.rename("Export_bilateral_original"),
                on=[self.reporter_col, self.partner_col],
                how="left",
            )
        else:
            df_res["Export_bilateral_original"] = np.nan

        is_same = (df_res[self.reporter_col] == df_res[self.partner_col]) & (
            df_res[self.reporter_col] != self.row_col
        )
        df_res.loc[is_same, [self.bilateral_col, "Export_bilateral_original"]] = np.nan

        is_orig_nan = (
            df_res["Export_bilateral_original"].isna()
            & (~df_res[self.reporter_col].isin([self.row_col]))
            & (~df_res[self.partner_col].isin([self.row_col]))
        )
        df_res.loc[is_orig_nan & ~is_same, self.bilateral_col] = np.nan

        df_res["RAS_adjusted"] = df_res["Export_bilateral_original"].notna()

        cols_order = [
            self.reporter_col,
            self.partner_col,
            self.commodity_col,
            self.period_col,
            self.row_target_col,
            self.col_target_col,
            self.bilateral_col,
            "Export_bilateral_original",
            "RAS_adjusted",
        ]
        return df_res[cols_order]

    