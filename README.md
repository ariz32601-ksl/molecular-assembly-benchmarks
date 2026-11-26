# Molecular Assembly Indices for the COCONUT Paper 3 Cohort

Chun Tang · Kunpeng Sovereign Lab · [ORCID](https://orcid.org/0009-0008-4128-2071)

This repository accompanies Paper 3, which compares exact molecular assembly indices with compression baselines across 626,131 COCONUT 2.0 records. The full internal production ledger contains 695,133 records; Paper 3 analyzes and releases results for the fixed cohort subset of 626,131 records (`is_exact == True AND phase_3_complete == True AND 1 <= ma_joint_assembly <= 36`) that met its inclusion criteria.

## Release Links (`v1.0.0` Results-Only Companion)

- **Paper 3 Preprint (ChemRxiv):** [Scale-Controlled Evaluation of Exact Molecular Assembly Index and Compression Baselines Across 626,131 Natural Products (v1)](https://doi.org/10.26434/chemrxiv.15012760/v1)
- **Canonical Dataset Archive (Zenodo `v1.0.0`):** [https://doi.org/10.5281/zenodo.24544551](https://doi.org/10.5281/zenodo.24544551)
- **Dataset Mirror (Kaggle):** [COCONUT 2.0: Exact Molecular Assembly Indices](https://www.kaggle.com/datasets/ariz32601ksl/coconut-2-0-exact-molecular-assembly-indices)
- **Upstream Source Archive (COCONUT 2.0, Sep 2024):** [https://doi.org/10.5281/zenodo.13692394](https://doi.org/10.5281/zenodo.13692394) (`coconut-09-2024.csv.zip`)

## Public Package Scope (`N = 626,131` Cohort Records)

The public `v1.0.0` release distributes the **three-column results-only companion** (`mol_id`, `monoisotopic_mass`, `ma_joint_assembly`) for the 626,131 Paper 3 cohort records in indexed SQLite (`coconut_paper3_626131_results.sqlite`) and Zstandard-compressed Apache Parquet (`coconut_paper3_626131_results.parquet`), alongside [`COLUMN_DICTIONARY.md`](COLUMN_DICTIONARY.md), [`join_coconut_sep2024.py`](join_coconut_sep2024.py), and [`SHA256SUMS.txt`](SHA256SUMS.txt). It does not distribute the full 695,133-record production ledger, and it omits upstream `smiles` and `standard_inchi_key` strings because per-collection license tags in the September 2024 COCONUT 2.0 database dump are blank or marked `Other Unknown` in 59 of 63 collections.

| Column | SQLite Type | Parquet Type | Description |
| :--- | :--- | :--- | :--- |
| `mol_id` | `TEXT PRIMARY KEY` | `string` (non-null) | COCONUT 2.0 stereovariant identifier (`CNP0000002.0` to `CNP0606860.3`); `1:1` join key to `identifier` in `coconut-09-2024.csv`. |
| `monoisotopic_mass` | `REAL NOT NULL` | `double` (non-null) | Exact monoisotopic molecular mass in Daltons (`41.026549` to `2,088.475923 Da`), computed via RDKit `Descriptors.ExactMolWt`. |
| `ma_joint_assembly` | `INTEGER NOT NULL` | `int64` (non-null) | Exact bond-level Molecular Assembly Index (`[1, 36]`, `assembly-theory==0.6.1`); source replicate columns `r1`, `r2`, and `r3` are identical across all 626,131 cohort records. |

## Local 5-Column Cohort Reconstruction

To reconstruct the full five-column Paper 3 cohort table (`mol_id`, `smiles`, `standard_inchi_key`, `monoisotopic_mass`, `ma_joint_assembly`) locally:

1. Download `coconut_paper3_626131_results.sqlite` from [Zenodo](https://doi.org/10.5281/zenodo.24544551) or [Kaggle](https://www.kaggle.com/datasets/ariz32601ksl/coconut-2-0-exact-molecular-assembly-indices).
2. Download `coconut-09-2024.csv.zip` (`88.9 MB`) from the September 2024 COCONUT 2.0 Zenodo archive ([`10.5281/zenodo.13692394`](https://zenodo.org/records/13692394)).
3. Run the local join script (Python 3 standard library only):

```bash
python3 join_coconut_sep2024.py \
  --results-sqlite coconut_paper3_626131_results.sqlite \
  --coconut-archive coconut-09-2024.csv.zip \
  --out-sqlite coconut_paper3_626131_joined.sqlite
