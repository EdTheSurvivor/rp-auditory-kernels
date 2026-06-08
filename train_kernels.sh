julia --threads 8 ../kernel_learning.jl VOICED voiced_paths.tsv \
--logpath training_log.tsv \
--verbose true

julia --threads 1 kernel_learning.jl VOICEDEXTEND extended_paths.tsv --logpath training_log.tsv --verbose true

julia --threads 8 kernel_learning.jl VOICEDEXTENDNEW extended_paths.tsv --logpath training_log.tsv --verbose true --mp_max_iter 10000 --mp_stop_cond 0.1 --apply_normalization true

julia --threads 8 kernel_learning.jl UNVOICEDNOFILTER unvoiced_paths.tsv --logpath training_log.tsv --mp_max_iter 1000 --mp_stop_cond 0.01 --apply_normalization true --apply_filtering false --exp_threshold 0.01