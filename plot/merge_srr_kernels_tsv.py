"""
Script for plotting multiple SRR vs kernels/second curves (as produced by
plot_srr_vs_kernels_per_sec.py) in a single graph.

Usage:
    python merge_srr_kernels_tsv.py <TSV_1> <LABEL_1> [<TSV_2> <LABEL_2> ...] [--output=merged_srr_vs_kernels_per_sec]
"""

import argparse
import os

import matplotlib.pyplot as plt
import numpy as np


def main():
    parser = argparse.ArgumentParser(description="Plot multiple SRR vs kernels/second tsv files in a single graph.")
    parser.add_argument("tsv_label", nargs="+", help="Pairs of <tsv_path> <label>.")
    parser.add_argument("--output", default="merged_srr_vs_kernels_per_sec", help="Name of the resulting plot.")
    args = parser.parse_args()

    os.makedirs("output", exist_ok=True)

    if len(args.tsv_label) % 2 != 0:
        raise ValueError("Expected pairs of <tsv_path> <label>.")

    for i in range(0, len(args.tsv_label), 2):
        tsv_path = args.tsv_label[i]
        label = args.tsv_label[i + 1]

        kernels_per_second, srr = np.loadtxt(tsv_path, skiprows=1, unpack=True)
        plt.plot(kernels_per_second, srr, label=label)

    plt.title("SSR vs Number of kernels/second")
    plt.xlabel("kernels/second")
    plt.ylabel("SRR [dB]")
    plt.legend()
    plt.grid()
    plt.savefig(f"output/{args.output}.png")
    print(f"Saved plot to output/{args.output}.png")


if __name__ == "__main__":
    main()