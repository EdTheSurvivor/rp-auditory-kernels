"""
    Script for plotting and comparing the spectral features (centroid vs bandwidth) of multiple saved sets of kernels in a single graph.
    Code taken from kernel_learning.jl and mp_utils.jl
    
    Usage:
        julia plot_spectral_features_compare.jl <JLD2_FILE_1> <LABEL_1> [<JLD2_FILE_2> <LABEL_2> ...] [--output=OUTPUT_FILE]
    Example:
        julia plot_spectral_features_compare.jl ResultsUNVOICEDREDUCEDHIGHSTOPNEW/epoch_6.jld2 Unvoiced ResultsVOICEDFILTERSTOPNEW/epoch_6.jld2 Voiced jupyter-notebook/kernels/kernels.jld2 Notebook --output=spectral_features_compare.svg
"""

import Pkg
if VERSION < v"1.11"
    Pkg.activate("MPenvironment10")
else
    Pkg.activate("MPenvironment")
end

include(joinpath(@__DIR__, "utils_julia/mp_utils.jl"))
include(joinpath(@__DIR__, "utils_julia/filter_utils.jl"))
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
    output_path = "spectral_features_compare.svg"
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

    xlim = [100, fs/2]
    ylim = [30, fs/4]

    p = plot(
        xlabel="Spectral Centroid (Hz)",
        ylabel="Spectral Bandwidth (Hz)",
        title="Kernel Spectral Features",
        xscale=:log10,
        yscale=:log10,
        xlims=xlim,
        ylims=ylim,
        legend=true,
        grid=true,
        minorgrid=true
    )

    for i in 1:2:length(path_names_args)
        jld2_path = path_names_args[i]
        label = path_names_args[i+1]
        centroids, bandwidths = get_centroids_and_bandwidths(jld2_path, fs)
        scatter!(p, centroids, bandwidths, label=label, markersize=3)
    end

    savefig(p, output_path)
    println("Saved spectral features comparison plot to ", output_path)
end

main()
