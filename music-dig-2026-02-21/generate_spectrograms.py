import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import os

files = [
    "01-wednesday-campanella-momotaro.wav",
    "02-sakanaction-shin-takarajima.wav",
    "03-yorushika-dakara-boku-wa.wav",
    "04-amazarashi-karappo.wav",
    "05-zazen-boys-honnoji.wav"
]

for audio_file in files:
    if not os.path.exists(audio_file):
        print(f"File not found: {audio_file}")
        continue
    
    print(f"Processing {audio_file}...")
    
    # Load audio
    y, sr = librosa.load(audio_file, sr=None)
    
    # Generate mel spectrogram
    S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=16000)
    S_dB = librosa.power_to_db(S, ref=np.max)
    
    # Plot
    plt.figure(figsize=(14, 5))
    librosa.display.specshow(S_dB, sr=sr, x_axis='time', y_axis='mel', fmax=16000)
    plt.colorbar(format='%+2.0f dB')
    plt.title(f'Mel Spectrogram: {os.path.basename(audio_file)}')
    plt.tight_layout()
    
    # Save
    output_file = audio_file.replace('.wav', '_spectrogram.png')
    plt.savefig(output_file, dpi=150)
    plt.close()
    print(f"  -> Saved {output_file}")

print("All spectrograms generated!")
