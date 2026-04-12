---
description: Run a full research pipeline — literature review → experiment design → implementation → results → paper section. Zero questions.
---

Execute this full research pipeline with ZERO questions: $ARGUMENTS

## Pipeline Stages

### Stage 1: Literature Context
- Search for 10+ relevant papers on this topic
- Identify gaps, baselines, and standard metrics
- Write findings to docs/literature/

### Stage 2: Experiment Design
- Define hypothesis, variables, baselines, metrics
- Create config.yaml with all hyperparameters
- Write experiment plan to docs/experiments/

### Stage 3: Implementation
- Implement any new models/algorithms needed
- Create run.py with full experiment pipeline
- Create reproduce.sh for reproducibility
- Write unit tests for new code

### Stage 4: Execute
- Run experiments across all seeds
- Save results to results/

### Stage 5: Analysis
- Compute statistics, generate figures, build LaTeX tables
- Write analysis report to docs/experiments/

### Stage 6: Paper Section
- Draft the relevant paper section(s) with results integrated
- Include citations from the literature review
- Save to docs/papers/

## Rules
- Follow CLAUDE.md for all defaults
- Document every decision in DECISIONS.md
- If blocked at any stage, write what you have and continue to the next stage
- Generate publication-quality figures (PDF, 300 DPI, colorblind-safe)
