---
name: paper-writing
description: Draft, edit, or extend academic papers. Triggers on write paper, draft section, write abstract, write introduction, write related work, revise paper, camera-ready, rebuttal.
---

## Autonomous Paper Writing Protocol

NEVER ask what to write or which style. Infer from CLAUDE.md (target venue, citation style) and existing drafts.

### Phase 1: Context Gathering
1. Read CLAUDE.md for target venue and citation style
2. Scan `docs/papers/` for existing drafts
3. Scan `docs/literature/` for literature review notes
4. Scan `docs/experiments/` and `results/` for experimental results
5. If a venue template exists in `docs/papers/`, use it

### Phase 2: Structure
Standard structure (adapt to venue requirements):

```latex
\begin{abstract} ... \end{abstract}

\section{Introduction}
% Paragraph 1: Problem statement and motivation (why should anyone care?)
% Paragraph 2: Current approaches and their limitations (what's wrong now?)
% Paragraph 3: Our approach and key insight (what's our big idea?)
% Paragraph 4: Contributions list (what exactly did we do?)
% Paragraph 5: Paper organization (roadmap)

\section{Related Work}
% Organized by theme, not chronologically
% Each paragraph: context → existing approaches → gap → our differentiation

\section{Background / Preliminaries}
% Only include what's needed to understand the method
% Define all notation here

\section{Method / Approach}
% Start with overview/intuition, then formal details
% Include algorithm pseudocode if applicable
% Clearly state assumptions and limitations

\section{Experiments}
% Research questions (RQ1, RQ2, ...) 
% Experimental setup (datasets, baselines, metrics, hardware)
% Results with analysis (tables + figures)
% Ablation studies

\section{Discussion}
% What do results mean? Why do they matter?
% Limitations (be honest — reviewers will find them anyway)
% Future work

\section{Conclusion}
% Restate contributions
% Key takeaways (not just summary — insights)
```

### Phase 3: Writing Guidelines

#### Abstract (150-250 words)
- Sentence 1: Problem and why it matters
- Sentence 2-3: What existing approaches miss
- Sentence 3-4: Our approach and key insight
- Sentence 5-6: Key results with numbers
- Sentence 7: Broader impact / implication

#### Every Claim Must Be Supported
- Factual claim → citation
- Our claim → experimental evidence (table/figure reference)
- Intuitive claim → clearly marked as "we hypothesize" or "we conjecture"

#### Figure Quality Requirements
- Vector format (PDF for LaTeX, SVG as source)
- Font size: match paper body text (typically 10-12pt)
- Colorblind-friendly palette: use Okabe-Ito or viridis
- Self-contained: readable without body text
- Caption: descriptive, includes key takeaway

#### Table Requirements
- Bold the best result per column
- Include ± standard deviation
- Footnote any special conditions
- LaTeX format: booktabs package (no vertical lines)

### Phase 4: Self-Review Before Output
Before delivering any draft:
- [ ] Every claim has a citation or evidence?
- [ ] All notation defined before first use?
- [ ] Figures are referenced in text?
- [ ] No orphan sections (every section ≥ 2 paragraphs)?
- [ ] Contributions match what's actually shown?
- [ ] Limitations section is honest?

### Output
Write to `docs/papers/PAPER_NAME/`:
- `main.tex` (or individual section files)
- `references.bib`
- `figures/` (generated or referenced)

### Decision Rules
- If no venue specified, use NeurIPS format as default
- If asked to "write the paper", write ALL sections
- If asked to write one section, write only that section but ensure consistency with existing sections
- If results aren't available yet, write with placeholder: `\textbf{[RESULTS PENDING]}`
- Use \citet for "Author (Year)" and \citep for "(Author, Year)"
