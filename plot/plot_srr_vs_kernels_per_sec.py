"""
Script for plotting the SRR against the number of kernels per second. It runs for every wav file in --input_dir,
and averages the curves. The output gets saved to a png and a tsv. Short time matching pursuit is used.

Usage:
    python plot_srr_vs_kernels_per_sec.py <input_dir> <kernels_path> [--output=ssr_vs_kernels_per_sec.png] [--data_output=ssr_vs_kernels_per_sec.tsv]
"""

fs = 16000

import argparse
import glob
import os

import librosa
import matplotlib.pyplot as plt
import numpy as np

from utils_python import mp_utils as mp
from utils_python import utils_notebook as un


def compute_srr_curve(dictionary, y):
    encoded_waveform, _ = mp.short_time_matching_pursuit(dictionary, y, "abs_amplitude", 0.05)

    encoded_waveform_sorted = sorted(encoded_waveform, key=lambda tup: abs(tup[1]), reverse=True)
    _, norm_list = un.reconstruct_and_get_norm(dictionary, encoded_waveform_sorted, y)

    norm_list = np.array(norm_list)
    srr = 10 * np.log10(np.linalg.norm(y) / norm_list)
    kernels_per_second = np.linspace(1, len(norm_list) / len(y) * fs, len(norm_list))
    return kernels_per_second, srr


def main():
    parser = argparse.ArgumentParser(description="Plots the SRR vs kernels per second, averaged over a directory of wav files.")
    parser.add_argument("--input_dir", required=True, help="Input directory containing all wav files to be reconstructed.")
    parser.add_argument("--kernels_path", required=True, help="Path to the JLD2 file containing the dictionary of kernels.")
    parser.add_argument("--output", default="output/ssr_vs_kernels_per_sec.png", help="Path to save the resulting plot.")
    parser.add_argument("--data_output", default="output/ssr_vs_kernels_per_sec.tsv", help="Path to save the curve data as a tsv file.")
    args = parser.parse_args()

    wav_paths = sorted(
        p for p in glob.glob(os.path.join(args.input_dir, "*"))
        if os.path.splitext(p)[1].lower() == ".wav"
    )
    if not wav_paths:
        raise FileNotFoundError(f"No wav files found in {args.input_dir}")

    dictionary = mp.create_dictionary_from_JLD2(args.kernels_path)
    print(f"Loaded kernels from {args.kernels_path}")

    curves = []
    for wav_path in wav_paths:
        print(f"Running matching pursuit on {wav_path}...")
        y, _ = librosa.load(wav_path, sr=fs)
        y = y / np.max(np.abs(y))
        kernels_per_second, srr = compute_srr_curve(dictionary, y)
        curves.append((kernels_per_second, srr))

    max_kps = min(kernels_per_second[-1] for kernels_per_second, _ in curves)
    common_grid = np.linspace(0, max_kps)

    interpolated = np.stack([
        np.interp(common_grid, kernels_per_second, srr)
        for kernels_per_second, srr in curves
    ])
    average_srr = interpolated.mean(axis=0)

    np.savetxt(
        args.data_output,
        np.column_stack((common_grid, average_srr)),
        header="kernels_per_second\tsrr_db",
        delimiter="\t",
        comments="",
    )
    print(f"Saved curve data to {args.data_output}")

    plt.plot(common_grid, average_srr)
    plt.title("SSR vs Number of kernels/second")
    plt.xlabel("kernels/second")
    plt.ylabel("SRR [dB]")
    plt.grid()
    plt.savefig(args.output)
    print(f"Saved plot to {args.output}")


if __name__ == "__main__":
    main()
