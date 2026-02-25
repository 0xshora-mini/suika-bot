#!/usr/bin/env python3
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import os
import sys

def analyze_track(file_path, output_dir="spectrograms"):
    """音楽ファイルを分析してスペクトログラムを生成"""
    os.makedirs(output_dir, exist_ok=True)
    
    # ファイル名取得
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    
    # 音声読み込み
    print(f"Loading: {file_path}")
    y, sr = librosa.load(file_path, sr=None)
    duration = librosa.get_duration(y=y, sr=sr)
    
    # BPM検出
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    # tempoが配列の場合は最初の値を取得
    if isinstance(tempo, np.ndarray):
        tempo = float(tempo[0]) if len(tempo) > 0 else 0.0
    else:
        tempo = float(tempo)
    
    # スペクトログラム生成
    D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
    
    # プロット
    plt.figure(figsize=(14, 8))
    librosa.display.specshow(D, sr=sr, x_axis='time', y_axis='hz')
    plt.colorbar(format='%+2.0f dB')
    plt.title(f'{base_name} - Spectrogram')
    plt.tight_layout()
    
    # 保存
    output_path = os.path.join(output_dir, f"{base_name}_spectrogram.png")
    plt.savefig(output_path, dpi=100)
    plt.close()
    
    print(f"  Duration: {duration:.2f}s")
    print(f"  BPM: {tempo:.2f}")
    print(f"  Spectrogram saved: {output_path}\n")
    
    return {
        "file": base_name,
        "duration": duration,
        "bpm": tempo,
        "spectrogram": output_path
    }

if __name__ == "__main__":
    # music-tempディレクトリ内の全m4aファイルを分析
    music_dir = "/Users/shora-mini/shora-bot/suika-bot/music-temp"
    results = []
    
    for file in os.listdir(music_dir):
        if file.endswith(".m4a"):
            file_path = os.path.join(music_dir, file)
            try:
                result = analyze_track(file_path)
                results.append(result)
            except Exception as e:
                print(f"Error processing {file}: {e}")
    
    print("\n=== Analysis Complete ===")
    for r in results:
        print(f"{r['file']}: {r['duration']:.2f}s, {r['bpm']:.2f} BPM")
