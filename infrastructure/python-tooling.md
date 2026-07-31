---
content_type: infrastructure
last_reviewed: "2026-07-31"   # bump when a human verifies the page is still accurate
---

# Python tooling baseline — uv + ruff

The shared setup for Python repos in the team. One config, copied into each repo, so that
formatting and the mechanical error checks are **enforced by a tool rather than remembered
from a document** — the same move `check_links.py` / `check_docs.py` make for the docs
layer. The reasoning behind the split below is D93; the advisory layer that points here is
the `data-conventions` skill.

> There is no team repo template yet (the only `*-cookiecutter` in the org belongs to the
> HDX scraper stack, a different toolchain). Until one exists, copy the config below.
> When a template does land, it should carry this file rather than restate it.

## The split: formatting vs linting

They get opposite treatment, because they do different jobs.

**Formatting is cosmetic and should be invisible.** Its remaining value is not beauty but
**diff hygiene**: consistent formatting means every line in a diff is a real change, which
matters for the teammates who do still read code and for anyone (human or model) reading
git history to work out *why* something is the way it is. So it runs automatically and is
never a review comment. Use **`ruff format`** and **drop `black`** — ruff's formatter is
black-compatible, so running both is redundant tooling for an identical result.

**Linting is bug-catching and worth expanding.** Each rule switched on is a sentence that
can be deleted from the house style, and it applies in repos where nobody read the house
style anyway. That is the whole trade: prose that hopes to be followed, replaced by checks
that are.

## The config

Deliberately small — a first version that is easy to argue with. Add rules when one would
have caught something real, not speculatively.

```toml
# ruff.toml (or the [tool.ruff] block of pyproject.toml)
line-length = 100
target-version = "py311"

[lint]
# Ruff's default already covers pyflakes (F) + the pycodestyle error subset (E4/E7/E9),
# which is where bare `except` (E722) and friends live.
extend-select = [
  "I",    # import sorting — deletes a whole class of pointless diff churn
  "UP",   # pyupgrade — keeps syntax current (this is what makes an "always f-strings"
          #             house rule unnecessary)
  "B",    # bugbear — mutable default args, missing `raise ... from`, loop-var capture
  "SIM",  # obvious simplifications, incl. `try/except/pass`
  "RUF",  # ruff's own checks
]
ignore = [
  "E501",  # line length belongs to the formatter, not the linter
]
```

Run both halves in CI on pull requests:

```bash
uv run ruff format --check .
uv run ruff check .
```

Locally, `ruff format` on save (or a pre-commit hook) keeps the CI check from ever being
the thing that tells you.

## What this deliberately does not cover

- **Tests.** The team does not currently write them for data code; that is a live
  question, not a settled convention, and nothing here presumes an answer.
- **Type checking** (mypy/pyright). Type hints are advised on signatures, but no checker
  is wired up — turning one on across existing repos is a project of its own.
- **The "never silently suppress exceptions" rule.** Ruff catches the crude forms; a
  deliberately narrow `except` that swallows a real failure is invisible to it.
