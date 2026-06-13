python .\plot_srr_vs_kernels_per_sec.py C:\Users\Edwin\Documents\TIMIT16kHz\TEST ../ResultsNORMAL/epoch_6.jld2 --name normal_on_timit
python .\plot_srr_vs_kernels_per_sec.py C:\Users\Edwin\Documents\TIMIT16kHz\TEST ../ResultsVOICED/epoch_6.jld2 --name voiced_on_timit
python .\plot_srr_vs_kernels_per_sec.py C:\Users\Edwin\Documents\TIMIT16kHz\TEST ../ResultsUNVOICED/epoch_6.jld2 --name unvoiced_on_timit
python .\merge_srr_kernels_tsv.py --output timit_midamp_reconstruct output/normal_on_timit.tsv Normal output/voiced_on_timit.tsv Voiced output/unvoiced_on_timit.tsv Unvoiced
