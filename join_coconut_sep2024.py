#!/usr/bin/env python3
"""Reconstruct the 5-column COCONUT 2.0 Paper 3 cohort locally by joining
the Results-Only Companion table against the official September 2024 COCONUT 2.0
CSV archive (https://doi.org/10.5281/zenodo.13692394).

License: MIT (script only). Locally reconstructed 'smiles' and 'standard_inchi_key'
columns derive from COCONUT 2.0 (https://doi.org/10.5281/zenodo.13692394) and remain
subject to COCONUT 2.0 and its originating source collections' terms.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import pathlib
import sqlite3
import sys
import zipfile
import zlib

EXPECTED_ZIP_MD5 = "439fca469248b2eb5194ffb75ddf62ed"
EXPECTED_CSV_SHA256 = "1900a3824324dec786c4b41b040cc39c02dcb985987fb8eb238c4857a7c1e49a"
EXPECTED_COHORT_N = 626131
EXPECTED_CSV_N = 695133

WITNESS_TRIO = {
    "CNP0244378.1": 10,
    "CNP0247789.1": 18,
    "CNP0042289.1": 19,
}


def hash_file(path: pathlib.Path, algo: str) -> str:
    h = hashlib.new(algo)
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def open_upstream_csv_bytes(archive_path: pathlib.Path, skip_checksum: bool = False) -> bytes:
    if archive_path.suffix.lower() == ".zip":
        if not skip_checksum:
            actual_md5 = hash_file(archive_path, "md5")
            if actual_md5 != EXPECTED_ZIP_MD5:
                raise ValueError(
                    f"Upstream zip MD5 mismatch for {archive_path.name}: "
                    f"expected {EXPECTED_ZIP_MD5}, got {actual_md5}"
                )
            print(f"[OK] Verified coconut-09-2024.csv.zip MD5: {actual_md5}")
        with zipfile.ZipFile(archive_path, "r") as zf:
            members = [zi for zi in zf.infolist() if not zi.is_dir()]
            members.sort(key=lambda z: z.file_size, reverse=True)
            csv_bytes = zf.read(members[0].filename)
    else:
        csv_bytes = archive_path.read_bytes()

    if not skip_checksum:
        actual_sha = hashlib.sha256(csv_bytes).hexdigest()
        if actual_sha != EXPECTED_CSV_SHA256:
            raise ValueError(
                f"Inner CSV SHA-256 mismatch: expected {EXPECTED_CSV_SHA256}, got {actual_sha}"
            )
        print(f"[OK] Verified inner coconut-09-2024.csv SHA-256: {actual_sha}")
    return csv_bytes


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--results-sqlite",
        default="coconut_paper3_626131_results.sqlite",
        help="Path to coconut_paper3_626131_results.sqlite (default: %(default)s)",
    )
    ap.add_argument(
        "--coconut-archive",
        required=True,
        help="Path to coconut-09-2024.csv.zip (or unpacked coconut-09-2024.csv) from https://zenodo.org/records/13692394",
    )
    ap.add_argument(
        "--out-sqlite",
        default="coconut_paper3_626131_joined.sqlite",
        help="Output path for reconstructed 5-column SQLite database (default: %(default)s)",
    )
    ap.add_argument(
        "--out-parquet",
        default=None,
        help="Optional output path for reconstructed 5-column Parquet file (requires pyarrow)",
    )
    ap.add_argument(
        "--out-csv",
        default=None,
        help="Optional output path for reconstructed 5-column UTF-8 CSV file",
    )
    ap.add_argument(
        "--skip-checksum",
        action="store_true",
        help="Skip strict MD5/SHA-256 verification of the upstream COCONUT archive",
    )
    args = ap.parse_args()

    res_path = pathlib.Path(args.results_sqlite).expanduser().resolve()
    arc_path = pathlib.Path(args.coconut_archive).expanduser().resolve()
    out_sql_path = pathlib.Path(args.out_sqlite).expanduser().resolve()

    if not res_path.exists():
        sys.exit(f"ERROR: Results SQLite not found: {res_path}")
    if not arc_path.exists():
        sys.exit(
            f"ERROR: Upstream archive not found: {arc_path}\n"
            "Download coconut-09-2024.csv.zip (88.9 MB) from https://zenodo.org/records/13692394"
        )
    if out_sql_path == res_path:
        sys.exit("ERROR: --out-sqlite must differ from --results-sqlite")

    ro_uri = res_path.as_uri() + "?mode=ro"
    with sqlite3.connect(ro_uri, uri=True) as rcon:
        cols = [r[1] for r in rcon.execute("PRAGMA table_info(coconut_paper3_626131_results)")]
        has_mass = "monoisotopic_mass" in cols
        if has_mass:
            results_map = {
                mid: (mass, ma)
                for mid, mass, ma in rcon.execute(
                    "SELECT mol_id, monoisotopic_mass, ma_joint_assembly "
                    "FROM coconut_paper3_626131_results ORDER BY mol_id"
                )
            }
        else:
            results_map = {
                mid: (None, ma)
                for mid, ma in rcon.execute(
                    "SELECT mol_id, ma_joint_assembly "
                    "FROM coconut_paper3_626131_results ORDER BY mol_id"
                )
            }

    if len(results_map) != EXPECTED_COHORT_N:
        raise ValueError(f"Expected {EXPECTED_COHORT_N:,} cohort rows, found {len(results_map):,}")
    print(f"[OK] Loaded {len(results_map):,} results-only cohort rows from {res_path.name}")

    csv_bytes = open_upstream_csv_bytes(arc_path, skip_checksum=args.skip_checksum)
    text_stream = io.TextIOWrapper(io.BytesIO(csv_bytes), encoding="utf-8", newline="")
    rdr = csv.DictReader(text_stream)
    expected_hdr = ["standard_inchi", "standard_inchi_key", "canonical_smiles", "identifier"]
    if rdr.fieldnames != expected_hdr:
        raise ValueError(f"Unexpected CSV header {rdr.fieldnames}; expected {expected_hdr}")

    seen_upstream_ids: set[str] = set()
    joined: list[tuple] = []
    rdkit_exact_wt = None
    if not has_mass:
        try:
            from rdkit import Chem
            from rdkit.Chem import Descriptors
            rdkit_exact_wt = (Chem, Descriptors.ExactMolWt)
        except ImportError as exc:
            raise RuntimeError(
                "2-column results table requires RDKit to recompute monoisotopic_mass."
            ) from exc

    for row in rdr:
        mid = row["identifier"]
        if mid in seen_upstream_ids:
            raise ValueError(f"Duplicate identifier in upstream CSV: {mid}")
        seen_upstream_ids.add(mid)
        rec = results_map.get(mid)
        if rec is not None:
            mass, ma = rec
            smi = row["canonical_smiles"]
            ik = row["standard_inchi_key"]
            if mass is None and rdkit_exact_wt is not None:
                mol = rdkit_exact_wt[0].MolFromSmiles(smi)
                if mol is None:
                    raise ValueError(f"RDKit failed to parse SMILES for {mid}")
                mass = float(rdkit_exact_wt[1](mol))
            joined.append((mid, smi, ik, mass, ma))

    if len(seen_upstream_ids) != EXPECTED_CSV_N:
        raise ValueError(
            f"Upstream CSV row count mismatch: expected {EXPECTED_CSV_N:,}, got {len(seen_upstream_ids):,}"
        )
    if len(joined) != EXPECTED_COHORT_N:
        raise ValueError(
            f"Cohort join incomplete: matched {len(joined):,} of {EXPECTED_COHORT_N:,} mol_ids"
        )

    joined.sort(key=lambda r: r[0])
    print(f"[OK] Strictly 1:1 join verified: {len(joined):,} / {EXPECTED_COHORT_N:,} cohort records matched")

    by_id = {r[0]: r for r in joined if r[0] in WITNESS_TRIO}
    if len(by_id) == 3:
        for w_id, exp_ma in WITNESS_TRIO.items():
            _, w_smi, _, w_mass, w_ma = by_id[w_id]
            raw_b = len(w_smi.encode("utf-8"))
            z_b = len(zlib.compress(w_smi.encode("utf-8"), 6))
            if w_ma != exp_ma or abs(w_mass - 594.137341) > 1e-5 or raw_b != 111 or z_b != 72:
                raise ValueError(
                    f"Witness check failed for {w_id}: MA={w_ma}, mass={w_mass}, raw={raw_b}, zlib={z_b}"
                )
        print("[OK] Verified Paper 3 §3.3 C30H26O13 isomer witness trio (MA = 10, 18, 19; 111 raw / 72 zlib bytes)")

    if out_sql_path.exists():
        out_sql_path.unlink()
    con = sqlite3.connect(out_sql_path)
    try:
        con.execute("PRAGMA page_size = 4096;")
        con.execute("PRAGMA journal_mode = DELETE;")
        con.execute(
            """
            CREATE TABLE coconut_paper3_626131 (
                mol_id TEXT PRIMARY KEY,
                smiles TEXT NOT NULL,
                standard_inchi_key TEXT NOT NULL,
                monoisotopic_mass REAL NOT NULL,
                ma_joint_assembly INTEGER NOT NULL
            )
            """
        )
        con.executemany("INSERT INTO coconut_paper3_626131 VALUES (?, ?, ?, ?, ?)", joined)
        con.execute(
            "CREATE INDEX idx_coconut_p3_ma_mass ON coconut_paper3_626131 (ma_joint_assembly, monoisotopic_mass)"
        )
        con.execute("CREATE INDEX idx_coconut_p3_inchikey ON coconut_paper3_626131 (standard_inchi_key)")
        con.commit()
        con.execute("VACUUM;")
        ic = con.execute("PRAGMA integrity_check;").fetchone()[0]
        if ic != "ok":
            raise RuntimeError(f"SQLite integrity_check failed: {ic}")
    finally:
        con.close()
    print(f"[OK] Wrote 5-column SQLite ({out_sql_path.stat().st_size:,} bytes): {out_sql_path}")

    if args.out_csv:
        csv_out = pathlib.Path(args.out_csv).expanduser().resolve()
        with csv_out.open("w", encoding="utf-8", newline="\n") as cf:
            cw = csv.writer(cf, lineterminator="\n")
            cw.writerow(["mol_id", "smiles", "standard_inchi_key", "monoisotopic_mass", "ma_joint_assembly"])
            cw.writerows(joined)
        print(f"[OK] Wrote 5-column CSV ({csv_out.stat().st_size:,} bytes): {csv_out}")

    if args.out_parquet:
        import pyarrow as pa
        import pyarrow.parquet as pq

        pq_out = pathlib.Path(args.out_parquet).expanduser().resolve()
        schema = pa.schema([
            pa.field("mol_id", pa.string(), nullable=False),
            pa.field("smiles", pa.string(), nullable=False),
            pa.field("standard_inchi_key", pa.string(), nullable=False),
            pa.field("monoisotopic_mass", pa.float64(), nullable=False),
            pa.field("ma_joint_assembly", pa.int64(), nullable=False),
        ])
        tbl = pa.Table.from_pydict(
            {
                "mol_id": [r[0] for r in joined],
                "smiles": [r[1] for r in joined],
                "standard_inchi_key": [r[2] for r in joined],
                "monoisotopic_mass": [r[3] for r in joined],
                "ma_joint_assembly": [r[4] for r in joined],
            },
            schema=schema,
        )
        pq.write_table(tbl, pq_out, compression="zstd")
        print(f"[OK] Wrote 5-column Parquet ({pq_out.stat().st_size:,} bytes): {pq_out}")

    print(
        "\nNOTE: Reconstructed 'smiles' and 'standard_inchi_key' columns derive from COCONUT 2.0 "
        "(https://doi.org/10.5281/zenodo.13692394) and remain subject to COCONUT 2.0 and its "
        "originating source collections' terms."
    )


if __name__ == "__main__":
    main()
