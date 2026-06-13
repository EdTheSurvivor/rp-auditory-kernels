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

BATCH_SIZE = 16

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
    "b", "d", "g", "dx",
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

def filter_phonemes(phonemes: str, phoneme_set: set[str]) -> str:
    return " ".join(p for p in phonemes.strip().split() if p in phoneme_set)

def phoneme_error_rate(reference: str, hypothesis: str) -> float:
    ref_phones = " ".join(reference.strip().split())
    hyp_phones = " ".join(hypothesis.strip().split())
    return wer(ref_phones, hyp_phones)


def find_phn_path(timit_phn_path, wav_path, timit):
    # wav_path has structure "{speaker}_{sample}_rec.WAV"
    # If timit, wav_path has structure "{sample}.WAV"
    if timit: 
        for ext in (".phn", ".PHN"):
            phn_path = Path(wav_path).with_suffix(ext)
            if phn_path.exists():
                return phn_path
    else:
        sample = Path(wav_path).stem.split("_")[1]
        timit_phn_path = Path(timit_phn_path)
        for ext in (".phn", ".PHN"):
            for phn_path in timit_phn_path.rglob(f"{sample}{ext}"):
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
    # File name format is "{category}_{phoneme}_{speaker}_{stem}_{start}_{end}_rec.wav",
    # where {phoneme} is itself "phn_phn_..." for an arbitrary number of phonemes.
    parts = Path(wav_path).stem.split("_")
    phonemes = parts[1:-5]
    return " ".join(phonemes)

def get_transcriptions(audios, processor: Wav2Vec2Processor, model: Wav2Vec2ForCTC, device: torch.device) -> list[str]:
    inputs = processor(audios, sampling_rate=fs, return_tensors="pt", padding=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        logits = model(**inputs).logits

    predicted_ids = torch.argmax(logits, dim=-1)
    return processor.batch_decode(predicted_ids)


def main():
    parser = argparse.ArgumentParser(description="Compute the phoneme error rate of all wav files in a directory.")
    parser.add_argument("input_dir", help="Directory with the wav file paths")
    parser.add_argument("--output", default="phoneme_error_rate", help="Name to save the PER results as a tsv file.")
    parser.add_argument("--timit_phn_path", 
                        help="A path to the TIMIT style directory with .PHN files. If not set, the phonetics will be taken from the wav name.")
    parser.add_argument("--timit", action='store_true', help="If the input is a TIMIT directory with standard {sample}.WAV file names" )
    args = parser.parse_args()

    input_path = Path(args.input_dir)
    timit_phn_path = args.timit_phn_path
    output = f"output/{args.output}.tsv"

    if not input_path.is_dir():
        parser.error(f"input_dir must be a directory file: {input_path}")

    wav_paths = u.find_wav_paths(input_path)

    print(f"Using GPU: {torch.cuda.is_available()}")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    processor = Wav2Vec2Processor.from_pretrained(MODEL)
    model = Wav2Vec2ForCTC.from_pretrained(MODEL)
    model.eval()
    model.to(device)

    results = []
    batch = []  # list of (i, wav_path, reference, audio)

    def process_batch(batch):
        hypotheses = get_transcriptions([audio for _, _, _, audio in batch], processor, model, device)
        for (i, wav_path, reference, _), hypothesis in zip(batch, hypotheses):
            # Our file names do not contain h#, but the transcription does give them
            if timit_phn_path is None:
                hypothesis = hypothesis.replace("h#", "").strip()

            per = phoneme_error_rate(reference, hypothesis)

            voiced_reference = filter_phonemes(reference, VOICED)
            voiced_hypothesis = filter_phonemes(hypothesis, VOICED)
            voiced_per = phoneme_error_rate(voiced_reference, voiced_hypothesis)

            unvoiced_reference = filter_phonemes(reference, UNVOICED)
            unvoiced_hypothesis =  filter_phonemes(hypothesis, UNVOICED)
            unvoiced_per = phoneme_error_rate(unvoiced_reference, unvoiced_hypothesis)

            # print(f"ref: {reference}\ntrans:{hypothesis}")
            print(f"[{i + 1}/{len(wav_paths)}] PER for {wav_path}: {per:.2%}")

            speaker = ''
            sample = ''

            if args.timit:
                path = Path(wav_path)
                speaker = path.parent.name
                sample = path.stem
            else:
                parts = Path(wav_path).stem.split("_")
                if timit_phn_path is None:
                    speaker = parts[-5]
                    sample = parts[-4]
                    phonemes = "_".join(parts[1:-5])
                    results.append((f"[{phonemes}]-{speaker}-{sample}", per, voiced_per, unvoiced_per, reference, hypothesis))
                    continue
                else:
                    speaker = parts[0]
                    sample = parts[1]

            results.append((f"{speaker}-{sample}", per, voiced_per, unvoiced_per, reference, hypothesis))

    for i, wav_path in enumerate(wav_paths):
        reference = ''

        if(timit_phn_path is not None):
            phn_path = find_phn_path(timit_phn_path, wav_path, args.timit)
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

        batch.append((i, wav_path, reference, audio))
        if len(batch) >= BATCH_SIZE:
            process_batch(batch)
            batch = []

    if batch:
        process_batch(batch)

    pers = np.array([per for _, per, _, _, _, _ in results])
    voiced_pers = np.array([voiced_per for _, _, voiced_per, _, _, _ in results])
    unvoiced_pers = np.array([unvoiced_per for _, _, _, unvoiced_per, _, _ in results])
    print(f"Average PER over {len(pers)} files: {pers.mean():.2%}")

    if os.path.dirname(output):
        os.makedirs(os.path.dirname(output), exist_ok=True)
    with open(output, "w") as f:
        if timit_phn_path is None:
            f.write("phonemes-speaker-sample\tper\tvoiced_per\tunvoiced_per\treference\thypothesis\n")
        else:
            f.write("speaker-sample\tper\tvoiced_per\tunvoiced_per\treference\thypothesis\n")
        for speaker_sample, per, voiced_per, unvoiced_per, reference, hypothesis in results:
            f.write(f"{speaker_sample}\t{per}\t{voiced_per}\t{unvoiced_per}\t{reference}\t{hypothesis}\n")
        f.write(f"average\t{pers.mean()}\t{voiced_pers.mean()}\t{unvoiced_pers.mean()}\n")
    print(f"Saved PER results to {output}")


if __name__ == "__main__":
    main()