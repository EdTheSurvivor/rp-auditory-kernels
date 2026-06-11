"""
Script for computing the phoneme error rate for files. It takes an input dir to find wav files in
and finds the corresponding .phn file if the timit flag is true.
Else it takes an input tsv created from split_timit/generate_tsv with the wav file names and takes
the phonetics from the wav file name: {phoneme}_{speaker}_{stem}_{start}_{end}.wav. It saves the PER to a tsv.

Usage:
    python compute_phoneme_error_rate.py <input_dir_tsv> [--output=phoneme_error_rate.tsv] [--timit]
"""

import argparse
import os
import sys
from pathlib import Path

import librosa
import numpy as np
import torch
from jiwer import wer
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor

# The root of the project is one folder down (and contains the python_utils folder)
PROJECT_ROOT = os.path.abspath(os.path.join(os.getcwd(), ".."))

# Add project root to sys.path if not already present
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils_python import utils as u

fs = 16000

MODEL = "excalibur12/wav2vec2-large-lv60_phoneme-timit_english_timit-4k"


def phoneme_error_rate(reference: str, hypothesis: str) -> float:
    ref_phones = " ".join(reference.strip().split())
    hyp_phones = " ".join(hypothesis.strip().split())
    return wer(ref_phones, hyp_phones)


def find_phn_path(wav_path):
    wav_path = Path(wav_path)
    for ext in (".phn", ".PHN"):
        phn_path = wav_path.with_suffix(ext)
        if phn_path.exists():
            return phn_path
    return None


def get_phoneme_list(phn_path):
    phonemes = []
    with open(phn_path) as f:
        for line in f:
            parts = line.split()
            if len(parts) != 3:
                continue
            # PHN format is (start_sample end_sample phn)
            phonemes.append(parts[2])
    return " ".join(phonemes)


def get_phoneme_list_from_filename(wav_path):
    # File name format is "{phoneme}_{speaker}_{stem}_{start}_{end}.wav",
    # where {phoneme} is itself "phn_phn_..." for an arbitrary number of phonemes.
    parts = Path(wav_path).stem.split("_")
    phonemes = parts[:-4]
    return " ".join(phonemes)

def get_transcription(audio, processor: Wav2Vec2Processor, model: Wav2Vec2Processor) -> str:
    inputs = processor(audio, sampling_rate=fs, return_tensors="pt", padding=True)

    with torch.no_grad():
        logits = model(**inputs).logits
        
    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = processor.batch_decode(predicted_ids)[0]

    return transcription


def main():
    parser = argparse.ArgumentParser(description="Compute the phoneme error rate of all wav files in a directory.")
    parser.add_argument("input_dir_tsv", help="Directory (if --timit) or tsv with the wav file paths")
    parser.add_argument("--output", default="output/phoneme_error_rate.tsv", help="Path to save the PER results as a tsv file.")
    parser.add_argument("--timit", action="store_true",
                        help="If true, the input directory is a TIMIT style directory with .PHN files. If false, the phonetics will be taken from the wav name.")
    args = parser.parse_args()

    input_path = Path(args.input_dir_tsv)

    if args.timit:
        if not input_path.is_dir():
            parser.error(f"--timit is set, so input_dir_tsv must be a directory: {input_path}")
        wav_paths = u.find_wav_paths(input_path)
    else:
        if not input_path.is_file():
            parser.error(f"--timit is not set, so input_dir_tsv must be a tsv file: {input_path}")
        with open(input_path) as f:
            wav_paths = [line.strip() for line in f.readlines()[1:] if line.strip()]

    processor = Wav2Vec2Processor.from_pretrained(MODEL)
    model = Wav2Vec2ForCTC.from_pretrained(MODEL)
    model.eval()

    results = []
    for i, wav_path in enumerate(wav_paths):

        reference = ''

        if(args.timit):
            phn_path = find_phn_path(wav_path)
            if phn_path is None:
                print(f"[{i + 1}/{len(wav_paths)}] No phn file for {wav_path}, skipping.")
                continue

            reference = get_phoneme_list(phn_path)
        else:
            reference = get_phoneme_list_from_filename(wav_path)

        audio, _ = librosa.load(wav_path, sr=fs, mono=True)

        # The model's conv feature extractor needs at least 400 samples (25 ms at 16 kHz)
        # to produce any output; shorter clips crash with a kernel-size error.
        if len(audio) < 400:
            print(f"[{i + 1}/{len(wav_paths)}] Audio too short ({len(audio)} samples) for {wav_path}, skipping.")
            continue

        hypothesis = get_transcription(audio, processor, model)

        if (not args.timit):
            hypothesis = hypothesis.replace("h#", "").strip()

        per = phoneme_error_rate(reference, hypothesis)
        # print(f"ref: {reference}\ntrans:{hypothesis}")
        print(f"[{i + 1}/{len(wav_paths)}] PER for {wav_path}: {per:.2%}")
        results.append((wav_path, per))

    pers = np.array([per for _, per in results])
    print(f"Average PER over {len(pers)} files: {pers.mean():.2%}")

    if os.path.dirname(args.output):
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w") as f:
        f.write("wav_path\tper\n")
        for wav_path, per in results:
            f.write(f"{wav_path}\t{per}\n")
        f.write(f"average\t{pers.mean()}\n")
    print(f"Saved PER results to {args.output}")


if __name__ == "__main__":
    main()