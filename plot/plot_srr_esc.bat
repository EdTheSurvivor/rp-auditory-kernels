@REM python sort_esc50.py C:\Users\Edwin\Documents\ESC-50-master\audio C:\Users\Edwin\Documents\ESC-50-master\meta\esc50.csv
@REM python .\plot_srr_vs_kernels_per_sec.py ESC-50-split/animals ../ResultsNORMAL/epoch_6.jld2 --name ESC-50/normal_on_animals
@REM python .\plot_srr_vs_kernels_per_sec.py ESC-50-split/animals ../ResultsVOICED/epoch_6.jld2 --name ESC-50/voiced_on_animals
@REM python .\plot_srr_vs_kernels_per_sec.py ESC-50-split/animals ../ResultsUNVOICED/epoch_6.jld2 --name ESC-50/unvoiced_on_animals
python .\merge_srr_kernels_tsv.py --output esc_animals_reconstruct_lim output/ESC-50/normal_on_animals.tsv Normal output/ESC-50/voiced_on_animals.tsv Voiced output/ESC-50/unvoiced_on_animals.tsv Unvoiced

@REM python .\plot_srr_vs_kernels_per_sec.py ESC-50-split/Exterior_urban_noises ../ResultsNORMAL/epoch_6.jld2 --name ESC-50/normal_on_exterior
@REM python .\plot_srr_vs_kernels_per_sec.py ESC-50-split/Exterior_urban_noises ../ResultsVOICED/epoch_6.jld2 --name ESC-50/voiced_on_exterior
@REM python .\plot_srr_vs_kernels_per_sec.py ESC-50-split/Exterior_urban_noises ../ResultsUNVOICED/epoch_6.jld2 --name ESC-50/unvoiced_on_exterior
python .\merge_srr_kernels_tsv.py --output esc_exterior_reconstruct_lim output/ESC-50/normal_on_exterior.tsv Normal output/ESC-50/voiced_on_exterior.tsv Voiced output/ESC-50/unvoiced_on_exterior.tsv Unvoiced

@REM python .\plot_srr_vs_kernels_per_sec.py ESC-50-split/Human_non-speech_sounds ../ResultsNORMAL/epoch_6.jld2 --name ESC-50/normal_on_human_non_speech
@REM python .\plot_srr_vs_kernels_per_sec.py ESC-50-split/Human_non-speech_sounds ../ResultsVOICED/epoch_6.jld2 --name ESC-50/voiced_on_human_non_speech
@REM python .\plot_srr_vs_kernels_per_sec.py ESC-50-split/Human_non-speech_sounds ../ResultsUNVOICED/epoch_6.jld2 --name ESC-50/unvoiced_on_human_non_speech
python .\merge_srr_kernels_tsv.py --output esc_human_non_speech_reconstruct_lim output/ESC-50/normal_on_human_non_speech.tsv Normal output/ESC-50/voiced_on_human_non_speech.tsv Voiced output/ESC-50/unvoiced_on_human_non_speech.tsv Unvoiced

@REM python .\plot_srr_vs_kernels_per_sec.py ESC-50-split/Interior_domestic_sounds ../ResultsNORMAL/epoch_6.jld2 --name ESC-50/normal_on_interior
@REM python .\plot_srr_vs_kernels_per_sec.py ESC-50-split/Interior_domestic_sounds ../ResultsVOICED/epoch_6.jld2 --name ESC-50/voiced_on_interior
@REM python .\plot_srr_vs_kernels_per_sec.py ESC-50-split/Interior_domestic_sounds ../ResultsUNVOICED/epoch_6.jld2 --name ESC-50/unvoiced_on_interior
python .\merge_srr_kernels_tsv.py --output esc_interior_reconstruct_lim output/ESC-50/normal_on_interior.tsv Normal output/ESC-50/voiced_on_interior.tsv Voiced output/ESC-50/unvoiced_on_interior.tsv Unvoiced

@REM python .\plot_srr_vs_kernels_per_sec.py ESC-50-split/Natural_soundscapes_water_sounds ../ResultsNORMAL/epoch_6.jld2 --name ESC-50/normal_on_natural
@REM python .\plot_srr_vs_kernels_per_sec.py ESC-50-split/Natural_soundscapes_water_sounds ../ResultsVOICED/epoch_6.jld2 --name ESC-50/voiced_on_natural
@REM python .\plot_srr_vs_kernels_per_sec.py ESC-50-split/Natural_soundscapes_water_sounds ../ResultsUNVOICED/epoch_6.jld2 --name ESC-50/unvoiced_on_natural
python .\merge_srr_kernels_tsv.py --output esc_natural_reconstruct_lim output/ESC-50/normal_on_natural.tsv Normal output/ESC-50/voiced_on_natural.tsv Voiced output/ESC-50/unvoiced_on_natural.tsv Unvoiced
