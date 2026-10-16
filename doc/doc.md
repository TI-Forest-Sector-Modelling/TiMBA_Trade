# TiMBA Trade Module: Methodology

This document describes the two methodological building blocks of the module:

1. the **price-induced growth factor** for bilateral trade (derived from an Armington/CES relation), and
2. the **RAS balancing** that forces bilateral trade to match the export and import totals from TiMBA.

**How they fit together:** the BACI bilateral exports are scaled with the growth factor (`P_share_growth`) and then balanced with RAS to the TiMBA export and import targets (`X_q_o`, `M_q_p`). The result of one period is the bilateral base of the next period.

---

# Part 1: Price-induced growth factor

## 1.1 Armington relation

The estimated relation between imports and domestic supply is

$$
\ln\left(\frac{Q_M}{Q_D}\right)
=
\sigma\ln\left(\frac{\beta}{1-\beta}\right)
+
\sigma\ln\left(\frac{P_D}{P_M}\right)
+
\varepsilon
$$

| Symbol | Meaning |
|---|---|
| $Q_M$ | imported quantity |
| $Q_D$ | domestically produced quantity |
| $P_M$ | import price |
| $P_D$ | price of the domestically produced good |
| $\sigma$ | elasticity of substitution |
| $\beta$ | preference parameter |

The central relation is

$$
\frac{\partial \ln(Q_M/Q_D)}{\partial \ln(P_D/P_M)} = \sigma
$$

A higher price of the domestic good relative to the import good increases, ceteris paribus, the demand for imports.

## 1.2 Change over time (exact CES result)

Taking differences between $t$ and $t-1$ and assuming the preference term and error term do not change ($\Delta\varepsilon_t = 0$):

$$
\Delta\ln\left(\frac{Q_M}{Q_D}\right)_t
=
\sigma\,\Delta\ln\left(\frac{P_D}{P_M}\right)_t
$$

Exponentiating gives the exact growth of the import/domestic ratio:

$$
\boxed{
\frac{(Q_M/Q_D)_t}{(Q_M/Q_D)_{t-1}}
=
\left[
\frac{P_{D,t}/P_{M,t}}{P_{D,t-1}/P_{M,t-1}}
\right]^\sigma
=
\exp\left[\sigma\,\Delta\ln\left(\frac{P_D}{P_M}\right)_t\right]
}
$$

## 1.3 Mapping to TiMBA prices

In TiMBA, import and export prices are fixed at world market prices, so $P^o_m \equiv P^p_m$ (o = exporter, p = importer). A bilateral trade price therefore does not exist. What does exist is the ratio of the production price $P_p$ to the world market price $P_m$ in each country:

$$
P_D = \frac{P_p^o}{P_m^o}, \qquad P_M = \frac{P_p^p}{P_m^p}
$$

Because $P^o_m \equiv P^p_m$, the world market price cancels out:

$$
\Delta\ln\left(\frac{P_D}{P_M}\right)_t = \Delta\ln\left(\frac{P^o_p}{P^p_p}\right)_t
$$

## 1.4 Growth factor used in the module

The module uses the price-induced adjustment factor

$$
\boxed{
P^{\mathrm{dev}}_t
=
\left[
1+
\ln\left(\frac{P^o_t}{P^p_t}\right)
-
\ln\left(\frac{P^o_{t-1}}{P^p_{t-1}}\right)
\right]^{\sigma}
}
$$

**Note: this is an approximation.** For small changes $\exp(x) \approx 1 + x$, so

$$
\left[1 + \Delta\ln\left(\frac{P_D}{P_M}\right)\right]^\sigma
\;\approx\;
\exp\left[\sigma\,\Delta\ln\left(\frac{P_D}{P_M}\right)\right]
$$

The exact CES derivation would use the exponential form. The approximation is only valid for small relative price changes, and the base of the power must stay positive ($1 + \Delta\ln(\cdot) > 0$).

## 1.5 Symmetry between exporter and importer

A trade flow from exporter to importer is the same flow seen from both sides, so both perspectives must treat price changes consistently.

Plain relative changes of the price ratio are **not** symmetric: a ratio moving from 1 to 2 is +100 %, the reverse move from 2 to 1 is −50 %. Log differences are symmetric (+ln 2 and −ln 2), which is why the factor is built from $\Delta\ln$.

The import and export perspectives use opposite relative prices:

$$
P^{\mathrm{dev},M}_t = \left[1 + \Delta\ln\left(\frac{P_D}{P_M}\right)_t\right]^\sigma,
\qquad
P^{\mathrm{dev},X}_t = \left[1 + \Delta\ln\left(\frac{P_M}{P_D}\right)_t\right]^\sigma
$$

Since $\Delta\ln(P_M/P_D) = -\Delta\ln(P_D/P_M)$, the two factors react in opposite directions to a change in relative prices. With the exact exponential form they would be exact reciprocals; with the approximation they are reciprocal only approximately, because $(1+\Delta)(1-\Delta) = 1-\Delta^2 \approx 1$ for small $\Delta$.

The growth of imports and exports combines a general growth term with the price factor:

$$
M^{\mathrm{growth}}_t = LD^{\mathrm{growth}}_t \cdot P^{\mathrm{dev},M}_t,
\qquad
X^{\mathrm{growth}}_t = LD^{\mathrm{growth}}_t \cdot P^{\mathrm{dev},X}_t
$$

---

# Part 2: RAS balancing (per commodity)

## 2.1 Notation

- Countries $i, j \in \{1, \dots, n\}$, Rest of World $R$ as node $n+1$, $N = n+1$.
- $x_i$: export total (`X_q_o`), $m_j$: import total (`M_q_p`).
- $t_{ij}$: observed bilateral export (BACI base, scaled with the growth factor).
- $\tau$: `tol`, $c$: `cutoff`.

## 2.2 Preparing the targets

1. **Remove small and negative values:** $x_i \leftarrow x_i \cdot \mathbb{1}[x_i \ge c]$, analogously for $m_j$.
2. **Move targets without observed trade to RoW:** if country $i$ has no bilateral export $t_{ij} > 0$, then $x_R \leftarrow x_R + x_i$ and $x_i \leftarrow 0$. Analogously for $m_j$ (no $t_{ij} > 0$ as importer).
3. **Balance totals via RoW** so that $\sum_i x_i = \sum_j m_j$:

$$
\Delta = \sum_i x_i - \sum_j m_j,
\qquad
\Delta > \tau:\; m_R \mathrel{+}= \Delta,
\qquad
\Delta < -\tau:\; x_R \mathrel{+}= -\Delta
$$

## 2.3 Start matrix $T^{(0)}$

$$
T^{(0)}_{ij}=
\begin{cases}
t_{ij} & i\neq j,\; x_i>\tau,\; m_j>\tau,\; t_{ij}\ge 0 \text{ observed}\\[2pt]
1 & j=R,\; x_i>\tau \quad\text{or}\quad i=R,\; m_j>\tau \quad\text{(RoW support cells)}\\[2pt]
0 & \text{otherwise (including } T_{RR}=0,\; T_{ii}=0)
\end{cases}
$$

Zero cells stay zero throughout RAS. Only cells with a positive value are adjusted.

**Fallbacks**

- If RoW has a target ($x_R > \tau$) but no adjustable cell, its row is filled with 1 for all countries that have a positive import target (analogously its column for $m_R$).
- If a row $i$ has a target $x_i > \tau$ but an empty start row, it is filled proportionally to the column targets, without own trade:

$$
T^{(0)}_{ij} = x_i \, \frac{m_j}{\sum_{k\neq i} m_k} \quad (j \neq i)
$$

## 2.4 Iteration (Sinkhorn / Bregman projection)

Repeat for $k = 1, 2, \dots$:

$$
r_i^{(k)} = \frac{x_i}{\sum_j T^{(k-1)}_{ij}},
\qquad
T'_{ij} = r_i^{(k)}\, T^{(k-1)}_{ij}
\qquad\text{(row step)}
$$

$$
s_j^{(k)} = \frac{m_j}{\sum_i T'_{ij}},
\qquad
T^{(k)}_{ij} = T'_{ij}\, s_j^{(k)}
\qquad\text{(column step)}
$$

- The factor is set to 1 if the sum is 0.
- The run aborts with an error if a sum is $\le \tau$ while its target is $> \tau$ (the node cannot reach its target).
- **Convergence:** $\max_i \left| \sum_j T^{(k)}_{ij} - x_i \right| < \tau$, checked after the column step. Otherwise the run stops after `max_iter` iterations and logs a warning.

## 2.5 Solution

$$
T^* = \operatorname{diag}(r)\; T^{(0)}\; \operatorname{diag}(s),
\qquad
r_i = \prod_k r_i^{(k)},\;\; s_j = \prod_k s_j^{(k)}
$$

$T^*$ is the matrix with row sums $x$ and column sums $m$ that is closest to $T^{(0)}$ in terms of the Kullback-Leibler divergence:

$$
T^* = \arg\min_{T \ge 0} \sum_{ij} T_{ij} \ln\frac{T_{ij}}{T^{(0)}_{ij}}
\quad\text{s.t.}\quad
\sum_j T_{ij} = x_i,\;\; \sum_i T_{ij} = m_j
$$

A solution exists and RAS converges if $\sum x = \sum m$ (ensured by step 2.2.3) and if the zero structure of $T^{(0)}$ allows the targets (ensured by support cells and fallbacks).

Background: RAS is the same algorithm as iterative proportional fitting (Deming & Stephan 1940) and the Sinkhorn algorithm (Sinkhorn 1967). For bilateral trade it is equivalent to a Poisson pseudo-maximum-likelihood gravity model with exporter and importer fixed effects, where $r_i$ and $s_j$ play the role of the multilateral resistance terms (Fally 2015).

## 2.6 Output

| Column | Content |
|---|---|
| `Export_bilateral` | balanced value $T^*_{ij}$ |
| `Export_bilateral_original` | observed value $t_{ij}$ |
| `RAS_adjusted` | `True` if $t_{ij}$ was observed |

- For country pairs ($i, j \neq R$) without an observed value (including the diagonal) the result is `NaN`. Cells involving RoW are always kept.
- Diagnostics per commodity: number of iterations, convergence flag, $\max_i |\sum_j T^*_{ij} - x_i|$ and $\max_j |\sum_i T^*_{ij} - m_j|$.

---

# Part 3: Known limitations and ideas

| Topic | Issue | Idea |
|---|---|---|
| RoW start values | RoW support cells use the constant `1.0`. This ignores information in BACI and depends on units. | Fill RoW cells with BACI trade of non-FAO countries $U$: $T^{(0)}_{iR} = \sum_{k\in U} t_{ik}$ and $T^{(0)}_{Rj} = \sum_{k\in U} t_{kj}$. |
| Scale of thresholds | `cutoff` and `tol` are absolute values. | Define them relative to the scale of the data. |
| Missing vs. zero targets | Missing FAO values (`NaN`) and reported zeros are both treated as 0. | Treat "not reported" (move to RoW) and "reported zero" separately. |
| What RoW contains | RoW mixes real trade with non-covered countries and inconsistencies between FAO export and import totals ($\Delta$). | Report $\Delta$ separately; consider weighted or soft targets (e.g. KRAS, unbalanced optimal transport). |
| Feasibility | Only checks that rows and columns have some mass, not the exact existence condition. Near-infeasible cases converge slowly and may stop at `max_iter` without matching the targets. | Add a feasibility check and log the cells with the largest factors $r_i s_j$. |
| Validation | Matching the totals holds by construction and is not a quality measure. | Hold-out test: hide observed cells, reconstruct them and measure the error. |
| Consistency | Commodities and periods are balanced independently of each other. | Multi-dimensional RAS with constraints on aggregates, if needed. |
| Check against BACI | RoW results can be compared with BACI. | Compare $\sum_i T^*_{iR}$ with $\sum_{i\in C}\sum_{k\in U} t_{ik}$. Large gaps or scaling factors far from 1 point to FAO/BACI mismatches in concept, units or coverage. |

## References

- Deming, W. E., & Stephan, F. F. (1940). On a least squares adjustment of a sampled frequency table when the expected marginal totals are known. *Annals of Mathematical Statistics*.
- Sinkhorn, R. (1967). Diagonal equivalence to matrices with prescribed row and column sums. *American Mathematical Monthly*.
- Fally, T. (2015). Structural gravity and fixed effects. *Journal of International Economics*.
