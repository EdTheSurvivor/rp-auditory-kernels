"""
Splits a TIMIT directory into per-phoneme wav segments, sorted into voiced/ and
unvoiced/ sub-folders. Silence and non-speech events (pau, epi, h#) are skipped.

Two splitting modes are available:

    Default  — one wav per phoneme entry in the .PHN file. Segments shorter than
               MIN_SAMPLES (3100) are zero-padded to that length.

    Chained (-c) — consecutive phonemes of the same voicing class are merged into
               a single segment. Silence between same-class phonemes is absorbed;
               silence at the boundary starts a new segment.

Output structure:
    <output_dir>/
        voiced/
            <phoneme>_<SPEAKER>_<SENTENCE>_<start>_<end>.wav
        unvoiced/
            <phoneme>_<SPEAKER>_<SENTENCE>_<start>_<end>.wav

In chained mode, <phoneme> is an underscore-joined sequence of all merged phonemes
(e.g. b_d_g). These names are parsed by generate_tsv.py and compute_phoneme_error_rate.py.

Usage:
    python split.py -i <timit_dir> [-o <output_dir>] [-c]

Arguments:
    -i   Path to the TIMIT directory to split (e.g. TRAIN/ or TEST/).
    -o   Output directory (default: ./timit_split).
    -c   Enable chained mode.
"""

import argparse
import soundfile as sf
import numpy as np
from pathlib import Path


# Phonemes, taken from PHONCODE.DOC

VOICED = {
    # Vowels
    "iy", "ih", "eh", "ey", "ae", "aa", "aw", "ay", "ah", "ao", "oy",
    "ow", "uh", "uw", "ux", "er", "ax", "ix", "axr",
    # Semivowels and glides (According to PHONCODE.DOC, hv is voiced)
    "l", "r", "w", "y", "el", "hv",
    # Nasals
    "m", "n", "ng", "em", "en", "eng", "nx",
    # Voiced fricatives
    "v", "dh", "z", "zh",
    # Voiced affricates
    "jh",
    # Voiced stops
    "b", "d", "g", 'dx',
}

UNVOICED = {
    # Unvoiced fricatives
    "f", "th", "s", "sh",
    # Unvoiced affricates
    "ch",
    # Unvoiced stops (q is the glottal stop)
    "p", "t", "k", "q",
    # Glottal
    "hh",
    # Stop closures
    "bcl", "dcl", "gcl", "pcl", "tck", "kcl",
    # Devoiced schwa
    "ax-h", 
}

# pau - pause
# epi - epenthetic silence
# h# - begin/end marker (non-speech events)
SILENCE = {"pau", "epi", "h#"}

MIN_SAMPLES = 3100

def classify(phoneme: str) -> str | None:
    """Classifies a phoneme as voiced, unvoiced or non-speech

    Args:
        phoneme (str): The phoneme to classify

    Returns:
        str | None: 'voiced', 'unvoiced' or None
    """    
    if phoneme in VOICED:
        return "voiced"
    if phoneme in UNVOICED:
        return "unvoiced"
    return None


def process_timit(input_dir: Path, output_dir: Path):
    """Finds all PHN files in input_dir, and splits its WAV file according to their phoneme segments.
    Outputs into output_dir/voiced/ or output_dir/unvoiced/

    Args:
        input_dir (Path): Path to the input TIMIT directory (TRAIN/ or TEST/)
        output_dir (Path): Path to the output split TIMIT files directory

    Raises:
        FileNotFoundError: If there were no PHN files found

    Returns:
        A list of how many voiced, unvoiced, skipped files were written
    """    
    (output_dir / "voiced").mkdir(parents=True, exist_ok=True)
    (output_dir / "unvoiced").mkdir(parents=True, exist_ok=True)

    stats = {"voiced": 0, "unvoiced": 0, "skipped": 0}

    phn_files = sorted(input_dir.rglob("*.PHN"))

    if not phn_files:
        raise FileNotFoundError(f"No .PHN files found under {input_dir}.")

    print(f"Found {len(phn_files)} files.\n")

    for idx, phn_path in enumerate(phn_files):
        print(f"\rProcessing file {idx}/{len(phn_files)}", end='')
        # Find the matching WAV file
        wav_path = phn_path.with_suffix(".WAV")
        if not wav_path.exists():
            print(f"  [WARN] No WAV for {phn_path.name}, skipping.")
            continue

        audio, sr = sf.read(str(wav_path))
        # Flatten to mono if needed
        if audio.ndim > 1:
            audio = audio.mean(axis=1)

        with open(phn_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) != 3:
                    continue
                # PHN format is (start_sample end_sample phn)
                start, end, phoneme = int(parts[0]), int(parts[1]), parts[2]

                category = classify(phoneme)
                if category is None:
                    stats["skipped"] += 1
                    continue

                segment = audio[start:end]
                if len(segment) < MIN_SAMPLES:
                    pad = MIN_SAMPLES - len(segment)
                    segment = np.concatenate([
                        segment,
                        np.zeros(pad, dtype=segment.dtype),
                    ])
                # File format e.g. sh_FAKS0_SA1_9640_11240.wav
                stem = phn_path.stem  # Original name, e.g. SA1
                speaker = phn_path.parent.name
                out_name = f"{phoneme}_{speaker}_{stem}_{start}_{end}.wav"
                out_path = output_dir / category / out_name
                sf.write(str(out_path), segment, sr)
                stats[category] += 1

    return stats

def process_timit_chained(input_dir: Path, output_dir: Path):
    """Finds all PHN files in input_dir, and splits its WAV file according to their phoneme segments.
    Outputs into output_dir/voiced/ or output_dir/unvoiced/

    Args:
        input_dir (Path): Path to the input TIMIT directory (TRAIN/ or TEST/)
        output_dir (Path): Path to the output split TIMIT files directory

    Raises:
        FileNotFoundError: If there were no PHN files found

    Returns:
        A list of how many voiced, unvoiced, skipped files were written
    """    
    (output_dir / "voiced").mkdir(parents=True, exist_ok=True)
    (output_dir / "unvoiced").mkdir(parents=True, exist_ok=True)

    stats = {"voiced": 0, "unvoiced": 0, "skipped": 0}

    phn_files = sorted(input_dir.rglob("*.PHN"))

    if not phn_files:
        raise FileNotFoundError(f"No .PHN files found under {input_dir}.")

    print(f"Found {len(phn_files)} files.\n")

    for idx, phn_path in enumerate(phn_files):
        print(f"\rProcessing file {idx}/{len(phn_files)}", end='')
        # Find the matching WAV file
        wav_path = phn_path.with_suffix(".WAV")
        if not wav_path.exists():
            print(f"  [WARN] No WAV for {phn_path.name}, skipping.")
            continue

        audio, sr = sf.read(str(wav_path))
        # Flatten to mono if needed
        if audio.ndim > 1:
            audio = audio.mean(axis=1)

        entries = [] # List of (start, end, phoneme)
        with open(phn_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) != 3:
                    continue
                # PHN format is (start_sample end_sample phn)
                start, end, phoneme = int(parts[0]), int(parts[1]), parts[2]
                
                entries.append((start, end, phoneme))

        def write_segment(start, end, category, phoneme):
            """Write a segment to a wav file

            Args:
                start (_type_): The start of the audio file to extract
                end (_type_): The end of the audio file to extract
                category (_type_): The category of the phonemes in the segment
                phoneme (_type_): The phonemes in the segment
            """
            # File format e.g. unvoiced_FAKS0_SA1_9640_11240.wav
            stem = phn_path.stem  # Original name, e.g. SA1
            speaker = phn_path.parent.name
            segment = audio[start:end]
            # if len(segment) < MIN_SAMPLES:
            #     pad = MIN_SAMPLES - len(segment)
            #     segment = np.concatenate([
            #         segment,
            #         np.zeros(pad, dtype=segment.dtype),
            #     ])
            out_name = f"{phoneme}_{speaker}_{stem}_{start}_{end}.wav"
            out_path = output_dir / category / out_name
            sf.write(str(out_path), segment, sr)
            stats[category] += 1

        cur_category = None
        cur_start = None
        cur_end = None
        cur_phon = ""

        for start, end, phoneme in entries:
            category = classify(phoneme)
            if category is None:
                if cur_category is not None: # Any silence in between is absorbed
                    cur_end = end
                else: # Any other silence is skipped
                    stats["skipped"] += 1
                continue

            if category == cur_category: # If we match with the last category; extend
                cur_end = end
                cur_phon += "_" + phoneme
            else:
                if cur_category is not None: # If we don't match; write to disk and start over
                    write_segment(cur_start, cur_end, cur_category, cur_phon)
                cur_category = category
                cur_start = start
                cur_end = end
                cur_phon = phoneme
            
        if cur_category is not None: # For last entry
            write_segment(cur_start, cur_end, cur_category, cur_phon)

    return stats

def main():
    parser = argparse.ArgumentParser(description="Split TIMIT by voiced or unvoiced phonemes")
    parser.add_argument("-i", required=True,
                        help="Path to the input TIMIT directory (TRAIN/ or TEST/)")
    parser.add_argument("-o", default="./timit_split",
                        help="Path to the output split TIMIT files directory (default: ./timit_split)")
    parser.add_argument("-c", action='store_true',
                        help="Process the files chained. Any following voiced/unvoiced are merged into one file. ")
    args = parser.parse_args()

    input_dir = Path(args.i)
    output_dir = Path(args.o)

    if not input_dir.exists():
        raise SystemExit(f"ERROR: input_dir '{input_dir}' does not exist.")

    print(f"Input dir : {input_dir}")
    print(f"Output dir : {output_dir}")

    stats = {}

    if args.c:
        print(f"Processing chained!")
        stats = process_timit_chained(input_dir, output_dir)
    else:
        stats = process_timit(input_dir, output_dir)

    print("\nDone!")
    print(f"Voiced segments written : {stats['voiced']}")
    print(f"Unvoiced segments written : {stats['unvoiced']}")
    print(f"Skipped (silence) : {stats['skipped']}")
    print(f"\nOutput written to: {output_dir.resolve()}")


if __name__ == "__main__":
    main()