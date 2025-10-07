# Changelog

All notable changes to SNID SAGE will be documented in this file.

## [0.9.0] - 2025-10-07

- Clustering: Adopted weighted 1-D GMM as default for cosmological clustering.
  - Per-sample weights: w_i = exp(sqrt(RLAP-CCC_i)) / σ_{z,i}^2
  - Weighted BIC model selection with resampling fallback if `sample_weight` is unsupported
  - Enforced contiguity plus hard gap splitting at Δz > 0.025; clusters are annotated with `segment_id`, `gap_split`, and point `indices`
- Uncertainty: Cluster redshift uncertainty now uses the standard error of the double-weighted mean
  - σ_SE = sqrt(Σ w_i σ_i^2 / Σ w_i)
- Template correction: `LSQ12fhs` subtype updated from `Ia-pec` to `Ia-02cx` in index and HDF5

## [0.8.1] - 2025-10-03

- Weighting: use sqrt(RLAP) instead of RLAP directly in weighting formula


## [0.8.0] - 2025-09-20

- Improved plot graphics
- New display settings
- Batch: optimal parallel execution

## [0.7.5] - 2025-09-14

- Template metadata corrections: updated `sn2016cvk` subtype from IIP to IIn and `sn1998S` subtype from IIn to II-flash in both JSON index and HDF5 storage files.

## [0.7.4] - 2025-09-04

- Enhanced wavelength range validation requiring minimum 2000 Å overlap with optical grid (2500-10000 Å), with automatic clipping and improved error handling across CLI, GUI, and core preprocessing.
- CLI: Added list-based batch mode `--list-csv` that accepts a CSV with a path column and optional per-row redshift column. Per-row redshift is applied as a fixed redshift for that spectrum; relative paths are resolved relative to the CSV file. Summary report now includes a `zFixed` column.

## [0.7.3] - 2025-09-02

- Template corrections:
  - Fixed incorrect subtype classifications for several Type Ia templates:
    - `sn2005hk`: corrected from `Ia-pec` to `Ia-02cx`
    - `sn2008A`: corrected from `Ia-pec` to `Ia-02cx`
    - `sn2013gr`: corrected from `Ia-pec` to `Ia-02cx`
    - `sn2016ado`: corrected from `Ia-pec` to `Ia-02cx`
    - `sn2008ae`: corrected from `Ia-pec` to `Ia-02cx`
    - `ASASSN-15ga`: corrected from `Ia-pec` to `Ia-91bg`
    - `ASASSN-15hy`: corrected from `Ia-pec` to `Ia-03fg`


## [0.7.2] - 2025-09-01

- Bug fixes:
  - Fixed subtype display in CLI summary output when clustering fails and only 1-2 matches survive (weak match cases)

## [0.7.1] - 2025-09-01

- Bug fixes:
  - Fixed autoscaling issue in plot display within the advanced preprocessing interface
  - Fixed subtype fetching in batch summary when only a single match survives

## [0.7.0] - 2025-08-30

- New preprocessing: added Step 0 to automatically detect and correct obvious cosmic-ray hits before standard preprocessing.
- Batch mode plotting: fixed inconsistencies when only weak matches are found; summary lines and generated plots now reflect weak-match status consistently.

## [0.6.1] - 2025-08-20

- Bug fixes and improvements:
  - Improved error handling for template loading failures in .csv
  - Fixed ejecta shifting

## [0.6.0] - 2025-08-19

- BREAKING: CLI renamed `snid` → `sage`; GUI utilities → `snid-sage-lines` / `snid-sage-templates`. Docs and entry points updated. Migration: replace `snid` with `sage`; main `snid-sage` unchanged.

- Analysis and messaging improvements:
  - Distinguish “weak match” vs “no matches” in GUI/CLI; cluster “no valid clusters” logs downgraded to INFO.
  - GUI: clearer status and dialogs for weak/no-match; added suggestion to reduce overlap threshold (`lapmin`).
  - CLI: “No good matches” suggestions now include lowering `lapmin`.
  - Batch CLI: adds “(weak)” marker in per-spectrum lines and suppresses cluster warnings.

- Clustering/logging:
  - More precise INFO messages for “no matches above RLAP-CCC” and “no types for clustering”.
