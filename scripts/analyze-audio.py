#!/usr/bin/env python3
import sys
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np

def generate_spectrogram(audio_path, output_path):
    """Generate spectrogram from audio file"""
    # Load audio
    y, sr = librosa.load(audio_path, sr=None)
    
    # Create figure with multiple plots
    fig, axes = plt.subplots(3, 1, figsize=(14, 10))
    
    # 1. Mel Spectrogram
    S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)
    S_dB = librosa.power_to_db(S, ref=np.max)
    
    img = librosa.display.specshow(S_dB, x_axis='time', y_axis='mel', sr=sr, fmax=8000, ax=axes[0])
    axes[0].set_title('Mel Spectrogram')
    fig.colorbar(img, ax=axes[0], format='%+2.0f dB')
    
    # 2. Chromagram
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    img2 = librosa.display.specshow(chroma, x_axis='time', y_axis='chroma', ax=axes[1])
    axes[1].set_title('Chromagram')
    fig.colorbar(img2, ax=axes[1])
    
    # 3. Rhythmic Energy
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    times = librosa.times_like(onset_env, sr=sr)
    axes[2].plot(times, onset_env, label='Onset Strength')
    axes[2].set_title('Rhythmic Energy Envelope')
    axes[2].set_xlabel('Time (s)')
    axes[2].set_ylabel('Energy')
    axes[2].legend()
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Spectrogram saved to: {output_path}")
    
    # Compute BPM
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    tempo_val = float(tempo[0]) if isinstance(tempo, np.ndarray) else float(tempo)
    print(f"Estimated BPM: {tempo_val:.2f}")
    
    # Duration
    duration = librosa.get_duration(y=y, sr=sr)
    print(f"Duration: {duration:.2f} seconds")
    
    return tempo, duration

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python analyze-audio.py <audio_file> <output_image_path>")
        sys.exit(1)
    
    audio_path = sys.argv[1]
    output_path = sys.argv[2]
    
    # Generate spectrogram
    print(f"Generating spectrogram from {audio_path}...")
    tempo, duration = generate_spectrogram(audio_path, output_path)
    
    print("Done!")
