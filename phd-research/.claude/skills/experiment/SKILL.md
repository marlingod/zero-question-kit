---
name: experiment
description: Design, implement, and run reproducible experiments. Triggers on experiment, run experiment, test hypothesis, benchmark, ablation, evaluate, train model, compare approaches.
---

## Autonomous Experiment Protocol

NEVER ask what to test or how to configure. Infer from the codebase and CLAUDE.md.

### Phase 1: Design
1. Read CLAUDE.md for research domain and methodology defaults
2. Scan `src/` for existing model implementations
3. Scan `experiments/` for existing experiment patterns
4. Define:
   - **Hypothesis**: What are we testing?
   - **Independent variables**: What are we varying?
   - **Dependent variables**: What are we measuring?
   - **Controls**: What stays fixed?
   - **Baselines**: Current SOTA + at least one classical method

Write plan to `docs/experiments/EXP_NAME-plan.md`

### Phase 2: Implement
Create experiment structure:
```
experiments/EXP_NAME/
├── config.yaml          # All hyperparameters, paths, seeds
├── run.py               # Single entry point
├── analyze.py           # Post-hoc analysis and figure generation
└── reproduce.sh         # Full reproduction from scratch
```

#### config.yaml template:
```yaml
experiment:
  name: EXP_NAME
  description: "One-line description"
  date: YYYY-MM-DD

model:
  architecture: ...
  hyperparameters:
    learning_rate: ...
    ...

training:
  epochs: ...
  batch_size: ...
  optimizer: ...
  scheduler: ...

evaluation:
  metrics: [accuracy, loss, ...]
  seeds: [42, 123, 456, 789, 1024]

data:
  dataset: ...
  split: [train, val, test]
  preprocessing: ...

hardware:
  device: auto  # auto-detect GPU/CPU
  
logging:
  save_dir: results/EXP_NAME/
  wandb_project: ...  # optional
```

#### run.py requirements:
- Parse config.yaml with argparse override support
- Loop over all seeds automatically
- Save results per seed to `results/EXP_NAME/seed_N/`
- Save aggregate results to `results/EXP_NAME/aggregate.json`
- Log everything: hyperparams, hardware, wall-clock time, memory usage

#### reproduce.sh template:
```bash
#!/bin/bash
set -e
# pip install -r requirements.txt
python experiments/EXP_NAME/run.py --config experiments/EXP_NAME/config.yaml
python experiments/EXP_NAME/analyze.py --results results/EXP_NAME/
echo "Done. Results in results/EXP_NAME/"
```

### Phase 3: Run
1. Execute `run.py` with all seeds
2. Monitor for failures — retry with adjusted config if needed (3 attempts)
3. Save raw results

### Phase 4: Analyze
1. Compute mean ± std across seeds for all metrics
2. Run statistical significance tests (paired t-test or Wilcoxon)
3. Generate publication-quality figures (PDF/SVG, 300 DPI)
4. Generate results tables (LaTeX-formatted)
5. Write analysis to `docs/experiments/EXP_NAME-results.md`

### Output: Results Summary
```markdown
# Experiment Results: [EXP_NAME]

## Setup
- Hypothesis: ...
- Hardware: ...
- Total compute time: ...

## Results Table
| Method | Metric 1 (↑) | Metric 2 (↓) | Metric 3 |
|--------|--------------|--------------|----------|
| Ours   | **X.XX ± Y.YY** | ... | ... |
| SOTA   | X.XX ± Y.YY | ... | ... |
| Baseline | X.XX ± Y.YY | ... | ... |

## Statistical Significance
- Ours vs SOTA: p=X.XXX (test used)

## Key Findings
1. ...
2. ...

## Figures Generated
- figures/EXP_NAME_comparison.pdf
- figures/EXP_NAME_ablation.pdf
```

### Decision Rules
- If no baselines specified, use current SOTA + simplest classical approach
- If no metrics specified, use standard metrics for the field (check recent papers)
- If compute is limited, run 3 seeds and document the limitation
- Always generate LaTeX-formatted tables (ready for paper insertion)
- Figures: Matplotlib, font size 12+, vector format, colorblind-friendly palette
