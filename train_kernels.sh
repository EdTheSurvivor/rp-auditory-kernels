julia --threads 8 ../kernel_learning.jl VOICED voiced_paths.tsv \
--logpath training_log.tsv \
--verbose true

julia --threads 1 kernel_learning.jl VOICEDEXTEND extended_paths.tsv --logpath training_log.tsv --verbose true

julia --threads 8 kernel_learning.jl VOICEDEXTENDNEW extended_paths.tsv --logpath training_log.tsv --verbose true --mp_max_iter 10000 --mp_stop_cond 0.1 --apply_normalization true

julia --threads 8 kernel_learning.jl UNVOICEDSMALLITER unvoiced_paths.tsv --logpath training_log.tsv --mp_max_iter 50 --mp_stop_cond 0.05 --apply_normalization true --apply_filtering false --exp_threshold 0.02 --exp_range 0.15 --mp_rand_stop true --mp_stop_min 0.03 --mp_stop_max 0.08 --init_length 32 --init_min_length 16 --init_max_length 64 --min_length 16 --max_length 64

julia --threads 8 kernel_learning.jl UNVOICEDREDUCED unvoiced_paths_reduced.tsv --logpath training_log.tsv --mp_max_iter 50 --mp_stop_cond 0.05 --apply_normalization true --apply_filtering false --exp_threshold 0.01 --exp_range 0.15 --mp_rand_stop true --mp_stop_min 0.03 --mp_stop_max 0.08 --init_length 32 --init_min_length 16 --init_max_length 64 --min_length 16 --max_length 64

julia --threads 8 kernel_learning.jl UNVOICEDREDUCEDHIGHSTOP unvoiced_paths_reduced.tsv \
  --logpath training_log.tsv \
  --mp_max_iter 50 \
  --mp_stop_cond 0.12 \
  --mp_rand_stop true \
  --mp_stop_min 0.10 \
  --mp_stop_max 0.15 \
  --apply_normalization true \
  --apply_filtering false \
  --exp_threshold 0.02 \
  --exp_range 0.1 \
  --init_length 32 \
  --init_min_length 16 \
  --init_max_length 64 \
  --min_length 16 \
  --max_length 64 \
  --verbose true

  
julia --threads 8 kernel_learning.jl UNVOICEDREDUCEDHIGHSTOPNEW unvoiced_reduced_good.tsv \
  --logpath training_log.tsv \
  --mp_max_iter 150 \
  --mp_stop_cond 0.12 \
  --mp_rand_stop true \
  --mp_stop_min 0.10 \
  --mp_stop_max 0.15 \
  --apply_normalization true \
  --apply_filtering false \
  --init_length 32 \
  --init_min_length 16 \
  --init_max_length 64 \
  --min_length 16 \
  --max_length 64 \