julia --threads 8 kernel_learning.jl FULLUTTERANCE <timit_dir>.tsv \
 --logpath training_log.tsv \
 --mp_max_iter 1000 \
 --mp_stop_cond 0.12 \
 --mp_rand_stop true \
 --mp_stop_min 0.10 \
 --mp_stop_max 0.15 \
 --apply_normalization true  \
 --tsv_col_segments segments \
