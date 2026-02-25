#!/usr/bin/env python3
import sys
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np

def generate_spectrogram(audio_path, output_path):
    # Load audio
    y, sr = librosa.load(audio_path, sr=None)
    
    # Compute spectrogram
    D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
    
    # Create figure
    plt.figure(figsize=(14, 6))
    librosa.display.specshow(D, sr=sr, x_axis='time', y_axis='hz', cmap='magma')
    plt.colorbar(format='%+2.0f dB')
    plt.title(f'Spectrogram: {audio_path}')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    
    # Compute tempo
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    tempo_val = float(tempo) if isinstance(tempo, (np.ndarray, np.generic)) else tempo
    
    # Compute rhythmic energy
    rms = librosa.feature.rms(y=y)[0]
    
    print(f"✓ Spectrogram saved to: {output_path}")
    print(f"✓ Tempo: {tempo_val:.2f} BPM")
    print(f"✓ Duration: {len(y)/sr:.2f} seconds")
    print(f"✓ Sample rate: {sr} Hz")
    
    return tempo, len(y)/sr

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_spectrogram.py <audio_file> <output_image>")
        sys.exit(1)
    
    audio_path = sys.argv[1]
    output_path = sys.argv[2]
    generate_spectrogram(audio_path, output_path)
