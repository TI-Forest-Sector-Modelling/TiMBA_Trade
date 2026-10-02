# RAS – Mathematische Formulierung (pro Commodity)

**Notation:** Länder $i,j \in \{1,\dots,n\}$, Rest der Welt $R$ als Knoten $n{+}1$, $N=n+1$.
$x_i$ = Export-Randsumme (`X_q_o`), $m_j$ = Import-Randsumme (`M_q_p`), $t_{ij}$ = beobachteter bilateraler Export, $\tau$ = `tol`, $c$ = `cutoff`.

## 1. Randsummen aufbereiten

1. Negatives und Kleinstwerte entfernen: $x_i \leftarrow x_i\,\mathbb{1}[x_i \ge c]$, analog $m_j$.
2. Ziel ohne Beobachtungsmasse nach RoW verschieben: Hat Land $i$ keinen bilateralen Export $t_{ij}>0$, gilt
   $x_R \leftarrow x_R + x_i,\; x_i \leftarrow 0$. Analog für $m_j$ (kein $t_{ij}>0$ als Importeur).
3. Bilanz über RoW ausgleichen, damit $\sum_i x_i = \sum_j m_j$:
$$\Delta = \sum_{i} x_i - \sum_{j} m_j,\qquad \Delta>\tau:\; m_R \mathrel{+}= \Delta,\quad \Delta<-\tau:\; x_R \mathrel{+}= -\Delta$$

## 2. Startmatrix $T^{(0)}$

$$T^{(0)}_{ij}=\begin{cases}
t_{ij} & i\neq j,\ x_i>\tau,\ m_j>\tau,\ t_{ij}\ge 0 \text{ beobachtet}\\
1 & j=R,\ x_i>\tau \quad\text{oder}\quad i=R,\ m_j>\tau \quad\text{(Support-Zellen)}\\
0 & \text{sonst (inkl. } T_{RR}=0,\ T_{ii}=0)
\end{cases}$$

Nullzellen bleiben im RAS immer Null; nur die Zellen mit Wert $>0$ sind anpassbar.

**Fallbacks**
- Hat $R$ ein Ziel $x_R>\tau$, aber keine anpassbare Zelle, wird die Zeile $T_{Rj}=1$ gesetzt (analog Spalte $T_{iR}=1$ für $m_R$).
- Zeile $i$ mit $x_i>\tau$, aber $\sum_j T_{ij}\approx 0$, wird proportional zu den Spaltenzielen gefüllt (ohne Eigenhandel):
$$T^{(0)}_{ij} = x_i\,\frac{m_j}{\sum_{k\neq i} m_k}\quad (j\neq i)$$

## 3. RAS-Iteration (Sinkhorn/Bregman-Projektion)

Wiederhole für $k=1,2,\dots$:

$$r_i^{(k)}=\frac{x_i}{\sum_j T^{(k-1)}_{ij}},\qquad T'_{ij}=r_i^{(k)}\,T^{(k-1)}_{ij}\quad\text{(Zeilenschritt)}$$

$$s_j^{(k)}=\frac{m_j}{\sum_i T'_{ij}},\qquad T^{(k)}_{ij}=T'_{ij}\,s_j^{(k)}\quad\text{(Spaltenschritt)}$$

(Faktor $=1$, falls die Summe $=0$; Abbruch mit Fehler, falls Summe $\le\tau$ bei Ziel $>\tau$.)

**Abbruch:** $\max_i \left|\sum_j T^{(k)}_{ij}-x_i\right| < \tau$ (nach dem Spaltenschritt gilt die Spaltenbedingung ohnehin exakt bis auf Rundung), sonst nach `max_iter`.

## 4. Lösung

$$T^* = \operatorname{diag}(r)\,T^{(0)}\,\operatorname{diag}(s),\qquad r_i=\prod_k r_i^{(k)},\; s_j=\prod_k s_j^{(k)}$$

$T^*$ ist die Matrix mit den Randsummen $x$ und $m$, die $T^{(0)}$ in der **KL-Divergenz** am nächsten liegt:
$$T^*=\arg\min_{T\ge0}\ \sum_{ij} T_{ij}\ln\frac{T_{ij}}{T^{(0)}_{ij}} \quad\text{s.t.}\quad \textstyle\sum_j T_{ij}=x_i,\ \sum_i T_{ij}=m_j$$

Existenz/Konvergenz setzt voraus: $\sum x=\sum m$ (durch Schritt 1.3 erfüllt) und dass die Nullstruktur von $T^{(0)}$ die Randsummen zulässt (durch Support-Zellen und Fallbacks abgesichert).

## 5. Ausgabe

- $T^*_{ij}$ wird als `Export_bilateral` ausgegeben, $t_{ij}$ als `Export_bilateral_original`.
- Für Länderpaare ($i,j\neq R$) ohne beobachteten Wert (inkl. Diagonale) wird `NaN` gesetzt; Zellen mit RoW bleiben erhalten.
- `RAS_adjusted` $=\mathbb{1}[t_{ij}\text{ beobachtet}]$.
- Diagnose: $\max_i|\sum_j T^*_{ij}-x_i|$ und $\max_j|\sum_i T^*_{ij}-m_j|$.

---

# Einordnung in die Literatur

> Hinweis: Auswahl, keine systematische Übersicht. Die Verifikation (Web-Recherche) betraf v. a. Lenzen et al. 2009, Junius & Oosterhaven 2003, Fally 2015/2018, Lahr & de Mesnard 2004, Gehlhar (GTAP) und die RAS-vs.-Gravity-Studie (ESR 2020). Die übrigen Klassiker sind aus dem Gedächtnis zitiert – bitte vor Verwendung in einer Arbeit prüfen.

## 1. Methodische Wurzeln

| Strang | Kernidee | Referenzen |
|---|---|---|
| **IPF / RAS** | Iterative Zeilen-/Spaltenskalierung; in der Statistik *Iterative Proportional Fitting*, in der Input-Output-Analyse *RAS* | Deming & Stephan (1940); Stone (1962); Bacharach (1970); Überblick: Lahr & de Mesnard (2004) |
| **Konvergenz / Optimalität** | Sinkhorn-Skalierung; Lösung ist die KL-Projektion (I-Projektion) auf die Randsummenbedingungen | Sinkhorn (1967); Csiszár (1975); McDougall (1999, „Entropy theory and RAS are friends“) |
| **Optimal Transport** | RAS = Sinkhorn-Algorithmus für entropisch regularisierten OT mit Kosten $c_{ij}=-\varepsilon\ln T^{(0)}_{ij}$ | Cuturi (2013); Peyré & Cuturi (2019) |
| **Gravitation** | PPML mit Exporteur-/Importeur-Fixed-Effects reproduziert die Randsummen; die Multilateral-Resistance-Terme sind mathematisch die Skalierungsfaktoren $r_i, s_j$ | Fally (2015, JIE); Fally (2018, Iterative solutions… Panels) |

## 2. Varianten in der Matrix-Balancing-Literatur

- **GRAS** (Junius & Oosterhaven 2003; Note: Temurshoev, Miller & Bouwmeester 2013): negative Einträge zulässig.
- **KRAS** (Lenzen, Gallego & Wood 2009): Zuverlässigkeitsgewichte für Seed und Randsummen, **konfliktbehaftete Nebenbedingungen** werden als Kompromiss gelöst – genau das, was der vorliegende Code über die RoW-Konstruktion nur grob abbildet.
- **MR-GRAS / Multidimensional RAS** (Holý & Šafr 2017; Valderas-Jaramillo & Rueda-Cantuche): partitionierte, multiregionale Matrizen.
- **Cross-Entropy-Ansätze** (Golan et al. 1994; Robinson, Cattaneo & El-Said 2001): Randsummen als weiche Restriktionen mit Fehlertermen.

## 3. Anwendung auf bilaterale Handelsdaten

- **Spiegelstatistik-Abgleich:** Export- und Importmeldungen desselben Flusses weichen ab (Meldefehler, cif/fob). GTAP (Gehlhar) wählt die zuverlässigsten Meldungen nach Reporter-Credibility, BACI (Gaulier & Zignago 2010) gewichtet Spiegelwerte mit Reporter-Reliabilität. **Reines Matrix-Balancing mit unabgeglichenen Randsummen wird dort ausdrücklich als ungeeignet bezeichnet** (Gehlhar).
- **Netzwerkrekonstruktion:** Eine Studie in *Economic Systems Research* (2020, doi:10.1080/09535314.2019.1703173) vergleicht RAS und Gravitationsmodell für Nahrungsmittelhandel: RAS liefert bessere Flussschätzungen und garantiert die Bilanz (Weltimporte = Weltexporte), das Gravity-Modell hat geringere relative Fehler, unterschätzt aber die Gesamtströme.
- **MRIO-Datenbanken** (Eora, WIOD, OECD-ICIO): RAS-Varianten (v. a. KRAS bei Eora) sind Standard zum Ausgleich heterogener Quellen.

**Eigener Beitrag des Codes:** Der Kern ist Standard-RAS. Neu bzw. pragmatisch ist die Konstruktion um den Kern: Cutoff, Verschiebung nicht abbildbarer Ziele nach RoW, RoW als Schlupfknoten mit Support-Zellen, Fallbacks. Das ist eine **Heuristik-Pipeline, kein neuer Algorithmus**; mir ist keine direkte Entsprechung des RoW-Schlupfknotens mit Einheitswerten in der Literatur bekannt.

---

# Kritische Bewertung

## Vorteile

- **Theoretisch fundiert:** eindeutige KL-Minimum-Lösung bei Zulässigkeit; identisch mit dem Poisson-Maximum-Likelihood-Schätzer mit Länder-Fixed-Effects (Fally 2015).
- **Struktur bleibt erhalten:** Nullen und Verhältnisse der Seed-Werte innerhalb von Zeilen bleiben erhalten, keine negativen Werte.
- **Bilanz garantiert:** $\sum x=\sum m$ über RoW, Randsummen exakt getroffen (im Gegensatz zu Gravity/OLS).
- **Einfach und schnell:** $O(N^2)$ pro Iteration, keine Schätzung von Parametern, gut parallelisierbar über Commodities.
- **Transparent:** Faktoren $r_i, s_j$ sind interpretierbar (Multilateral-Resistance-Analogon).

## Nachteile / Schwächen

1. **Seed-Abhängigkeit (im vorliegenden Kontext abgeschwächt):** Der Seed sind BACI-Daten, also bereits spiegelabgeglichen und mit Reporter-Reliabilitäten gewichtet. Das ist ein starker Prior, und die multiplikative Fortschreibung seiner Struktur ist hier sachlich begründet. Bleibende Restrisiken: strukturelle Nullen in BACI werden nie „repariert“, und BACI (HS6, meist USD) und FAO (Warenliste, ggf. Tonnen) müssen in Konzept, Einheit und Güterabgrenzung übereinstimmen (Konkordanz).
2. **RoW-Seed mit Einheitswert `1.0` verschenkt Information (wichtig):** RoW ist fachlich richtig (BACI-Länder ohne FAO-Ziel; deren Handel muss als Rest verbucht werden). Die Support-Zellen $T_{iR}, T_{Rj}$ erhalten aber die Konstante `1.0`, obwohl BACI die Information liefert: $T_{iR}=\sum_{k\in U} t_{ik}$ und $T_{Rj}=\sum_{k\in U} t_{kj}$ mit $U$ = BACI-Länder ohne FAO-Ziel. Die Konstante ist einheitenabhängig (USD vs. Mio. USD) und ignoriert, wie stark einzelne Länder mit $U$ handeln. Gleiches Skalenproblem: `cutoff=0.1` und `tol=1e-10`.
3. **RoW vermischt zwei Dinge:** (a) echter Handel mit Ländern außerhalb der FAO-Abdeckung und (b) Inkonsistenz der FAO-Randsummen untereinander ($\Delta=\sum x-\sum m$, da FAO-Meldungen ebenfalls Spiegeldaten sind). Zusätzlich werden fehlende FAO-Werte (`NaN`) und gemeldete Nullen beide zu 0 (`fillna(0)`). Fehlanpassung wird dadurch versteckt statt gemessen; es gibt keine Gewichte oder weiche Restriktionen (vgl. KRAS).
4. **Harte, diskontinuierliche Regeln:** Cutoff und „keine Masse → nach RoW“ sind Schwellenwerte; kleine Datenänderungen können große Sprünge in RoW-Flüssen erzeugen.
5. **Zulässigkeit wird nur schwach geprüft:** Der Code prüft, ob Zeilen/Spalten *irgendeine* Masse haben, nicht die notwendige und hinreichende Bedingung für Existenz (Total-Support, z. B. $x_i \le \sum_{j\in \text{Support}(i)} m_j$). Bei fast-unzulässigen Mustern konvergiert RAS nur sublinear und läuft bis `max_iter` (10 000) mit Warnung – die Lösung ist dann nicht randsummentreu.
6. **Exakte Randsummen trotz verrauschter Randsummen:** Überanpassung an fehlerbehaftete Ziele; keine Unsicherheitsmaße (Punktschätzung ohne Konfidenzintervall).
7. **Naiver Ersatz-Prior:** Die Nullzeilen-Auffüllung nutzt $x_i m_j/\sum m$ (Unabhängigkeit) ohne Distanz, BIP, Handelsabkommen – ökonomisch uninformativ und verwirft die RoW-Support-Zelle der Zeile.
8. **Keine Konsistenz über Dimensionen:** Commodities werden unabhängig behandelt (Summe über Güter ≠ aggregierte bilaterale Ströme), Perioden werden nicht verknüpft (`Period=0`), keine zeitliche Glättung.
9. **Negative Werte und Binnenhandel:** Negative Randsummen werden auf 0 gekappt (kein GRAS), Diagonale (Eigenhandel) ist ausgeschlossen, sodass Handelsanteile relativ zur Gesamtproduktion nicht abgeleitet werden können.
10. **Validierung fehlt:** Randsummentreue ist per Konstruktion erfüllt und kein Gütemaß. Aussagekräftig wäre ein Holdout (Zellen verstecken, rekonstruieren, Fehler messen).

## Empfehlungen zur Verbesserung

| Problem | Möglicher Ansatz |
|---|---|
| RoW-Seed `1.0` | RoW-Zellen aus aggregierten BACI-Flüssen zu Nicht-FAO-Ländern füllen (siehe Nachtrag); Cutoff und Toleranz relativ zur Skala definieren |
| Seed-Lücken (Nullen in BACI) | Nur falls nötig: Gravity-Vorhersage (PPML) als Ergänzung für fehlende Zellen |
| Fehlend vs. Null in FAO | `NaN` (nicht berichtet → RoW) und `0` (berichtet, kein Handel → Zeile/Spalte 0) getrennt behandeln |
| Konfliktive Randsummen, Rauschen | KRAS oder **unbalanced OT** (Chizat et al. 2018; weiche KL-Strafe auf die Randsummen) statt RoW-Schlupf |
| FAO-Randsummen inkonsistent | Weiche Randsummen mit Reliabilitätsgewichten (KRAS / unbalanced OT), Δ getrennt ausweisen |
| Zulässigkeit | Vorab Feasibility-Check, Diagnose der Zellen mit größten Faktoren $r_iS_j$ |
| Unsicherheit | Bootstrap über Randsummen/Seed oder Bayes-Ansatz; Sensitivität gegenüber Cutoff und RoW-Seed |
| Konsistenz über Güter/Zeit | Mehrdimensionales RAS (MR-GRAS) mit Zusatzrestriktionen auf Aggregate |

**Fazit:** Mit BACI als Seed und FAO als Randsummen ist RAS ein methodisch sauberer Ansatz: hochwertiger Prior, Anpassung an die FAO-Totale unter minimaler Informationsänderung. Die wichtigste Verbesserung ist die **RoW-Seed-Konstruktion aus BACI statt `1.0`**. Danach folgen die Unterscheidung von fehlenden und gemeldeten Null-Zielen, relative Schwellenwerte und eine Ausweisung der Δ-Bilanz.

---

# Nachtrag: Anwendungskontext BACI (Seed) × FAO (Targets)

**RoW-Seed aus BACI.** Sei $U$ die Menge der BACI-Länder ohne FAO-Ziel, $C$ die abgedeckten Länder. Statt $T^{(0)}_{iR}=T^{(0)}_{Rj}=1$:
$$T^{(0)}_{iR}=\sum_{k\in U} t_{ik}\quad(i\in C),\qquad T^{(0)}_{Rj}=\sum_{k\in U} t_{kj}\quad(j\in C)$$
Dann erbt RoW die BACI-Struktur, und das Ergebnis ist einheiteninvariant.

**Diagnose statt Vermutung.** Da RoW hier eine bekannte Größe hat, lässt sich der Schätzer prüfen:
$$\text{RoW-Export}^{\text{RAS}}=\sum_{i\in C} T^*_{iR}\ \text{vs.}\ \sum_{i\in C}\sum_{k\in U} t_{ik}\quad(\text{analog Import})$$
Große Abweichungen zeigen, dass FAO- und BACI-Totale für abgedeckte Länder nicht zueinander passen (Konzept-/Einheits-/Konkordanzfehler oder Meldelücken) und nicht nur ein RoW-Effekt vorliegt.

**Skalierungsfaktoren als Qualitätsmaß.** Faktoren $r_i, s_j$ weit von 1 bedeuten starke FAO-BACI-Diskrepanzen für Land $i$ bzw. $j$. Sie eignen sich als Filter oder Flag pro Land und Gut.
