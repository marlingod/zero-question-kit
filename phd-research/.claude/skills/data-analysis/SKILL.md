---
name: data-analysis
description: Analyze experimental results, generate figures, and produce statistical reports. Triggers on analyze results, plot, visualize, statistics, significance test, compare results, ablation.
context: fork
agent: general-purpose
allowed-tools: Bash(python *), Read, Write, Grep, Glob
---

## Autonomous Data Analysis Protocol

NEVER ask what to analyze or how to plot. Analyze EVERYTHING in the results directory.

### Phase 1: Discovery
1. Scan `results/` for all experiment outputs
2. Identify data formats (JSON, CSV, pickle, npy)
3. Load all results and summarize dimensions

### Phase 2: Statistical Analysis
For each experiment:
1. Compute descriptive stats: mean, std, median, min, max per metric per method
2. Normality test (Shapiro-Wilk) to determine parametric vs non-parametric
3. If normal → paired t-test or ANOVA
4. If non-normal → Wilcoxon signed-rank or Kruskal-Wallis
5. Compute effect size (Cohen's d or rank-biserial correlation)
6. Report: test statistic, p-value, effect size, confidence interval

### Phase 3: Visualization
Generate publication-quality figures:

```python
# Standard figure setup
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams.update({
    'font.size': 12,
    'font.family': 'serif',
    'axes.labelsize': 14,
    'axes.titlesize': 14,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 11,
    'figure.figsize': (6, 4),
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'axes.grid': True,
    'grid.alpha': 0.3,
})

# Colorblind-friendly palette (Okabe-Ito)
COLORS = ['#E69F00', '#56B4E9', '#009E73', '#F0E442', 
          '#0072B2', '#D55E00', '#CC79A7', '#000000']
```

Required figures:
1. **Comparison bar chart**: All methods, all metrics, with error bars
2. **Training curves**: Loss/metric over epochs (if applicable)
3. **Ablation plots**: One variable at a time
4. **Statistical significance matrix**: Pairwise p-values heatmap

Save to: `docs/figures/EXP_NAME_PLOT_TYPE.pdf` AND `.svg`

### Phase 4: LaTeX Tables
Generate ready-to-paste LaTeX tables:

```latex
\begin{table}[t]
\centering
\caption{Results on [dataset]. Best results in \textbf{bold}. 
Mean $\pm$ std over [N] seeds. 
$\dagger$ indicates $p < 0.05$ vs.\ best baseline.}
\label{tab:results}
\begin{tabular}{lccc}
\toprule
Method & Metric 1 ($\uparrow$) & Metric 2 ($\downarrow$) \\
\midrule
Baseline 1 & $X.XX \pm Y.YY$ & $X.XX \pm Y.YY$ \\
Baseline 2 & $X.XX \pm Y.YY$ & $X.XX \pm Y.YY$ \\
\midrule
\textbf{Ours} & $\mathbf{X.XX \pm Y.YY}^\dagger$ & $\mathbf{X.XX \pm Y.YY}$ \\
\bottomrule
\end{tabular}
\end{table}
```

### Phase 5: Report
Write to `docs/experiments/EXP_NAME-analysis.md`:
- Summary statistics table
- Statistical test results
- List of generated figures with descriptions
- LaTeX table code (copy-paste ready)
- Key insights and anomalies detected

### Decision Rules
- Always use non-parametric tests if N < 30 seeds
- Always include error bars (std or 95% CI)
- Bold the best result, underline second-best
- Use ↑ for higher-is-better, ↓ for lower-is-better in table headers
- If results are inconclusive, say so — don't cherry-pick
