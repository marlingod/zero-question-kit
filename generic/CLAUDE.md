# Project: ___PROJECT_NAME___

## Quick Config
# ─── Fill these 6 fields. Everything else auto-adapts. ───
PROJECT_TYPE: ___app | api | cli | library | fullstack | data-pipeline | mobile___
BACKEND: ___python-fastapi | python-django | node-express | node-nest | go | rust | none___
FRONTEND: ___react-next | react-vite | vue-nuxt | svelte | flutter | none___
DATABASE: ___postgres | mysql | mongodb | sqlite | supabase | none___
HOSTING: ___digitalocean | aws | vercel | fly | railway | self-hosted___
TESTING: ___pytest | jest | vitest | go-test | cargo-test___

---

## Decision Protocol — DO NOT ASK, JUST DO

When you encounter ambiguity, follow these rules.
Never ask for clarification — make the decision and document it in DECISIONS.md.

### When Requirements Are Ambiguous
1. Choose the simpler interpretation
2. Implement the minimum viable version
3. Add: `# TODO: Clarify — assumed [YOUR ASSUMPTION]`
4. Log the decision in DECISIONS.md with rationale

### Error Handling Protocol
1. Attempt 3 different fixes before reporting failure
2. Log each attempt and why it failed
3. If all 3 fail, write BLOCKER.md with reproduction steps and move to next task

### Code Conventions
- Follow the existing codebase patterns EXACTLY
- If no patterns exist, use community standards for the language:
  - Python: Black (88 chars), isort, type hints, Google-style docstrings
  - TypeScript/JS: Prettier, ESLint, strict TypeScript
  - Go: gofmt, golint
  - Rust: rustfmt, clippy
- Conventional commits: feat|fix|refactor|docs|test|chore
- Never commit to main directly
- Always run tests before committing

### Architecture Defaults (when not specified)
- Use repository/service pattern for data access
- Environment variables for all config (never hardcode)
- All dates in UTC, ISO 8601 format
- RESTful API design with OpenAPI/Swagger docs
- JWT auth with httponly cookies (when auth is needed)
- Input validation on all user-facing endpoints

### What NOT to Do
- Never ask which library to use — pick the most popular stable option
- Never ask about file structure — follow existing patterns or framework conventions
- Never ask about naming conventions — follow existing patterns
- Never ask "should I also..." — if it improves the code, just do it
- Never ask for confirmation before running safe commands

---

## Project-Specific Context
<!-- Add any project-specific notes below -->
<!-- e.g., API integrations, third-party services, domain rules -->

### Domain Rules
<!-- e.g., "All monetary values in cents", "Patient data requires HIPAA compliance" -->

### External Integrations
<!-- e.g., "Stripe for payments", "SendGrid for email", "S3 for file storage" -->

### Known Constraints
<!-- e.g., "Must support IE11", "Max 512MB memory", "Cold start < 3s" -->
