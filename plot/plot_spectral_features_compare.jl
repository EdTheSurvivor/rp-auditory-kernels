"""
Overlays spectral spread vs. bandwidth scatter plots for one or more
kernel sets on a single log-log axes.

Each JLD2 file is paired with a display label. Kernels are loaded, their spectral
features computed at fs=16000 Hz, and plotted with a distinct marker/color per set
(cycling through triangle, circle, square and green, black, red).

Output:
    A PNG scatter plot saved to output/spectral_features_compare.png by default,
    or to the path given by --output.

Usage:
    julia plot_spectral_features_compare.jl <JLD2_1> <LABEL_1> [<JLD2_2> <LABEL_2> ...] [--output=PATH]

Arguments:
    JLD2_N      Path to a JLD2 file produced by the kernel learning pipeline.
    LABEL_N     Display label for that kernel set in the plot legend.
    --output    Output image path (default: output/spectral_features_compare.png).

Example:
    julia plot_spectral_features_compare.jl \\
        ResultsUNVOICED/epoch_6.jld2 Unvoiced \\
        ResultsVOICED/epoch_6.jld2   Voiced \\
        --output=spectral_features_compare.png
"""

import Pkg
if VERSION < v"1.11"
    Pkg.activate("../MPenvironment10")
else
    Pkg.activate("../MPenvironment")
end

include(joinpath(@__DIR__, "../utils_julia/mp_utils.jl"))
include(joinpath(@__DIR__, "../utils_julia/filter_utils.jl"))
using .mp_utils
using .filter_utils
using Plots

function get_centroids_and_bandwidths(jld2_path, fs)
    kernels = mp_utils.load_kernels_from_jld2(jld2_path)
    println("Loaded ", length(kernels), " kernels from ", jld2_path)

    centroids = Float64[]
    bandwidths = Float64[]
    for k in kernels
        c, b, _, _ = filter_utils.spectral_features(k.kernel, fs; nfreqs=1024)
        push!(centroids, c)
        push!(bandwidths, b)
    end
    return centroids, bandwidths
end

function main()
    output_path = "output/spectral_features_compare.png"
    fs = 16000
    path_names_args = String[]

    for arg in ARGS
        if startswith(arg, "--output=")
            output_path = arg[length("--output=")+1:end]
        else
            push!(path_names_args, arg)
        end
    end

    if length(path_names_args) < 2 || isodd(length(path_names_args))
        error("Usage: julia plot_spectral_features_compare.jl <JLD2_FILE_1> <LABEL_1> [<JLD2_FILE_2> <LABEL_2> ...] [--output=OUTPUT_FILE]")
    end

    xlim = [100/1000, fs/2/1000]
    ylim = [30/1000, fs/4/1000]

    xtick_vals = [0.1, 0.2, 0.5, 1, 2, 5]
    ytick_vals = [0.05, 0.1, 0.2, 0.5, 1, 2, 4]

    p = plot(
        xlabel="Spectral Spread (kHz)",
        ylabel="Spectral Bandwidth (kHz)",
        title="Kernel Spectral Features",
        xscale=:log10,
        yscale=:log10,
        xlims=xlim,
        ylims=ylim,
        xticks=(xtick_vals, string.(xtick_vals)),
        yticks=(ytick_vals, string.(ytick_vals)),
        legend=:topleft,
        grid=true,
        minorgrid=true,
        titlefontsize=14,
        guidefontsize=14,
        tickfontsize=14,
        legendfontsize=14,
    )

    markers = [:utriangle, :circle, :square]
    colors  = [:green, :black, :red]

    for i in 1:2:length(path_names_args)
        jld2_path = path_names_args[i]
        label = path_names_args[i+1]
        centroids, bandwidths = get_centroids_and_bandwidths(jld2_path, fs)
        idx    = div(i, 2) + 1
        marker = markers[mod1(idx, length(markers))]
        color  = colors[mod1(idx, length(colors))]
        scatter!(p, centroids ./ 1000, bandwidths ./ 1000, label=label, markersize=3, markershape=marker, color=color)
    end

    savefig(p, output_path)
    println("Saved spectral features comparison plot to ", output_path)
end

main()

