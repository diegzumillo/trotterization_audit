# Week-5 Reference Audit

Date: 2026-04-25

Scope: quick non-destructive audit of `references.bib` for PRD/PRR readiness. No bibliography entries were edited.

## Mechanical Checks

- total BibTeX entries: 31
- duplicate keys: none found
- entries missing `title`, `author`, or `year`: none found

## Entries Without DOI, arXiv eprint, or URL

These entries have enough core metadata for BibTeX, but should be checked before manuscript revision. Older classic references may legitimately lack DOI fields in the current file; modern references should preferably have DOI or arXiv identifiers.

- `lloyd1996universal`
- `suzuki1985decomposition`
- `heyl2019localization`
- `sieberer2019kickedtop`
- `halimeh2021singlebody`
- `zohar2016quantum`
- `martinez2016realtime`
- `dalmonte2016lgtqi`
- `dimeglio2024hepqc`
- `homeier2023realistic`
- `borla2020confined`
- `kogut1975hamiltonian`
- `banks1976strong`
- `wilson1974confinement`
- `kogut1979intro`

## Cleanup Recommendation

Before editing the manuscript, do a reference pass with three goals:

1. Add DOI fields where stable and available, especially for modern journal articles.
2. Keep arXiv identifiers for preprints and recent papers where the published version may still be unstable.
3. Standardize journal names and capitalization for APS style.

This is tracked as pending in the PRD/PRR readiness checklist in `results/week5_full_report.md`.
