---
description: Run a full pre-submission review — simulated peer review + methodology audit + completeness check. Zero questions.
---

Run a comprehensive pre-submission review on the paper draft with ZERO questions: $ARGUMENTS

## Review Pipeline

### Step 1: Simulated Peer Review
Use the peer-reviewer agent to generate 3 independent reviews of the paper, each from a different perspective:
- Reviewer 1: Focus on novelty and related work coverage
- Reviewer 2: Focus on experimental methodology and statistical rigor
- Reviewer 3: Focus on clarity, presentation, and reproducibility

### Step 2: Methodology Audit
Use the methodology-advisor agent to check:
- Internal, external, statistical, and construct validity
- Threats to validity not yet addressed
- Missing ablations or baselines

### Step 3: Completeness Check
Verify:
- [ ] Abstract has concrete results with numbers
- [ ] All contributions are supported by experiments
- [ ] All figures/tables are referenced in text
- [ ] All notation is defined before first use
- [ ] Related work covers all major approaches
- [ ] Limitations section is present and honest
- [ ] Reproducibility details are sufficient (code, data, compute)
- [ ] Citation style matches venue requirements
- [ ] Page count within limits

### Step 4: Synthesis
Write a consolidated report to `docs/papers/pre-submission-review.md`:
- Top 3 critical issues to fix
- Top 5 improvements that would strengthen the paper
- Estimated accept probability (with reasoning)
- Specific revision plan ordered by impact

Default: Review everything in docs/papers/ if no specific draft is mentioned.
