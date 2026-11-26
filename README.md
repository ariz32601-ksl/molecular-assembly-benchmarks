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
```

The script verifies `coconut-09-2024.csv.zip` (MD5: `439fca469248b2eb5194ffb75ddf62ed`) and inner `coconut-09-2024.csv` (SHA-256: `1900a3824324dec786c4b41b040cc39c02dcb985987fb8eb238c4857a7c1e49a`), confirms an exact `626,131 / 626,131` one-to-one match on `mol_id == identifier`, checks the Paper 3 §3.3 $\text{C}_{30}\text{H}_{26}\text{O}_{13}$ (`594.137341 Da`) constitutional isomer trio (`CNP0244378.1` MA = 10, `CNP0247789.1` MA = 18, `CNP0042289.1` MA = 19; 111 UTF-8 SMILES bytes / 72 level-6 zlib bytes), and writes the indexed 5-column SQLite database (plus optional `--out-parquet` or `--out-csv`). See `COLUMN_DICTIONARY.md` for full verification scope and limitations.

## Checksums (SHA-256) & Table-Content Digest

| File | Size (Bytes) | SHA-256 |
| :--- | ---: | :--- |
| `coconut_paper3_626131_results.sqlite` | 44,777,472 | `ce5f002e388dd558839e50b11391dac600cd484761a39a7b4ffc7f6f567b9302` |
| `coconut_paper3_626131_results.parquet` | 3,881,452 | `ecad65d4b429c8fbe16d7ca7979e663d8a7ec630cce0c1a00cb0f8d10e91346a` |
| `join_coconut_sep2024.py` | 11,121 | `e3cf93beb23c060d223729ecd39d1dce856c3389ec611de7159f851dbef19341` |
| `COLUMN_DICTIONARY.md` | 4,746 | `8eb5ef850af4ba1330606c78e4c0cb9834025c38aa240a74688ac0cd144625ce` |

**Canonical 3-Column Table-Content Digest** (supplementary cross-format SQLite/Parquet parity check across all $626,131 \times 3 = 1,878,393$ cells; does not replace file hashes): `baabda0c394b5a23531dce7ac27050ed15029b966a38504a961aed08e144a3fb`

## Licensing & Attribution

* **Companion data tables & documentation:** CC BY 4.0
* **Join script (`join_coconut_sep2024.py`):** MIT License
* **Upstream `CNP*` identifier attribution (CC BY 4.0 Section 3(a)):** `mol_id` values were adapted from `coconut-09-2024.csv.zip` (`identifier` filtered from 695,133 to 626,131 cohort records, renamed `mol_id`, stripped of structure columns, and paired with computed `monoisotopic_mass` and `ma_joint_assembly` columns) from the September 2024 release of COCONUT 2.0 (`10.5281/zenodo.13692394`; Chandrasekhar et al., *Nucleic Acids Research*, 2025, 53(D1), D634–D643, `10.1093/nar/gkae1063`). Locally reconstructed `smiles` and `standard_inchi_key` columns remain subject to COCONUT 2.0 and its originating source collections' terms.

## Related Preprints

* **Paper 1:** Process-Isolated Molecular Assembly Benchmarking (v3) [https://doi.org/10.26434/chemrxiv.15004164/v3]
* **Paper 2:** Molecular Assembly Enumeration vs. 1D Dictionary Compression (v1) [https://doi.org/10.26434/chemrxiv.15012530/v1]
