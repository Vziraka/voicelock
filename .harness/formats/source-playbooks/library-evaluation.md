# Source playbook — evaluating a library / dependency

Load this before searching. Work top to bottom; the further down the list, the
weaker the source.

1. **Registry page** (npm / PyPI / crates.io / etc.): last publish date, weekly
   downloads, dependents. Quote the date and the number.
2. **The repo**: releases tab (cadence), issues tab (are maintainers actually
   responding?), last commit date.
3. **Official docs**: do they exist, do they cover your use case, are they
   current with the latest release?
4. **Community signal** (last resort): recent discussions. Blogs and tutorials
   rank last — they age fastest and rarely say which version they describe.

What good looks like: a release or commit within ~12 months, real adoption
(downloads and dependents, never star count alone), docs that answer your
actual question. **Gray zone = FAIL** — if you can't confirm it's alive, it's
out. The human may waive the bar; a waiver is recorded as waived in
`memory/decisions.md`.

Fit beats fame: judge every candidate against the spec's Outcome and
Constraints sections, not against what's popular.
