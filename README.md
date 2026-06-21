[![DOI](https://zenodo.org/badge/1262948901.svg)](https://doi.org/10.5281/zenodo.20786161)
# Auditory Kernels

This repository contains code for training auditory kernels (in Julia) and for computing the encodings (Python/Julia). There is also a Jupyter-notebook which hopefully helps get an idea of the Python code, and what it means to encode and decode the speech signals. As well there are scripts included to split TIMIT, encode sounds and generate plots.

This repository is part of the TU Delft CSE3000 Research Project: Efficient Auditory Coding in Speech Categorization, by Edwin van der Heijden. `ResultsFULLUTTERANCE, ResultsUNVOICED and ResultsVOICED` contain the trained kernel sets used in the research. The parameters used are included in `train_kernels.sh` under each Results folder.

## How to Cite

If you use this code, please cite it as follows.

### BibTeX
```bibtex
@software{van_der_heijden_2026_20786162,
  author       = {van der Heijden, Edwin and
                  de Groot, Dimme},
  title        = {Auditory Kernels Codebase},
  month        = jun,
  year         = 2026,
  publisher    = {Zenodo},
  version      = {v1.0.0},
  doi          = {10.5281/zenodo.20786162},
  url          = {https://doi.org/10.5281/zenodo.20786162},
}
```
### APA
```
van der Heijden, E., & de Groot, D. (2026). Auditory Kernels Codebase (v1.0.0). Zenodo. https://doi.org/10.5281/zenodo.20786162
```
### IEEE
```
E. van der Heijden and D. de Groot, “Auditory Kernels Codebase”. Zenodo, Jun. 21, 2026. doi: 10.5281/zenodo.20786162.
```



## Getting started with the code

- It is recommended to start by going through `jupyter-notebook/getting_started.ipynb`. This jupyter-notebook briefly explains matching pursuit and shows you how to apply it to a speech signal. After going through this notebook, you should be familiar with the basics of encoding/decoding the speech signals using the kernels, and how to use the basics of `utils_python/matching_pursuit.py`.
- There is also a small script which allows you to train the kernels. Note that you do need Julia for training them.
  - To construct the dataset, run `uv run python training/construct_train_set.py` (or however you run your python scripts). This creates a small dataset of audiofiles using 3 unique kernels: a sawtooth centered at zero, a square wave, and a piece of a sinusoid.
  - To train the kernels, run `./training/example_train_on_simple_train_set.sh`. This script effectively calls `julia kernel_learning.jl` with a few default settings.
  - When training the kernels, the folder `resultsSIMPLE` is created. In here, you will find:
    - Stored kernels (as `.jld2` file)
    - Images of the kernels (as `.svg` file). The image also shows the length of the kernel in samples (in red) and the horizontal line is the $y=0$ axis.
    - The spectral-centroid spectral-spread curve of the kernels
    - A `.pdf` which plots the number of kernels used per second against the signal-to-residue ratio (SRR) for each of the epochs.

## Further notes

Below there is some more information. In particular, most settings of `kernel_learning.jl` are explained.

### Modules

#### Julia utils

- `Par_measure.jl`: a port of the Matlab version of the auditory distortion measure by Van de Par et al.
- `mp_utils.jl`: implements matching pursuit, short-time matching pursuit, and some related functions.
- `filter_utils.jl`: just wraps some functions of `DSP` in a way I found convenient
- `train_utils.jl`: some other stuff used during training.

### Python utils

- `mp_utils.py`
- `gammatone.py`
- `filter_utils.py`

### Split TIMIT

- `split.py`: Splits a TIMIT directory into per-phoneme wav segments, sorted into voiced/ and
  unvoiced/ sub-folders. Silence and non-speech events (pau, epi, h#) are skipped.
- `generate_tsv.py`: Generates a TSV listing wav file paths from a directory of split TIMIT segments
  (as produced by split.py), for use as input to downstream scripts.
- `sort_esc50`: Script for sorting ESC-50 wav files into category sub-folders.

### Plot

- `compute_phoneme_error_rate.py`: Computes Phoneme Error Rate (PER) for all wav files in a directory using a
  Wav2Vec2 phoneme recognition model, then saves per-file and average results to a TSV.
- `combine_per_tsv.py`: Merges multiple PER TSV files (as produced by compute_phoneme_error_rate.py) into one. `plot_srr_vs_kernels_per_sec.py`: Plots average SRR (Signal-to-Residual Ratio) vs. kernels-per-second over a set of wav files. Also saves reconstructed files.
- `merge_srr_kernels_tsv.py`: Overlays multiple SRR vs. kernels/second curves on a single rate-fidelity plot.
- `plot_spectral_features_compare.jl`: Overlays spectral spread vs. bandwidth scatter plots for one or more
  kernel sets on a single log-log axes.

### Training

The functions in the code can also be used for training the auditory kernels. The most complete example is `kernel_learning.jl`.

#### Basics for `kernel_learning.jl`

- To run this code, you would typically run: `julia --threads <number_of_threads> kernel_learning.jl <ID> <TSVfile> --logpath <Path for storing logs>`. Here:
  - `<ID>` is an identifier for your current run,
  - `<TSVfile>` is a `.tsv` file containing the path to your training examples (by default in the column `path_wav`),
  - `-- <name of logfile>` is the file where you want your training log to be stored.
  - So a typical run would look like `julia --threads 8 kernel_learning.jl TIMIT TIMIT_train_local.tsv --logpath training_log.tsv`.
  - The learned kernels will be stored in `Results<ID>`, so in the case above, it will be `ResultsTIMIT`.
- Sometimes, you want to continue from a previous iteration. In this case, you can use `--continue_count` (or `-c`).For example, if I want to continue from iteration 250, I would do:
  `julia --threads 8 kernel_learning.jl TIMIT TIMIT_train_local.tsv --logpath training_log.tsv -c 250`. This requires the result of the 250th iteration to be stored in `ResultsTIMIT`!

#### A list of options

- `<ID>`; String. Positional argument. It effectively sets the folder in which the results are stored. For example, if `<ID>=TIMIT`, the data will be stored in `ResultsTIMIT`.
- `<train_tsv_file>`; String. Positional argument. Path to the `.tsv` containing the training examples. The default expected column name within the `.tsv` is `path_wav`, but it can be modified by setting `--tsv_col_path`:
  - `--tsv_col_path`; String. Default: `path_wav`. The name of the column within the training TSV file which contains the paths to the audio files.
- `--tsv_col_segments`; optional argument (default: `nothing`). By specifying this argument, you can train on segments of the audio instead of running on the full audio segments.
  - These segments should be listed in the `<train_tsv_file>` in the column specified by `--tsv_col_segments <column_name>`. The expected format is JSON with `start` and `end`. For example, if there is only one segment, it looks like `[{"start": 3616, "end": 46797}]`. The numbers are the samples, so you should be careful if you resample data at some point.
  - For an example, look at `training/TIMIT_train_local.tsv`. Here the segments are the regions of the signal containing voice-activity, but you can also use it to split on particular types of speech etc.
- `--verbose`; `true` or `false` (default). The code gives extra output when this is set to `true`.
- `--logpath`; optional argument, example: `training_log.tsv`. You can set this to collect some logging data of the training examples. In particular, it stores the signal-to-residue ratio (SRR) and the number of kernels/second used. The file `training_log.tsv` is stored in `Results<ID>/training_log.tsv`. I'm actually not sure what happens if you specify an extra path instead of the file itself.
  - If you specify a logpath, you will also get a .pdf which shows the signal-to-residue ratio and the number of kernels/second of each audiofile per epoch.
- `--storage_frequency`; Int. Default: `500`. The kernels learned every `--storage_frequency` training examples will be stored in `Results<ID>/...`:
  - The kernels itself are stored (`kernels_it<ITERATION_NUMBER>.jld2`)
  - A plot of the kernels is stored (`kernels_it<ITERATION_NUMBER>.svg`)
  - A plot of the spectral centroid-spread curve is stored (`kernels_dist_it<ITERATION_NUMBER>.svg`).
  - Note that, at the end of each epoch, the results are also stored.
- `--random_seed`. Int. Default: `42`. Sets the random seed.
- `--fs`. Int. Default: `16000`. Sets the sampling rate in Hz. Audio will be up- or downsampled if required.
- `--apply_normalization`: Boolean. Default: `true`. Whether or not to apply amplitude normalisation (i.e., if $s$ is the speech signal and amplitude normalisation is used, $\max |s| = 1$).
- `--apply_filtering`: Boolean. Default: `true`. Whether or not to apply filtering on the input signal.
  - `--filter_f_low`; Default: `100`; Controls the lower cutoff frequency of the filter (in Hz)
  - `--filter_f_high`; Default: `7000`; Controls the higher cutoff frequency of the filter (in Hz)
  - `--filter_length`: Sets the length of the filter. A longer filter can be "sharper". Default: `3001`. Note that if you use a different sample rate you might also want to change the length accordingly. There are some rules of thumb for selecting the filter-length.

#### Matching pursuit parameters

- `--mp_stop_type`; String. Default: `amplitude`. Other option: `iterations` (I'm not sure if this has been tested).
- `--mp_stop_cond`; Float64 or Int. Default: `0.05`. Stopping condition for matching pursuit.
  - If `--mp_stop_type amplitude`, the iterations stop after a kernel is placed which is scaled with an amplitude $|\alpha|< 0.05$
  - If `--mp_stop_type iterations`, it will effectively set the number of kernels used per frame of the audio. I am not sure if this has been tested, so it might not work.
- `--mp_rand_stop`; Boolean. Default: `false`. For each training iteration, pick a random stop condition (uniformy distributed between `--mp_stop_min` and `--mp_stop_max`)
  - `--mp_stop_min`; Float64. Default: `0.02`.
  - `--mp_stop_max`; Float64. Default: `0.1`.
- `--fixed_MP_param`; Boolean. Default: `true`. This fixes the parameters (such as the window length etc.) during the short-time matching pursuit iterations.
- `--mp_max_iter`; Int. Default: `40000`. This is the maximum number of matching pursuit iterations per audiofile/window/segment.

#### Initialising kernels

When training, you can either initialise a fresh set of kernels or continue from a previous iteration.

##### Training from scratch

- `--Ng`; Int. Default: `32`. The number of kernels when initialising the kernels.
- `--initial_type`; String. Default: `gaussian`. The type of the initial kernels (`gaussian` (default), `gammatone`, `impulse`, `filtered_gaussian`). `gaussian` grabs samples from a normal distribution. `gammatone` initalises a gammatone filter bank and depends on Python being reachable. I kind of forgot how that worked. The `filtered_gaussian` filters the initial kernels to force them into a certain frequency response characteristic. The `impulse` simply initialises all kernels as a spike.
- `--window_initial_kernels`; Boolean. Default: `false`. Applies a hamming window to the initialised kernels.
  - I'm not sure if it operates for all initial types, but it definitely does for `gaussian`.
  - A hamming window basically forces the edges of the initialised kernel to go to zero, while the amplitude increases as we move towards the center of the initialised kernel.
- `--init_length`; Int. Default: `100`. The initial length of each kernel.
- `--init_spacing`; String. Default: `nothing`. Other option: `linear`. Instead of initialising the kernels as equal length, you can also space their lengths linearly between `--init_min_length` and `--init_max_length`.
  - `--init_min_length`; Int. Default: `64`. Minimum initial kernel length. Used when `--init_spacing` is not `nothing`.
  - `--init_max_length`; Int. Default: `256`. Maximum initial kernel length. Used when `--init_spacing` is not `nothing`.

##### Continuing from old kernels

- `--continue_count` or `-c`; Int. Default: `0`. This argument can be set to continue from a certain previous iteration. This iteration should have been stored. By default, the code stores the kernels every `--storage_frequency` training examples.
- `--path_initial_kernels`; optional argument (default `nothing`). If you do not want to continue from a previous iteration but instead load specific kernels, you can use this argument to specify the path (e.g. `kernels_i_like_a_lot.jld2`). I think this overrides the `--continue_count` in terms of loading the kernels, but it will probably still skip the first `<continue_count>` iterations if you specify it.

#### Kernel updates

The kernels are updated during training. For example they can be shrinked and expanded.

- `--exp_frequency`; Int. Default: `100`. The kernels are expanded (or trimmed) every `--exp_frequency` number of iterations.
- `--exp_range`; Float64. Default: `0.1`. The kernels expand if the energy in expansion range exceeds `--exp_threshold`. The `--expansion_range` is as percentage of the kernel length.
- `--exp_threshold`; Float64. Default: `0.02`. See `--exp_range`.
- `--min_length`; Int. Default: `32`. The minimum length of the kernels.
- `--max_length`; Int. Default `256`. The maximum length of the kernels.
- `--ortho_flag`; Boolean. Default: `false`. If `true`: the kernels are orthogonalised every `--exp_frequency` iterations. Note that the implementation of this is very naive.
- `--kernel_dropout`; Int. Default: `0`. Specifies the number of kernels which are dropped. Every iteration, some kernels can be dropped (and put back later). The idea is that this helps each kernel to get some shape.

#### Training parameters

- `--step_size`; Float64. Default: `0.0025`. The stepsize of each kernel update
- `--clamp_gradient`; Float64. Default: `1.0`. The gradient can be clamped to avoid overshooting.
- `--smooth_gradient`; Float64. Default: `0.0`. The gradient can be updated in a smoothed fashion (another typical value is `0.7`).
- `--max_train_iterations`; Int. Default: `100000`. The maximum number of training iterations.
- `--max_epochs`; Int. Default: `6`. The maximum number of epochs.

#### Schedule

- `--epoch_schedule`; String. Default: `1,2,3,4,5,6,7,8`. Some parameters (see below) can be updated every epoch.
- `--stepsize_schedule`; String. Default: `1,1,1,1,1,1,1,1`. The stepsize is multiplied by the parameter within the `--stepsize_schedule` at the start of each epoch in `--epoch_schedule`. So you can use it to modify the stepsize as a function of the epoch.
- `--exp_threshold_schedule`; String. Default: `1,1,1,1,1,1,1,1`. The expansion threshold is multiplied by the parameter within the `--exp_threshold_schedule` at the start of each epoch in `--epoch_schedule`. Set the number to negative to avoid updating (trimming or expanding) kernels.
- `--kernel_dropout_schedule`; String. Default: `1,1,1,1,0,0,0,0`. A binary value indicating if the kernel is dropped (number of kernels that are dropped is specified by `--kernel_dropout`). If it is `1`, kernels are dropped for that epoch. If it is `0`, no kernels are dropped.

#### Other

- `--weightscheme`; String. Default: `uniform`. There is the option to weight the kernels in matching pursuit based on a `--weightscheme preemphasis` scheme. I tried and it does not work at all. This might be due to a bug though. I hoped that the higher frequencies would come out better when implementing this.
  - `--weightcoeff`; Float64. Default: `0.7`. The weight of the preemphasis filter (in case it is used). A parameter of `0.7` implies that the weight of the kernel is calculated based on the preemphasis vector `[1, -0.7]`.
- `--big_segment`; Boolean. Default: `false`. When segments are used and `--big_segment true`, there is a single segment considered which starts at the start of the first segment and ends at the end of the last segment.
- `--dev_tsv_file`; optional argument. This is similar to `train_tsv_file`, but for the development set. I did not implement any functionality yet related to the development set, so it is **useless** at this point.
