py sort_esc50.py G:\RP\ESC-50-master\audio G:\RP\ESC-50-master\meta\esc50.csv --output_dir ESC-50-split-type
py .\plot_srr_vs_kernels_per_sec.py ESC-50-split-type/vocalization ../ResultsNORMAL/epoch_6.jld2 --name ESC-50/normal_on_vocalization
py .\plot_srr_vs_kernels_per_sec.py ESC-50-split-type/vocalization ../ResultsVOICED/epoch_6.jld2 --name ESC-50/voiced_on_vocalization
py .\plot_srr_vs_kernels_per_sec.py ESC-50-split-type/vocalization ../ResultsUNVOICED/epoch_6.jld2 --name ESC-50/unvoiced_on_vocalization
py .\merge_srr_kernels_tsv.py --output esc_vocalization_reconstruct_lim output/ESC-50/normal_on_vocalization.tsv Normal output/ESC-50/voiced_on_vocalization.tsv Voiced output/ESC-50/unvoiced_on_vocalization.tsv Unvoiced

py .\plot_srr_vs_kernels_per_sec.py ESC-50-split-type/transient ../ResultsNORMAL/epoch_6.jld2 --name ESC-50/normal_on_transient
py .\plot_srr_vs_kernels_per_sec.py ESC-50-split-type/transient ../ResultsVOICED/epoch_6.jld2 --name ESC-50/voiced_on_transient
py .\plot_srr_vs_kernels_per_sec.py ESC-50-split-type/transient ../ResultsUNVOICED/epoch_6.jld2 --name ESC-50/unvoiced_on_transient
py .\merge_srr_kernels_tsv.py --output esc_transient_reconstruct_lim output/ESC-50/normal_on_transient.tsv Normal output/ESC-50/voiced_on_transient.tsv Voiced output/ESC-50/unvoiced_on_transient.tsv Unvoiced

py .\plot_srr_vs_kernels_per_sec.py ESC-50-split-type/ambient ../ResultsNORMAL/epoch_6.jld2 --name ESC-50/normal_on_ambient
py .\plot_srr_vs_kernels_per_sec.py ESC-50-split-type/ambient ../ResultsVOICED/epoch_6.jld2 --name ESC-50/voiced_on_ambient
py .\plot_srr_vs_kernels_per_sec.py ESC-50-split-type/ambient ../ResultsUNVOICED/epoch_6.jld2 --name ESC-50/unvoiced_on_ambient
py .\merge_srr_kernels_tsv.py --output esc_ambient_reconstruct_lim output/ESC-50/normal_on_ambient.tsv Normal output/ESC-50/voiced_on_ambient.tsv Voiced output/ESC-50/unvoiced_on_ambient.tsv Unvoiced