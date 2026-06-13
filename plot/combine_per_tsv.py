"""
Script for combining multiple phoneme error rate tsv files as produced by
compute_phoneme_error_rate.py into a single tsv.

Rows with the same speaker-sample are merged: the speaker-sample and
reference columns are kept once, while the per and hypothesis columns are
taken from each input file and renamed to <file_stem>_per and
<file_stem>_hypothesis.

Usage:
    python combine_per_tsv.py <TSV_1> [<TSV_2> ...] [--output=combined_per]
"""

import argparse
import csv
import os
from pathlib import Path


def read_tsv(tsv_path):
    """Turns a tsv into an object with objects of every row,
    with the first row as key
    """
    with open(tsv_path, newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        key_field = reader.fieldnames[0]
        rows = {}
        for row in reader:
            rows[row[key_field]] = row
    return key_field, rows


def main():
    parser = argparse.ArgumentParser(description="Combine multiple phoneme error rate tsv files into a single tsv.")
    parser.add_argument("tsvs", nargs="+", help="Paths of the input tsv files.")
    parser.add_argument("--output", default="combined_per", help="Name to save the combined results as a tsv file.")
    args = parser.parse_args()

    output = f"output/{args.output}.tsv"

    key_field = None
    combined = {}
    order = []

    for tsv_path in args.tsvs:
        stem = Path(tsv_path).stem
        file_key_field, rows = read_tsv(tsv_path)
        if key_field is None:
            key_field = file_key_field

        for key, row in rows.items():
            if key not in combined:
                combined[key] = {key_field: key, "reference": row.get("reference", "")}
                order.append(key)

            entry = combined[key]
            if not entry.get("reference"):
                entry["reference"] = row.get("reference", "")
            entry[f"{stem}_per"] = row.get("per", "")
            entry[f"{stem}_hypothesis"] = row.get("hypothesis", "")

    fieldnames = [key_field, "reference"]
    for tsv_path in args.tsvs:
        stem = Path(tsv_path).stem
        fieldnames.append(f"{stem}_per")
        fieldnames.append(f"{stem}_hypothesis")

    if os.path.dirname(output):
        os.makedirs(os.path.dirname(output), exist_ok=True)
    with open(output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t", restval="")
        writer.writeheader()
        for key in order:
            writer.writerow(combined[key])
    print(f"Saved combined PER results to {output}")


if __name__ == "__main__":
    main()
