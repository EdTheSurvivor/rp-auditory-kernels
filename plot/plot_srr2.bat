python .\plot_srr_vs_kernels_per_sec.py ../paths/voiced_paths_laptop.tsv ../ResultsNORMAL/epoch_6.jld2 --name normal_on_voiced
python .\plot_srr_vs_kernels_per_sec.py ../paths/voiced_paths_laptop.tsv ../ResultsVOICED/epoch_6.jld2 --name voiced_on_voiced
python .\plot_srr_vs_kernels_per_sec.py ../paths/voiced_paths_laptop.tsv ../ResultsUNVOICED/epoch_6.jld2 --name unvoiced_on_voiced
python .\merge_srr_kernels_tsv.py --output voiced_reconstruct output/normal_on_voiced.tsv Normal output/voiced_on_voiced.tsv Voiced output/unvoiced_on_voiced.tsv Unvoiced
python .\plot_srr_vs_kernels_per_sec.py ../paths/unvoiced_paths_laptop.tsv ../ResultsNORMAL/epoch_6.jld2 --name normal_on_unvoiced
python .\plot_srr_vs_kernels_per_sec.py ../paths/unvoiced_paths_laptop.tsv ../ResultsVOICED/epoch_6.jld2 --name voiced_on_unvoiced
python .\plot_srr_vs_kernels_per_sec.py ../paths/unvoiced_paths_laptop.tsv ../ResultsUNVOICED/epoch_6.jld2 --name unvoiced_on_unvoiced
python .\merge_srr_kernels_tsv.py --output unvoiced_reconstruct output/normal_on_unvoiced.tsv Normal output/voiced_on_unvoiced.tsv Voiced output/unvoiced_on_unvoiced.tsv Unvoiced
