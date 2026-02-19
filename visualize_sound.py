#!/usr/bin/env python3
"""
音をスペクトログラムとして視覚化
"""
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np

print('音声ファイルを読み込み中...')
y, sr = librosa.load('temp_audio.m4a', sr=None)
print(f'サンプルレート: {sr} Hz')
print(f'長さ: {len(y)/sr:.2f}秒')

# 複数の可視化を作成
fig, axes = plt.subplots(3, 1, figsize=(15, 12))

# 1. メル・スペクトログラム（全体的な周波数分布）
S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)
S_dB = librosa.power_to_db(S, ref=np.max)

img1 = librosa.display.specshow(S_dB, x_axis='time', y_axis='mel', sr=sr, fmax=8000, ax=axes[0])
axes[0].set_title('Mel Spectrogram (Overall Sound)', fontsize=14)
axes[0].set_ylabel('Frequency (Hz)')
fig.colorbar(img1, ax=axes[0], format='%+2.0f dB')

# 2. 高周波数帯域（ハイハット領域）
high_freq_start = 5000
high_freq_end = 16000

stft = librosa.stft(y)
freqs = librosa.fft_frequencies(sr=sr)
high_freq_mask = (freqs >= high_freq_start) & (freqs <= high_freq_end)
high_freq_stft = stft[high_freq_mask, :]

img2 = librosa.display.specshow(librosa.amplitude_to_db(np.abs(high_freq_stft), ref=np.max),
                                 x_axis='time', y_axis='linear', sr=sr, ax=axes[1])
axes[1].set_title(f'High Frequency Band ({high_freq_start}-{high_freq_end}Hz) - Hi-hat Region', fontsize=14)
axes[1].set_ylabel('Frequency (Hz)')
fig.colorbar(img2, ax=axes[1], format='%+2.0f dB')

# 3. エネルギーエンベロープ（リズムパターン）
onset_env = librosa.onset.onset_strength(y=y, sr=sr)
times = librosa.times_like(onset_env, sr=sr)

axes[2].plot(times, onset_env, label='Onset Strength')
axes[2].set_title('Rhythmic Energy Envelope', fontsize=14)
axes[2].set_xlabel('Time (s)')
axes[2].set_ylabel('Energy')
axes[2].legend()
axes[2].grid(True)

plt.tight_layout()
plt.savefig('sound_visualization.png', dpi=150, bbox_inches='tight')
print('\n保存完了: sound_visualization.png')
