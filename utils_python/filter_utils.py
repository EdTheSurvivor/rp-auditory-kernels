# This code defines some functions which I find handy when working with filters in python
# Functions:   
#   fir_coeffs = get_FIR(Fs = 16000, filter_order = 64, cutoff_freqs = [100, 6000])
#   filtered_signal = apply_fir_filter(signal_data, fir_coeffs)
#   center_freq, bandwidth = estimate_fir_bandwidth_and_center_frequency(filter_coeffs, fs = 1.0, plotting = False,  Nfreqz = 2048)

import scipy.signal as signal
import numpy as np
import matplotlib.pyplot as plt
import glob
from os.path import join, abspath, exists
import emd


def get_FIR(Fs = 16000, filter_order = 64, cutoff_freqs = [20, 7000]):
    # Define FIR filter parameters 
    #filter_order = 64
    #cutoff_freqs = [100, 6000]  # Hz

    # Design FIR bandpass filter using scipy.signal.firwin()
    fir_coeffs = signal.firwin(filter_order + 1, 
                               cutoff_freqs, 
                               fs=Fs, 
                               pass_zero=False)  # Bandpass filter
    return fir_coeffs


# Function to apply FIR filter
def apply_fir_filter(signal_data, fir_coeffs):
    return signal.filtfilt(fir_coeffs, 1.0, signal_data)


def spectral_centroid(w, h):
    """
        w : the frequency axis for the digital filter response (single-sided, ie output of freqz)
        h : the corresponding filter response (freq. domain)
        note that the unit of the centroid is the unit of w
        centroid : (output) the centroid frequency (same unit of w)
    """
    power = np.abs(h)**2
    return np.sum(w * power) / np.sum(power)


def ERB(w,h):
    """
        Equivalent Rectangular Bandwidth (ERB)
        w : the frequency axis for the digital filter response (single-sided, ie output of freqz)
        h : the corresponding filter response (freq. domain)
        note that the unit of the ERB is the unit of w
        ERB : (output) the equivalent rectangular bandwidth (same unit of w)
    """
    power = np.abs(h)**2
    area = np.trapz(power, w)  # Area under the power curve   
    denominator = np.max(power) 
    ERB = area/denominator
    return ERB


def spectral_spread(w, h, centroid):
    power = np.abs(h)**2
    return np.sqrt(np.sum(((w - centroid) ** 2) * power) / np.sum(power))


def spectral_skewness(w, h, centroid, spread):
    power = np.abs(h)**2
    return np.sum(((w - centroid) ** 3) * power) / (np.sum(power) * spread**3)


def spectral_kurtosis(w, h, centroid, spread):
    power = np.abs(h)**2
    return np.sum(((w - centroid) ** 4) * power) / (np.sum(power) * spread**4)


def spectral_entropy(h, normalise=True):
    power = np.abs(h)**2
    p = power / np.sum(power)           # probability distribution
    p = p[p>0]
    entropy = -np.sum(p * np.log2(p))
    if normalise:
        entropy /= np.log2(len(power))
    return entropy


def peak_frequency(w, h):
    power = np.abs(h)**2
    peak_idx = np.argmax(power)
    peak_mag = power[peak_idx]
    return w[peak_idx]
    
    
def bandwidth_3db(w, h, method='last_crossing'):
    # method: take first time -3dB is crossed or last time (`last_crossing` vs `first_crossing`)
    #
    # Returns: bandwidth_3db, center_frequency (center of bandwidth), peak_frequency (frequency with max power)
    power = np.abs(h)**2
    peak_idx = np.argmax(power)
    peak_mag = power[peak_idx]
    threshold = peak_mag / 2    # -3 dB point
    
    if method == "first_crossing":
        # left crossing
        left = peak_idx
        while left > 0 and power[left] >= threshold:
            left -= 1

        # right crossing
        right = peak_idx
        while right < len(power)-1 and power[right] >= threshold:
            right += 1
    elif method == "last_crossing":
        indices = np.where(power >= threshold)[0] 
        left = indices[0]
        right = indices[-1]
    else:
        raise ValueError(f"Invalid value specified for method ({method}). Use 'last_crossing' or 'first_crossing'")
    
    bandwidth_3db = w[right] - w[left]
    center_frequency = (w[right] + w[left])/2  # Note that this is only a particular definition!!!!! peak-frequency is a vague term
    peak_frequency = w[peak_idx]
    return bandwidth_3db, center_frequency, peak_frequency
    

def plot_filter_params(w, h, spectral_spread, centroid, filter_coeffs, results):
    mag_db = 20*np.log10(abs(h))
    mag_3db = np.max(mag_db) - 3
    f_low = centroid - spectral_spread
    f_high = centroid + spectral_spread

    fig, axes = plt.subplots(2, 1, figsize=(8, 8))  # Create 2 subplots
    # **1st Plot: Frequency Response**
    axes[0].plot(w, mag_db, label="Magnitude Response", color="blue")
    axes[0].axvline(f_low, color="red", linestyle="--", label=f"F_low = {f_low:.1f} Hz")
    axes[0].axvline(f_high, color="red", linestyle="--", label=f"F_high = {f_high:.1f} Hz")
    axes[0].axvline(centroid, color="green", linestyle="--", label=f"Center = {centroid:.1f} Hz")
    axes[0].axhline(mag_3db, color="black", linestyle="--", label="-3dB Level")
    # Labels & title
    axes[0].set_ylim([-20, 20])
    axes[0].set_xlim([0, 8000])
    axes[0].set_xlabel("Frequency (Hz)")
    axes[0].set_ylabel("Magnitude (dB)")
    axes[0].set_title("Frequency Response, centroid and spectral spread")
    axes[0].legend()
    axes[0].grid(True)
    # **List Spectral Features**
    feature_text = "\n".join([f"{key.capitalize()}: {value:.2f}" for key, value in results.items()])
    axes[0].text(0.02, 0.95, feature_text, transform=axes[0].transAxes, fontsize=10,
                 verticalalignment='top', bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))

    # **2nd Plot: Time-Domain Filter Coefficients**
    axes[1].plot(filter_coeffs)  # Discrete impulse response
    axes[1].set_xlabel("Samples")
    axes[1].set_ylabel("Amplitude")
    axes[1].set_title("Time-Domain Filter Coefficients")
    axes[1].grid(True)

    # Adjust layout and display
    plt.tight_layout()
    plt.show()


def estimate_fir_params(filter_coeffs, fs = 1.0, plotting = False, Nfreqz = 2048, features=["centroid", "spread", "entropy"]):
    """
    Estimate spectral properties of FIR filter
    
    Parameters:
        filter_coeffs  : array-like, FIR filter coefficients.
        fs : float, Sampling frequency (default=1.0 for normalized frequency).
        plotting : boolean, True for plotting the filter and some properties
        Nfreqz : int, number of points in freqz (response digital filter)
        features : list of str
            Which features to compute (default: ["centroid","spread"]).
            Choose from ["centroid", "spread", "skewness", "kurtosis", "entropy", "ERB", "peak_frequency", "bandwidth_3db", "center_frequency"]
            Note: some features require other features: 
                centroid --> spread --> skewness --> kurtosis 
                peak_frequency, bandwidth_3db, center_frequency are computed in one go. Specifying one will yield the others as well. 
    Returns:
        results : dict
            Dictionary with requested spectral features.
    """
    # Compute the frequency response
    if len(filter_coeffs) > Nfreqz:
        print("Warning in estimate_fir_bandwidth_and_center_frequency: length(Nfreqz) < length(filter_coeffs)")  
        Nfreqz = 2*len(filter_coeffs)  # Increase Nfreqz

    w, h = signal.freqz(filter_coeffs, worN = Nfreqz, fs = fs)  # w in Hz
 
    results = {}
    if "centroid" in features:
        results["centroid"] = spectral_centroid(w, h)
    if "spread" in features:
        results["spread"] = spectral_spread(w, h, results["centroid"])
    if "skewness" in features:
        results["skewness"] = spectral_skewness(w, h, results["centroid"], results["spread"])
    if "kurtosis" in features:
        results["kurtosis"] = spectral_kurtosis(w, h, results["centroid"], results["spread"])
    if "entropy" in features:
        results["entropy"] = spectral_entropy(h)
    if "ERB" in features:
        results["ERB"] = ERB(w, h)
    if {"bandwidth_3db", "peak_frequency", "center_frequency"} & set(features):
        # bandwidth_3db, center_frequency, peak_frequency
        # Note: bandwidth_3db takes a method parameter: "first_crossing" or "last_crossing". 
        # .... "last_crossing" apprxoimates results of smith and lewicki better.... (default) 
        results["bandwidth_3db"], results["center_frequency"], results["peak_frequency"] = bandwidth_3db(w, h, method = "last_crossing")

    if plotting:
        plot_filter_params(w, h, results["spread"], results["centroid"], filter_coeffs, results)

    return results
    
    
def ReadDataCarney(directory, type_of_data = ".txt"): 
    print("Loading data Carney")
    files = sorted(glob.glob(join(directory, '**', '*' + type_of_data), recursive=True))

    print(f"Found {len(files)} files for Carney Data")
    
    bandwidths = []
    center_freqs = []
    revcors = []
    sample_rates = []
    for filename in files:
        filepath = abspath(filename)
        
        try:
            errorFlag = False
        
            # Load the text file
            data = np.genfromtxt(filepath, usecols=(0, 1), delimiter=None, invalid_raise=False, skip_header=1)
            data = data[~np.isnan(data).any(axis=1)] # Remove invalid rows
    
            # Extract columns
            time = data[:, 0]         # First column (Time)
            magnitude = data[:, 1]    # Second column (Magnitude)    
            Fs = 1.0/(time[1] - time[0])*1000 #*1000 # Sampling frequency [Hz]
            
            if np.sum(np.abs(magnitude))<1e-12:
                errorFlag = True
                print(f"Error: The file '{filepath}' has a total power < 1e-12 (Exact: {np.sum(np.abs(magnitude))}).")
                
      
        except FileNotFoundError:
            errorFlag = True
            print(f"Error: The file '{filepath}' was not found.")
        except Exception as e:
            errorFlag = True
            print(f"Error: {e}")

        if not errorFlag:
            revcors.append(magnitude)
            sample_rates.append(Fs)
        
    res = list(set(sample_rates))
    if len(res) > 1:
        print(f"Warning: detected multiple sampling rates ({res})")

    return revcors, sample_rates


def process_data_Carney(revcors, sample_rate = 20000, plotting=False, features=["centroid", "spread", "entropy", "peak_frequency", "bandwidth_3db"]):
    # Load in a filter
    fir_coeffs = get_FIR(sample_rate)
    revcors_f = []
    
    # (1) Filter revcors and remove the ones which likely only contain noise.
    for revcor in revcors:
        revcor_f = apply_fir_filter(revcor, fir_coeffs)
    
        # Check if there are filters for which the filtering is too agressive
        fraction_energy = np.linalg.norm(revcor_f)/np.linalg.norm(revcor)
        if fraction_energy < 0.8:
            pass # In these cases, the data likely only contains noise.
            #print(f"Warning: large percentage of energy got filtered out {fraction_energy}")
            #plt.plot(revcor)
            #plt.plot(revcor_f)
            #plt.show()
        else:
            revcors_f.append(revcor_f/np.linalg.norm(revcor_f))
    
    # (2) We now have the filtered revcors. Compute some statistics. 
    results = []
    for revcor_f in revcors_f:
        result = estimate_fir_params(revcor_f, fs = sample_rate, plotting = plotting, Nfreqz = 2048, features=features)
        results.append(result)
    return results, revcors_f
 
        
def CEI(x, max_imfs=6, max_iters=1, conf=None):
    """Compute Cascaded Envelope Interpolation (CEI) modes using EMD."""
    
    if max_iters > 1:
        print("Warning: note that setting max_iters to larger than 1 is not CEI anymore!")
        
    imf_opts = {'max_iters': max_iters, 'energy_thresh': None, 'stop_method': 'fixed'}
    if conf == None:
        conf = emd.sift.get_config('sift')
    conf['max_imfs'] = max_imfs
    conf['imf_opts'] = imf_opts

    #  Compute the modes
    cei_modes = emd.sift.sift(x, **conf)
    return cei_modes
