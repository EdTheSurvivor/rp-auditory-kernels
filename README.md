# Auditory Kernels
This repository has some code for training the kernels (in Julia) and for computing the encodings (Python/Julia). There is also a Jupyter-notebook which hopefully helps get an idea of the Python code, and what it means to encode and decode the speech signals. Additionally, the reading materials I send previously are also added. 

## Introduction
We have a speech signal $s(t)$. This signal can, for example, be recorded using a microphone. The main idea is that we can decompose $s(t)$ based on a small number of "building blocks". These building-blocks are referred to as *auditory kernels*, with as symbol $\phi_i(t)$. There are $N_\mathrm{g}$ unique auditory kernels $\phi_{i}$, $i \in \{1, 2, \ldots, N_\mathrm{g}\}$.  We usually take $N_\mathrm{g}=32$. 

When the signal is decomposed into these auditory kernels, we are allowed to (1) reuse kernels, (2) shift kernels in time by $\tau\in\mathbb{R}$ seconds, and (3) scale the kernels by $\alpha\in\mathbb{R}$.  In this way, we can express the speech signal as

$$
s(t) = \sum_{k=0}^{K-1}\alpha_k\phi_{f(k)}(t-\tau_k) + \varepsilon(t).
$$

Where, there are $K$ kernel activations (i.e. we use $K$ kernels in total to represent the signal). Note that, since we are allowed to re-use kernels, $K$ can be larger than $N_\mathrm{g}$. This is typically the case! The function $f(k)$ basically maps a given kernel activation $k$ to the corresponding kernel, so if $k=200$ and the corresponding auditory kernel is number $i=5$ we have $f(200)=5$.  Lastly, the error signal $\varepsilon(t)$ is the part of the signal which we cannot capture by using only $K$ kernels. The error signal decreases as $K$ increases.

We may define the reconstructed signal $s_\mathrm{rec}^{[K]}$ as the part of the signal which we can capture when using $K$ kernel activations:

$$
s_\mathrm{rec}^{[K]} = \sum_{k=0}^{K-1}\alpha_k\phi_{f(k)}(t-\tau_k).
$$

It straightforwardly follows that the error $\varepsilon(t)$ is given by

$$
 \varepsilon^{[K]}(t) = s(t) - s_\mathrm{rec}^{[K]}  = s(t) - \sum_{k=0}^{K-1}\alpha_k\phi_{f(k)}(t-\tau_k),
$$

The superscript ${[K]}$ was added since, strictly speaking, the error also depends on the number of kernels used. This error is often referred to as the *residual*, with as symbol $s_{\mathrm{res}}^{[K]}(t)$. 

After encoding the signal (finding the representation based on kernel activations), $s_\mathrm{rec}^{[K]}$ is represented as a list of tuples storing (1) the selected kernel element $\phi_i$, (2) the corresponding scaling $\alpha$ and the time-shift $\tau$. This list of tuples is referred to as the *encoding* $\mathcal{S}_\mathrm{enc}^{[K]}$:

$$
\mathcal{S}_\mathrm{enc}^{[K]} = \{(f(1), \alpha_1, \tau_1), (f(2), \alpha_2, \tau_2), \ldots, (f(K), \alpha_K, \tau_K)\}
$$ 

Using $\mathcal{S}_{\mathrm{enc}}^{[K]}$, it is straightforward to find the reconstructed signal $s_\mathrm{rec}^{[K]}(t)$ using the equations you have already seen above!

It is a lot harder to find (1) the $N_\mathrm{g}$ unique kernels (this set of kernels is referred to as the *dictionary*) and (2) the encoding. Generally speaking,  finding the optimal encoding (i.e. keeping $K$ as small as possible while simultaneously minimizing the error $\varepsilon(t)$ ) is NP-hard. Thus, only approximate methods are feasible. 

#### How to find the encoding?
First assume that we already have the unique kernels (the dictionary) available. This can be, for example, because we selected a standard set of kernels. Let's have a look at how to find the encoding. 

For finding the encoding we use an algorithm called *matching pursuit* (MP). You can read about it on the [wikipedia](https://en.wikipedia.org/wiki/Matching_pursuit) or in the [original paper](https://doi.org/10.1109/78.258082) from 1993 ([pdf](reading_materials/Mallat1993 - Matching Pursuits with Time Frequency Dictionaries.pdf)). Usually MP is formulated somewhat different (without cross-correlations), but the  basic idea is as follows:

- Initialise the residual signal as $s^{[1]}_\mathrm{res}(t) = s(t)$ (the residual signal is effectively the error $\varepsilon(t)$) and set $k=0$. 
- Repeat the following until some stopping condition is met
	- Compute the cross-correlation between each of the dictionary elements (auditory kernels) and the $s^{[k]}_\mathrm{res}(t)$ (so you get $N_\mathrm{g}$ cross-correlations)
	- Select the dictionary element $i=f(k)$ with the highest absolute cross-correlation
	- Select the time $\tau_k$ corresponding to the time with the highest absolute cross-correlation
	- Set $\alpha_k$ equal to the value of the cross-correlation at time $\tau_k$ for the selected dictionary element (note that this requires the $l_2$ norm of each kernel to be 1, i.e. $||\phi_i||_2=1$). 
	- Update $s_\mathrm{res}[k]$ by subtracting the selected dictionary element at the correct timeshift $\tau$ and scaling $\alpha$
	- $k \leftarrow k + 1$

#### How to find the dictionary elements (auditory kernels)?
For finding the dictionary elements we use the approach outlined in the [paper of Smith and Lewicki](https://doi.org/10.1038/nature04485) ([pdf](reading_materials/Smith2006 - Efficient Auditory Coding.pdf)). The basic idea is quite simple:

- Select the number of dictionary elements $N_\mathrm{g}$ you want to use
- Initialise them as random noise of 100 samples in length
- Repeat:
	- Compute the encoding and the error signal using matching pursuit
	- Update the kernels based on the error signal
	- Trim or expand the kernels based on the energy in the tails. 
	- normalise each kernel to have a norm of 1 (i.e. $\phi_i \leftarrow \phi_i / ||\phi_i||$)
	
#### This repository
In this repository there is some code for learning the kernels (in Julia) and for performing matching pursuit (Python/Julia). There is also a variant of matching pursuit which we called short-time matching pursuit. The reason for this is that matching pursuit becomes very slow as the length of $s(t)$ increases due to the convolutions (or cross-correlations) involved. 

The remainder of this README focuses on the reading-material and on how to use the code in the repo. (And there might still be bugs!!!! So let me know if you find any!)

## Reading material
The reading material can be found in the folder `reading material`. I  recommend everyone to read/look at:

-  [The slides we used during our first meeting](reading_material/slides1_intro_to_project_slides.pdf),	
- [Lewicki2010](reading_material/Lewicki2010 - A Signal Take on Speech.pdf) (very easy to read),
- [Smith2006](reading_material/Smith2006 - Efficient Auditory Coding.pdf) (This paper is more technical, but it is the paper which is the center of this research project so study it carefully!)
- [A youtube talk by Lewicki](https://www.youtube.com/watch?v=UN_j04vyvS0&list=PL_wSRP1hDkU34HgXGFBTiC5kv_s0KsuTs&index=6)
- Optionally you can also go through [Ming2009](reading_material/Ming2009 - Efficient Coding in Human Auditory Perception.pdf)
- You might also want to look up material on matching pursuit. Probably there is a lot of good stuff on Youtube. Anyway, for your reference, [Mallat1993](reading_material/Mallat1993 - Matching Pursuits with Time Frequency Dictionaries.pdf) is the original paper.
- You can optionally have a look at both posters. One of them is from a research project on bat echolocation ([poster](reading_material/poster_bat_paper_draft.pdf)), and the other is from a presentation Jorge and I gave a while ago ([poster](reading_material/poster_dag_vd_fonetiek.pdf)).

If you are interested in the efficient coding hypothesis, you can read:

- [Barlow1961](reading_material/Barlow1961 - Possible Principles Underlying the Transformations of Sensory Messages.pdf) (the original paper)
- [Barlow2001](reading_material/Barlow2001 - Redundancy Reduction Revisited.pdf) (Barlow reflecting back on the original paper) 
- [Loh2014](reading_material/Loh2014 - Efficient Coding Hypothesis and an Introduction to Information Theory.pdf) (A nice introduction, this paper might be the best starting point out of these three?)

If you are interested in a nice (but very extensive!) overview of human speech recognition:

- [Allen2005](reading_material/Allen2005 - Articulation and Intelligibility.pdf)

Now let's have a look at some reading per research question.

**RQ1:** (non-linear cochlear signal processing)

- [Thoret2023](reading_material/Thoret2023 - Hearing As Adaptive Cascaded Envelope Interpolation.pdf)

**RQ2:** (number of kernels)

 - No specific extra reading

**RQ3:** (Reverberation)

- Have a look at the "room impulse response", you should be able to easily find a lot about this. Also look at the mirror-image source method.
- You might be interested in [Mesgarani2014](reading_material/Mesgarani2014 - Mechanisms of Noise Robust Representation of Speech in Primary Auditory Cortex.pdf), which is on how the auditory system deals with noise/reverb.
- You might be interested in the [research project](https://repository.tudelft.nl/record/uuid:4cfcac57-22ec-4ecc-b133-bfa5db2babc3) by Baturalp of last year.

 **RQ4:** (speech production)
 
 - Search for some materials on phonetics/speech production.
- [Ladefoged2012](reading_material/Ladefoged2012 - Vowels and Consonants.pdf) is an introductory textbook on phonetics. You might be able to find it in the library, otherwise I have a paperback version you can use if you are interested.
- You might also be interested in [Miller1955](reading_material/Miller1955 - An Analysis of Perceptual Confusions among Some English Consonants.pdf). I found it a very cool paper.

**RQ5:** (Social calls of bats)

- [Prat2017](reading_material/Prat2017 - An Annotated Dataset of Egyptian Fruit Bat Vocalizations across Varying Contexts and during Vocal Ontogeny.pdf) is a open-source partially labeled dataset of bat-social calls in different conditions (mother-pup pairs and bigger groups)
- [Salles2019](reading_material/Salles2019 - Auditory Communication Processing in Bats_ What We Know and Where to Go..pdf)
- You should definitely have a look at the [bachelor thesis](https://repository.tudelft.nl/record/uuid:f7d76b24-ee79-46ea-a85d-78fcbdfbafff) on bat echolocation of Aleksandra last year. This paper is accepted for publication at ICASSP 2026. The paper should become available soon, I will add it here when that happens. This is the [draft of the poster for the presentation](reading_materials/poster_bat_paper_draft.pdf)

## Getting started with the code

- I recommend you to start by going through `jupyter-notebook/getting_started.ipynb`. This jupyter-notebook briefly explains matching pursuit and shows you how to apply it to a speech signal. Also let me know if there are parts of the notebook which would require more detail! After going through this notebook, you should be familiar with the basics of encoding/decoding the speech signals using the kernels, and how to use the basics of `utils_python/matching_pursuit.py`.
- There is also a small script which allows you to train the kernels. Note that you do need Julia for training them. 
	- To construct the dataset, run `uv run python training/construct_train_set.py` (or however you run your python scripts). This creates a small dataset of audiofiles using 3 unique kernels: a sawtooth centered at zero, a square wave, and a piece of a sinusoid. 
	- To train the kernels, run `./training/example_train_on_simple_train_set.sh`.  This script effectively calls `julia kernel_learning.jl` with a few default settings. 
	- When training the kernels, the folder `resultsSIMPLE` is created. In here, you will find:
		- Stored kernels (as `.jld2` file)
		- Images of the kernels (as `.svg` file). The image also shows the length of the kernel in samples (in red) and the horizontal line is the $y=0$ axis.
		- The spectral-centroid spectral-spread curve of the kernels
		- A `.pdf` which plots the number of kernels used per second against the signal-to-residue ratio (SRR) for each of the epochs. 
	- Note that I tested everything on Ubuntu. I hope it works on windows, but I might have hardcoded some filepaths here and there, so let me know if you cannot get it to work!

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


### Training
The functions in the code can also be used for training the auditory kernels. The most complete example is `kernel_learning.jl`. This is the code I use myself for training the kernels (both locally and on the Delftblue cluster). 

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
The code has a bunch of other options apart from those already described. These mostly come from things I implemented (of which many did not turn out to be useful). I listed all below

 - `<ID>`; String. Positional argument. It effectively sets the folder in which the results are stored. For example, if `<ID>=TIMIT`, the data will be stored in `ResultsTIMIT`.
 - `<train_tsv_file>`; String. Positional argument. Path to the `.tsv` containing the training examples. The default expected column name within the `.tsv` is `path_wav`, but it can be modified by setting `--tsv_col_path`: 
 	- `--tsv_col_path`; String. Default: `path_wav`. The name of the column within the training TSV file which contains the paths to the audio files.
 - `--tsv_col_segments`; optional argument (default: `nothing`). By specifying this argument, you can train on segments of the audio instead of running on the full audio segments. 
 	- These segments should be listed in the  `<train_tsv_file>` in the column specified by `--tsv_col_segments <column_name>`. The expected format is JSON with `start` and `end`. For example, if there is only one segment, it looks like `[{"start": 3616, "end": 46797}]`. The numbers are the samples, so you should be careful if you resample data at some point. 
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
 
 

## Warning
It is very much possible that the code in `tests/...` does not work... I don't recall updating it...

