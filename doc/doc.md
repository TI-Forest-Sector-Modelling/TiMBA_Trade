# TiMBA Trade Module und Armington

## Armington Elastizität aus Schätzung
$$
\ln\left(\frac{Q_M}{Q_D}\right)
=
\sigma\ln\left(\frac{\beta}{1-\beta}\right)
+
\sigma\ln\left(\frac{P_D}{P_M}\right)
+
\varepsilon
$$

mit

- \($Q_M$): importierte Menge
- \($Q_D$): inländisch produzierte Menge
- \($P_M$): Importpreis
- \($P_D$): Preis des domestisch produzierten Gutes
- \($\sigma$): Substitutionselastizität
- \($\beta$): Präferenzparameter

### Interpretation

Verhältnis zwischen importierter und inländisch produzierter Menge.

Der zentrale Zusammenhang ist:

$$
\frac{\partial
\ln(Q_M/Q_D)}
{\partial
\ln(P_D/P_M)}
=
\sigma
$$

Ein höherer relativer Preis des inländisch Gutes gegenüber dem Importgut führt ceteris paribus zu einer höheren Nachfrage nach Importen.


## Betrachtung über die Zeit

$$
\ln\left(\frac{Q_{M,t}}{Q_{D,t}}\right)
-
\ln\left(\frac{Q_{M,t-1}}{Q_{D,t-1}}\right)
=
\sigma
\left[
\ln\left(\frac{P_{D,t}}{P_{M,t}}\right)
-
\ln\left(\frac{P_{D,t-1}}{P_{M,t-1}}\right)
\right]
+
(\varepsilon_t-\varepsilon_{t-1})
$$


$$
\Delta\ln\left(\frac{Q_M}{Q_D}\right)_t
=
\sigma
\Delta\ln\left(\frac{P_D}{P_M}\right)_t
+
\Delta\varepsilon_t
$$


$$
\Delta\ln\left(\frac{Q_M}{Q_D}\right)_t
=
\sigma
\Delta\ln\left(\frac{P_D}{P_M}\right)_t
$$

$$
\ln\left(
\frac{(Q_M/Q_D)_t}
     {(Q_M/Q_D)_{t-1}}
\right)
=
\sigma
\ln\left(
\frac{P_{D,t}/P_{M,t}}
     {P_{D,t-1}/P_{M,t-1}}
\right)
$$

$$
\frac{(Q_M/Q_D)_t}
     {(Q_M/Q_D)_{t-1}}
=
\exp\left[
\sigma
\Delta\ln\left(\frac{P_D}{P_M}\right)_t
\right]
$$

$$
\boxed{
\frac{(Q_M/Q_D)_t}
     {(Q_M/Q_D)_{t-1}}
=
\left[
\frac{
P_{D,t}/P_{M,t}
}{
P_{D,t-1}/P_{M,t-1}
}
\right]^\sigma
}
$$


# Herleitung TiMBA Wachstum

In TiMBA sind Import und Exportpreise an den Weltmarktpreisen fixiert. Daher ist $P^o_m \equiv P^p_m$ wobei o für den Exporteur und p für den Importeur steht.

Den bilateralen Preis $P_m$ gibt es daher im den Sinne nicht. Was existiert ist allerdings das Preisverhältnis zwischen dem Produktionkosten $P_p^o$ zum Importpreis $P^o_m$ und $P_p^p$ zu $P^p_m$. 

Daher gilt für das Modul:

$$
P_D = \left(\frac{P_p^o}{P^o_m}\right)
$$

und 

$$
P_M = \left(\frac{P_p^p}{P^p_m}\right)
$$


Die Veränderung ist dann ggb. durch:


$$
\Delta\ln\left(\frac{P_D}{P_M}\right)_t
$$

bzw.:

$$
\Delta\ln\left(\frac{P^o}{P^p}\right)_t
$$

Weil $P^o_m \equiv P^p_m$.

Die CES-/Armington-Gleichung liefert (s.o):

$$
\boxed{
\Delta\ln\left(\frac{Q_M}{Q_D}\right)_t
=
\sigma
\Delta\ln\left(\frac{P_D}{P_M}\right)_t
}
$$

für das Trade Module wird daraus der Wachstumsfaktor konstruiert:

$$
P^{\mathrm{dev}}_t
=
\left[
1+
\Delta\ln\left(\frac{P_D}{P_M}\right)_t
\right]^{\sigma}
$$

Damit ist $(P^{\mathrm{dev}}_t)$ preisinduzierter Anpassungsfaktor

# TiMBA Trade Module price development

$$
\boxed{
P^{\mathrm{dev}}_t
=
\left[
1+
\ln\left(
\frac{P^o_t}{P^p_t}
\right)
-
\ln\left(
\frac{P^o_{t-1}}{P^p_{t-1}}
\right)
\right]^{\sigma}
}
$$

## Problem: momentan nur Lösung durch Annäherung

Für kleine Änderungen gilt näherungsweise:

$$
\exp(x)\approx 1+x
$$

Für kleine relative Preisänderungen gilt daher:

$$
\exp\left[
\Delta\ln\left(\frac{P_D}{P_M}\right)
\right]
\approx
1+
\Delta\ln\left(\frac{P_D}{P_M}\right)
$$

Damit ist:

$$
\left[
1+
\Delta\ln\left(\frac{P_D}{P_M}\right)
\right]^\sigma
$$

als eine alternative bzw. approximative Konstruktion eines preisinduzierten Anpassungsfaktors interpretierbar.

Die **exakte CES-Ableitung** wäre:

$$
\exp\left[
\sigma
\Delta\ln\left(\frac{P_D}{P_M}\right)
\right].
$$



# Symmetrie

Da ein Handelsstrom vom Exporteur zum Importer genau der gleich ist wie der zum Importer vom Exporteur. Müssen die Preisveränderungen für alle Ströme identische Ergebnisse erhalten. D.h. wenn der Export berechnet wird sollten die Berechnungen mit den identischen Berechnungen aus dem Import übereinstimmen. Die exakte CES Herleitung ergibt allerdings einen Kehrwert für den gleichen Strom also wenn das Preisverhältnis in t-1 = 1 dann ergibt und in t=0 für den Export gilt 2/1 und umgekehrt für den Import 1/2. Die Veränderung zu t-1 wäre dann einmal 1 und einmal -0.5. 

$$
M^{\mathrm{growth}}_t
=
LD^{\mathrm{growth}}_t
\cdot
P^{\mathrm{dev},M}_t
$$

und analog:

$$
X^{\mathrm{growth}}_t
=
LD^{\mathrm{growth}}_t
\cdot
P^{\mathrm{dev},X}_t
$$

Für Importe wäre der relevante relative Preis:

$$
\frac{P_D}{P_M}
$$

und damit:

$$
P^{\mathrm{dev},M}_t
=
\left[
1+
\Delta\ln\left(\frac{P_D}{P_M}\right)_t
\right]^\sigma
$$

Für Exporte kann die Perspektive umgekehrt werden:

$$
\frac{P_M}{P_D}
$$

und damit:

$$
P^{\mathrm{dev},X}_t
=
\left[
1+
\Delta\ln\left(\frac{P_M}{P_D}\right)_t
\right]^\sigma
$$

Die beiden Faktoren reagieren damit in entgegengesetzte Richtungen auf eine Veränderung der relativen Preise.

