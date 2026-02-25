#!/usr/bin/env python3
import librosa
import numpy as np
import sys

if len(sys.argv) < 2:
    print("Usage: analyze_music.py <audio_file>")
    sys.exit(1)

audio_file = sys.argv[1]

print(f"Loading {audio_file}...")
y, sr = librosa.load(audio_file, sr=22050, mono=True)

print("\n=== SPECTRAL ANALYSIS ===\n")

# Chroma (harmonic content)
print("Analyzing harmonic content (chroma)...")
chroma = librosa.feature.chroma_cqt(y=y, sr=sr, bins_per_octave=36)
dominant_notes = []
note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
for i in range(min(10, chroma.shape[1])):  # First 10 frames
    dominant = np.argmax(chroma[:, i])
    dominant_notes.append(note_names[dominant])
print(f"Dominant notes in first 10 frames: {', '.join(dominant_notes)}")

# Tempo
print("\nAnalyzing tempo...")
tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
tempo_val = float(tempo) if isinstance(tempo, np.ndarray) else tempo
print(f"Estimated tempo: {tempo_val:.1f} BPM")
print(f"Number of beats detected: {len(beats)}")

# Loudness per 5-second segment
print("\nAnalyzing loudness per 5-second segment...")
segment_duration = 5  # seconds
rms = []
for i in range(0, len(y) - int(segment_duration * sr), int(segment_duration * sr)):
    segment = y[i:i + int(segment_duration * sr)]
    rms_val = np.sqrt(np.mean(segment**2))
    rms.append(rms_val)
    timestamp = i / sr
    print(f"  {timestamp:.1f}s - {timestamp + segment_duration:.1f}s: RMS = {rms_val:.4f}")

# Overall dynamics
print(f"\nOverall loudness range: {min(rms):.4f} - {max(rms):.4f}")
print(f"Average loudness: {np.mean(rms):.4f}")

# Energy arc (normalized RMS)
if len(rms) > 0:
    normalized_rms = [(r - min(rms)) / (max(rms) - min(rms)) if max(rms) > min(rms) else 0 for r in rms]
    print(f"\nEnergy arc (normalized): {', '.join([f'{r:.2f}' for r in normalized_rms])}")

print("\n=== ANALYSIS COMPLETE ===\n")
