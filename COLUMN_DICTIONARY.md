# Column Dictionary — COCONUT 2.0 Paper 3 Cohort Extract (Results-Only Companion, v1.0.0)

## 1. Scope & Architecture
This results-only companion archive distributes the `mol_id`, `monoisotopic_mass`, `ma_joint_assembly` fields for the exact pinned `N = 626,131` natural-product cohort analyzed in Paper 3 (`https://doi.org/10.26434/chemrxiv.15012760/v1`), omitting upstream chemical structure strings (`smiles` and `standard_inchi_key`) so that original assembly-index measurements are preserved across all `626,131` cohort records without redistributing third-party structure tables whose per-collection licenses are unpopulated or `Other Unknown` in `59` of `63` collections of the September 2024 COCONUT 2.0 database dump.

Users can reconstruct the complete 5-column Paper 3 cohort table (`mol_id`, `smiles`, `standard_inchi_key`, `monoisotopic_mass`, `ma_joint_assembly`) locally in seconds using `join_coconut_sep2024.py` against the official versioned COCONUT 2.0 September 2024 CSV archive (`coconut-09-2024.csv.zip`, `88,935,618` bytes, `MD5: 439fca469248b2eb5194ffb75ddf62ed`; inner `coconut-09-2024.csv`, `228,021,448` bytes, `SHA-256: 1900a3824324dec786c4b41b040cc39c02dcb985987fb8eb238c4857a7c1e49a`) from `https://doi.org/10.5281/zenodo.13692394`.

## 2. Shipped Table Schema (`coconut_paper3_626131_results`, `N = 626,131`)

| Column | SQLite Type | Parquet / Arrow Type | Description |
| :--- | :--- | :--- | :--- |
| `mol_id` | `TEXT PRIMARY KEY` | `string` (`nullable=False`) | Unique COCONUT 2.0 stereovariant accession (`CNP0000002.0` to `CNP0606860.3`). Strictly 1:1 join key to `identifier` in `coconut-09-2024.csv` (`10.5281/zenodo.13692394`). |
| `monoisotopic_mass` | `REAL NOT NULL` | `float64` (`nullable=False`) | Exact monoisotopic molecular mass in Daltons (`41.026549` to `2,088.475923 Da`), computed via RDKit `Descriptors.ExactMolWt`. |
| `ma_joint_assembly` | `INTEGER NOT NULL` | `int64` (`nullable=False`) | Exact bond-level Molecular Assembly Index (`MA` in `[1, 36]`) computed with `assembly-theory==0.6.1`; the three replicate columns (`ma_joint_assembly_r1`, `ma_joint_assembly_r2`, `ma_joint_assembly_r3`) in the `695,133`-row production ledger are identical across all `626,131` released cohort records. |

## 3. Local 5-Column Reconstruction (`join_coconut_sep2024.py`)
1. Download `coconut-09-2024.csv.zip` (`88.9 MB`) from `https://zenodo.org/records/13692394`.
2. Run:
   ```bash
   python3 join_coconut_sep2024.py --coconut-archive coconut-09-2024.csv.zip
   ```
3. The script verifies the archive checksums (`MD5: 439fca469248b2eb5194ffb75ddf62ed` and inner CSV `SHA-256: 1900a3824324dec786c4b41b040cc39c02dcb985987fb8eb238c4857a7c1e49a`), confirms a strict `626,131 / 626,131` `1:1` match on `mol_id == identifier` with `0` duplicate upstream IDs, verifies the Paper 3 §3.3 `C30H26O13` constitutional isomer trio (`CNP0244378.1` `MA = 10`, `CNP0247789.1` `MA = 18`, `CNP0042289.1` `MA = 19`; `594.137341 Da`, `111` UTF-8 SMILES bytes, `72` level-6 `zlib` bytes), and writes `coconut_paper3_626131_joined.sqlite` (plus optional `--out-parquet` or `--out-csv`).

## 4. Verification Scope & Licensing
- **Directly verifiable from this companion + `coconut-09-2024.csv.zip`:** Cohort membership (`626,131` `mol_id` keys), `monoisotopic_mass` and `standard_inchi_key` recomputation from `canonical_smiles` via RDKit (`Descriptors.ExactMolWt` and `Chem.MolToInchiKey`, audited on a 1,000-record sample with `0/1,000` mismatches against the archived column), and level-6 `zlib`/DEFLATE (`RFC 1950`) and 1D character Shannon entropy baselines.
- **Requires external code or full production ledger:** Reproducing cohort filtering from the `695,133`-row master ledger (`is_exact == True AND phase_3_complete == True AND 1 <= ma_joint_assembly <= 36`, excluding `68,815` non-exact rows, `137` `u32::MAX` overflows, `48` `MA = 0` trivial graphs, and `2` Phase-3-incomplete rows) and paired Run-1 C++ (`assemblycpp-v5`) comparisons requires `700k_COCONUT_v2_Dataset_Run2_Master.parquet` (`SHA-256: c6952c4a122eaf5a41c468ecdd1a2384c95ac3d22b030212916416a4af08485e`). Independently verifying `ma_joint_assembly` requires rerunning `assembly-theory==0.6.1` on the joined SMILES strings.
- **Licensing:** Original assembly-index results and documentation in this package are released under **CC BY 4.0**; `join_coconut_sep2024.py` is released under the **MIT License**. `CNP*` identifiers derive from **COCONUT 2.0** (`https://doi.org/10.5281/zenodo.13692394`; Chandrasekhar et al., *Nucleic Acids Research*, 2025, 53(D1), D634–D643, `https://doi.org/10.1093/nar/gkae1063`). Locally joined `smiles` and `standard_inchi_key` values remain subject to COCONUT 2.0 and its originating source collections' terms.
