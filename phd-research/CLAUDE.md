# Project: [RESEARCH PROJECT NAME]
# PI / Lead Researcher: [YOUR NAME]
# Institution: [YOUR UNIVERSITY]
# Program: [PhD in Computer Science / etc.]

## Decision Protocol — DO NOT ASK, JUST DO

When you encounter ambiguity in research tasks, follow these rules.
Never ask for clarification — make the decision and document it in DECISIONS.md.

---

### Research Domain Defaults
- Primary field: [e.g., Quantum Computing / Machine Learning / etc.]
- Subfield: [e.g., Quantum Continual Learning / etc.]
- Methodology: [Theoretical + Empirical / Pure Theoretical / Pure Empirical]
- Target venues: [e.g., NeurIPS, ICML, PRL, QIP — comma-separated]
- Citation style: [e.g., IEEE, APA, ACM]

### Tech Stack Defaults
- Language: Python 3.11+
- ML framework: [PyTorch / JAX / TensorFlow]
- Quantum framework: [PennyLane / Qiskit / Cirq]
- Experiment tracking: [Weights & Biases / MLflow / TensorBoard]
- Paper writing: LaTeX (using venue-specific template)
- Visualization: Matplotlib + Seaborn (publication-quality)
- Data: NumPy, Pandas, SciPy
- Environment: conda or venv (always use requirements.txt / environment.yml)

### Research Decision Rules

#### Literature Review
- When searching for related work, use: Google Scholar, Semantic Scholar, arXiv
- Minimum 20 papers for a full lit review, 5 for a quick context check
- Always include: seminal papers (>500 citations), most recent (last 12 months), and direct competitors
- If two papers conflict, document both positions — do NOT pick sides without evidence
- Always check if a paper has been retracted or corrected

#### Experiment Design
- Always define: hypothesis, independent variables, dependent variables, controls, baselines
- Default baselines: at minimum the current SOTA + one classical baseline
- Statistical significance: report p-values, confidence intervals, and effect sizes
- Random seeds: use 5 seeds minimum [42, 123, 456, 789, 1024] and report mean ± std
- If compute-constrained, run 3 seeds and note the limitation
- Always log hyperparameters, hardware specs, and wall-clock time

#### When Methodology Is Ambiguous
1. Follow the most recent published paper in the target venue as a template
2. Choose the simpler experimental setup
3. Document the choice in DECISIONS.md
4. Add: `# METHODOLOGICAL NOTE: Chose X over Y because [reason]`

#### Code for Experiments
- Every experiment must be reproducible from a single command
- Structure: `experiments/EXP_NAME/config.yaml` + `run.py`
- All results saved to `results/EXP_NAME/TIMESTAMP/`
- Never hardcode paths, seeds, or hyperparameters — use config files
- Include a `reproduce.sh` that sets up environment and runs everything

#### Paper Writing
- Always start from the target venue's LaTeX template
- Structure: Abstract → Intro → Related Work → Method → Experiments → Results → Discussion → Conclusion
- Every claim must have either a citation or experimental evidence
- Figures must be vector (PDF/SVG) for publication quality
- Tables must include standard deviations and bold the best result

#### What NOT to Do
- Never ask which papers to read — search and find them
- Never ask which baselines to compare against — include SOTA + classical
- Never ask about figure formatting — use publication-quality defaults
- Never ask about statistical tests — use appropriate test for the data distribution
- Never ask "should I also run..." — if it strengthens the paper, run it
- Never ask about LaTeX formatting — follow the venue template exactly

### File Organization
```
project/
├── CLAUDE.md                  # This file
├── DECISIONS.md               # Auto-generated decision log
├── docs/
│   ├── literature/            # Literature review notes
│   ├── experiments/           # Experiment plans and logs
│   ├── papers/                # Paper drafts (LaTeX)
│   └── figures/               # Publication-quality figures
├── src/                       # Source code
│   ├── models/                # Model implementations
│   ├── data/                  # Data loading and preprocessing
│   ├── training/              # Training loops
│   ├── evaluation/            # Evaluation metrics
│   └── utils/                 # Utilities
├── experiments/               # Experiment configs and runners
│   └── EXP_NAME/
│       ├── config.yaml
│       └── run.py
├── results/                   # Raw results (gitignored if large)
├── tests/                     # Unit tests
├── notebooks/                 # Exploration (not for final results)
└── requirements.txt           # Dependencies
```
