# Security

## What PhaseLens runs

PhaseLens is instructions plus one local script. It has **no hooks, no MCP servers, no network calls of its own and no dependencies** beyond Python's standard library.

- `skills/phaselens/scripts/valuation.py` does arithmetic on the numbers passed to it and prints JSON. It reads no files and makes no network requests.
- Live prices and filings are fetched by Claude's own web tools during an analysis, under your normal permission settings.

## Reporting a vulnerability

Please report privately through [GitHub's security advisories](https://github.com/arjunpycFlow/phaselens/security/advisories/new) rather than a public issue. You'll get a response within 7 days.
