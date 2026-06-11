import os

def find_wav_paths(input_dir):
    wav_paths = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith(".wav"):
                wav_paths.append(os.path.join(root, file))
    if not wav_paths:
        raise FileNotFoundError(f"No wav files found in {input_dir}")
    else:
        print(f"Found {len(wav_paths)} wav files in {input_dir}")

    return wav_paths