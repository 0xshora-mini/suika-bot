#!/usr/bin/env python3
"""
スペクトログラム分析スクリプト
5曲のmp3ファイルを読み込み、スペクトログラム画像を生成する
"""

import os
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np

# 曲リスト
songs = [
    ("01_sheena_ringo_marunouchi.mp3", "椎名林檎 - 丸ノ内サディスティック"),
    ("02_bucktick_iconoclasm.mp3", "BUCK-TICK - ICONOCLASM"),
    ("03_lamp_koibito.mp3", "Lamp - 恋人へ"),
    ("04_downy_mudai.mp3", "downy - 無題"),
    ("05_sakanaction_shintakarajima.mp3", "サカナクション - 新宝島"),
]

for filename, title in songs:
    if not os.path.exists(filename):
        print(f"⚠️  {filename} が見つからない")
        continue
    
    print(f"🎵 分析中: {title}")
    
    # 音源読み込み (sr=Noneでオリジナルのサンプリングレートを維持)
    y, sr = librosa.load(filename, sr=None)
    
    # 曲の長さ
    duration = librosa.get_duration(y=y, sr=sr)
    
    # BPM推定
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    tempo_val = float(tempo) if isinstance(tempo, np.ndarray) else tempo
    
    print(f"  ⏱️  長さ: {duration:.2f}秒 ({duration/60:.2f}分)")
    print(f"  🥁 BPM: {tempo_val:.2f}")
    
    # スペクトログラム計算
    # STFT (Short-Time Fourier Transform)
    D = librosa.stft(y)
    
    # 振幅をdBに変換
    S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
    
    # 図を作成
    plt.figure(figsize=(14, 6))
    
    # スペクトログラム表示
    img = librosa.display.specshow(
        S_db,
        sr=sr,
        x_axis='time',
        y_axis='hz',
        cmap='viridis',
        vmin=-80,
        vmax=0
    )
    
    plt.colorbar(img, format='%+2.0f dB')
    plt.title(f'{title}\nBPM: {tempo_val:.1f} | Duration: {duration:.1f}s', fontsize=14)
    plt.xlabel('Time (s)', fontsize=12)
    plt.ylabel('Frequency (Hz)', fontsize=12)
    plt.ylim(0, 16000)  # 0-16kHzまで表示
    plt.tight_layout()
    
    # 画像保存
    output_filename = filename.replace('.mp3', '_spectrogram.png')
    plt.savefig(output_filename, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"  ✅ 保存: {output_filename}\n")

print("🎉 全曲分析完了！")
