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

# MAJOR_CATEGORIES = {
#     0: "Animals",
#     1: "Natural_soundscapes_water_sounds",
#     2: "Human_non-speech_sounds",
#     3: "Interior_domestic_sounds",
#     4: "Exterior_urban_noises",
# }

MAJOR_CATEGORIES = {
    0: "vocalization",   # Dog
    1: "vocalization",   # Rooster
    2: "vocalization",   # Pig
    3: "vocalization",   # Cow
    4: "vocalization",   # Frog
    5: "vocalization",   # Cat
    6: "vocalization",   # Hen
    7: "ambient",        # Insects (insects do not have vocal cords)
    8: "vocalization",   # Sheep
    9: "vocalization",   # Crow
    10: "ambient",       # Rain
    11: "ambient",       # Sea waves
    12: "ambient",       # Crackling fire
    13: "ambient",       # Crickets
    14: "ambient",       # Chirping birds
    15: "transient",     # Water drops
    16: "ambient",       # Wind
    17: "ambient",       # Pouring water
    18: "ambient",       # Toilet flush
    19: "ambient",       # Thunderstorm
    20: "vocalization",  # Crying baby
    21: "transient",     # Sneezing
    22: "transient",     # Clapping
    23: "ambient",       # Breathing
    24: "transient",     # Coughing
    25: "transient",     # Footsteps
    26: "vocalization",  # Laughing
    27: "ambient",       # Brushing teeth
    28: "vocalization",  # Snoring
    29: "transient",     # Drinking/sipping
    30: "transient",     # Door knock
    31: "transient",     # Mouse click
    32: "transient",     # Keyboard typing
    33: "transient",     # Door creaking
    34: "transient",     # Can opening
    35: "ambient",       # Washing machine
    36: "ambient",       # Vacuum cleaner
    37: "transient",     # Clock alarm
    38: "ambient",       # Clock tick
    39: "transient",     # Glass breaking
    40: "ambient",       # Helicopter
    41: "ambient",       # Chainsaw
    42: "ambient",       # Siren
    43: "transient",     # Car horn
    44: "ambient",       # Engine
    45: "ambient",       # Train
    46: "transient",     # Church bells
    47: "ambient",       # Airplane
    48: "transient",     # Fireworks
    49: "ambient",       # Hand saw
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

        major_category = MAJOR_CATEGORIES[target]
        dest_dir = output_dir / major_category / category
        dest_dir.mkdir(parents=True, exist_ok=True)

        src_path = wav_dir / filename

        shutil.copy2(src_path, dest_dir / filename)

    print(f"Copied {len(rows)} files to {output_dir}")


if __name__ == "__main__":
    main()
