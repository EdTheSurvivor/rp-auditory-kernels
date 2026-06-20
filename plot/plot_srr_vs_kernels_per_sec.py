"""
Plots average SRR (Signal-to-Residual Ratio) vs. kernels-per-second over a set of wav files.

For each wav file, short-time matching pursuit is run using a kernel dictionary loaded
from a JLD2 file. The resulting per-file SRR curves are interpolated onto a common grid
and averaged. Reconstructed wavs and per-file outputs are written to output/<name>/.

Outputs (all under output/):
    <name>.png   — plot of the averaged SRR curve
    <name>.tsv   — tab-separated (kernels_per_second, srr) table of the averaged curve
    <name>/      — reconstructed wav files for each input

Processing is parallelized across all available CPU cores.

Usage:
    python plot_srr_vs_kernels_per_sec.py <input_dir> <kernels_path> [--name NAME]

Arguments:
    input_dir      Directory of wav files to reconstruct, or a TSV file with a
                   'path_wav' column listing absolute wav paths.
    kernels_path   Path to the JLD2 file containing the kernel dictionary.
    --name         Base name for all output files (default: ssr_vs_kernels_per_sec).
"""

fs = 16000

import argparse
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed

import librosa
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf
from pathlib import Path

# The root of the project is one folder down (and contains the python_utils folder)
PROJECT_ROOT = os.path.abspath(os.path.join(os.getcwd(), ".."))

# Add project root to sys.path if not already present
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils_python import mp_utils as mp
from utils_python import utils_notebook as un
from utils_python import utils as u

def reconstruct(dictionary, y, output_path):
    encoded_waveform, _ = mp.short_time_matching_pursuit(dictionary, y, "abs_amplitude", 0.03)

    encoded_waveform_sorted = sorted(encoded_waveform, key=lambda tup: abs(tup[1]), reverse=True)
    reconstructed_waveform, norm_list = un.reconstruct_and_get_norm(dictionary, encoded_waveform_sorted, y)

    sf.write(output_path, reconstructed_waveform, fs)
    return norm_list

def compute_srr_curve(norm_list, y):
    norm_list = np.array(norm_list)
    srr = 10 * np.log10(np.linalg.norm(y) / norm_list)
    kernels_per_second = np.linspace(1, len(norm_list) / len(y) * fs, len(norm_list))
    
    return kernels_per_second, srr


_dictionary = None
_reconstruct_dir = None

def _init_worker(kernels_path, reconstruct_dir):
    global _dictionary, _reconstruct_dir
    _dictionary = mp.create_dictionary_from_JLD2(kernels_path)
    _reconstruct_dir = reconstruct_dir


def _process_wav(wav_path):
    y, _ = librosa.load(wav_path, sr=fs)
    y = y / np.max(np.abs(y))

    wav_path_obj = Path(wav_path)
    new_stem = f"{wav_path_obj.parent.name}_{wav_path_obj.stem}_rec"
    output_path = Path(_reconstruct_dir) / wav_path_obj.with_stem(new_stem).name

    norm_list = reconstruct(_dictionary, y, output_path)
    return compute_srr_curve(norm_list, y)


def main():
    parser = argparse.ArgumentParser(description="Plots the SRR vs kernels per second, averaged over a directory of wav files.")
    parser.add_argument("input_dir", help="Input directory containing all wav files to be reconstructed, or a .tsv file with a 'path_wav' column listing wav paths.")
    parser.add_argument("kernels_path", help="Path to the JLD2 file containing the dictionary of kernels.")
    parser.add_argument("--name", default="ssr_vs_kernels_per_sec", help="Name of the wav and kernel combo")
    args = parser.parse_args()

    output_img = f"output/{args.name}.png"
    output_tsv = f"output/{args.name}.tsv"
    reconstruct_dir = f"output/{args.name}"

    os.makedirs(reconstruct_dir, exist_ok=True)

    if args.input_dir.lower().endswith(".tsv"):
        with open(args.input_dir, "r") as f:
            lines = [line.strip() for line in f.readlines()]
        header = lines[0].split("\t")
        col_idx = header.index("path_wav")
        wav_paths = [line.split("\t")[col_idx] for line in lines[1:] if line]
        print(f"Found {len(wav_paths)} wav files in {args.input_dir}")
    else:
        wav_paths = u.find_wav_paths(args.input_dir)

    num_workers = os.cpu_count()

    curves = []
    with ProcessPoolExecutor(max_workers=num_workers, initializer=_init_worker, initargs=(args.kernels_path, reconstruct_dir)) as executor:
        futures = {executor.submit(_process_wav, wav_path): wav_path for wav_path in wav_paths}
        for i, future in enumerate(as_completed(futures)):
            print(f"[{i + 1}/{len(wav_paths)}] Finished matching pursuit on {futures[future]}")
            kernels_per_second, srr = future.result()
            if len(kernels_per_second) == 0:
                print(f"Warning: skipping {futures[future]}, no kernels were extracted (file may be too short).")
                continue
            curves.append((kernels_per_second, srr))

    max_kps = min(kernels_per_second[-1] for kernels_per_second, _ in curves)
    common_grid = np.linspace(0, max_kps)

    interpolated = np.stack([
        np.interp(common_grid, kernels_per_second, srr)
        for kernels_per_second, srr in curves
    ])
    average_srr = interpolated.mean(axis=0)

    np.savetxt(
        output_tsv,
        np.column_stack((common_grid, average_srr)),
        header="kernels_per_second\tsrr",
        delimiter="\t",
        comments="",
    )
    print(f"Saved curve data to {output_tsv}")

    plt.plot(common_grid, average_srr)
    plt.title("SSR vs Number of kernels/second")
    plt.xlabel("kernels/second")
    plt.ylabel("SRR [dB]")
    plt.grid()
    plt.savefig(output_img)
    print(f"Saved plot to {output_img}")


if __name__ == "__main__":
    main()
