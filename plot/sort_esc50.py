"""
Script for sorting ESC-50 wav files into category sub-folders based the classes and major categories.
These are taken from the ESC-50 metadata csv (columns: filename,fold,target,category,esc10,src_file,take).

Files are copied into: <output>/<major_category>/<category>/<filename>

where <major_category> is determined by the target number:
0-9: Animals
10-19: Natural soundscapes & water sounds
20-29: Human, non-speech sounds
30-39: Interior/domestic sounds
40-49: Exterior/urban noises

Usage:
    python sort_esc50.py <WAV_DIR> <CSV_PATH> <OUTPUT_DIR>
"""

import argparse
import csv
import shutil
from pathlib import Path

MAJOR_CATEGORIES = {
    0: "Animals",
    1: "Natural_soundscapes_water_sounds",
    2: "Human_non-speech_sounds",
    3: "Interior_domestic_sounds",
    4: "Exterior_urban_noises",
}


def main():
    parser = argparse.ArgumentParser(description="Sorts ESC-50 wav files into category sub-folders.")
    parser.add_argument("wav_dir", help="Directory containing the ESC-50 wav files.")
    parser.add_argument("csv_path", help="Path to the ESC-50 metadata csv.")
    parser.add_argument("--output_dir", default="ESC-50-split", help="Directory to write the sorted folders to.")
    args = parser.parse_args()

    wav_dir = Path(args.wav_dir)
    output_dir = Path(args.output_dir)

    with open(args.csv_path, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    for row in rows:
        filename = row["filename"]
        target = int(row["target"])
        category = row["category"]

        major_category = MAJOR_CATEGORIES[target // 10]
        dest_dir = output_dir / major_category / category
        dest_dir.mkdir(parents=True, exist_ok=True)

        src_path = wav_dir / filename

        shutil.copy2(src_path, dest_dir / filename)

    print(f"Copied {len(rows)} files to {output_dir}")


if __name__ == "__main__":
    main()
