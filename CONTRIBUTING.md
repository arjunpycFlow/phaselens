# Contributing to PhaseLens

Thanks for helping. PhaseLens gives people prices they may act on, so changes are held to a high bar: every rule should be sourced, every number reproducible, and every behavior change measured.

## Ground rules

- **Cite a source** for any new rule, threshold or method (a filing standard, a textbook, a well-known practitioner's published guide).
- **Keep `SKILL.md` lean.** Claude already knows finance; add only what it wouldn't do on its own. Detail goes in `skills/phaselens/references/`, one level deep. `SKILL.md` stays under 500 lines.
- **Never add financial-advice language** ("you should buy"). The skill produces analysis and price bands; the decision stays with the investor.

## Development setup

```bash
git clone https://github.com/arjunpycFlow/phaselens.git
cd phaselens
python3 -m pip install pytest
make test       # unit tests + SKILL.md rules
make validate   # needs Claude Code installed
```

Load your working copy in Claude Code for one session without installing it:

```bash
claude --plugin-dir .
```

## Changing the skill's behavior

Run the eval suite before and after your change and paste both summaries in the pull request:

```bash
make eval   # claude plugin eval . --allow-tools Bash
```

Each case runs with and without the plugin, so the `Δ` column shows what PhaseLens adds. Evals make real model calls on your plan or API account. Add a case under `evals/` for any new behavior; see the [eval docs](https://code.claude.com/docs/en/plugin-evals).

## Changing `valuation.py`

Add or update tests in `tests/test_valuation.py`. Prefer closed-form checks (a Gordon-growth special case, a round trip through the reverse DCF) over snapshot numbers.

## Releasing (maintainers)

1. Bump `version` in `.claude-plugin/plugin.json` and add a `CHANGELOG.md` entry.
2. Merge to `main`.
3. Tag and push: `git tag v1.1.0 && git push origin v1.1.0`. The release workflow attaches `phaselens.zip`.

## Code of conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md).
