#!/usr/bin/env python3
"""
音楽スペクトログラム分析スクリプト
Usage: python3 scripts/analyze_music.py <youtube_url> <output_prefix>
"""
import sys
import os
import subprocess
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np

def download_audio(url, output_path="temp_audio.m4a"):
    """YouTube URLから音声をダウンロード"""
    print(f"Downloading audio from {url}...")
    subprocess.run([
        "yt-dlp",
        "-x",  # 音声のみ
        "--audio-format", "m4a",
        "-o", output_path,
        url
    ], check=True)
    return output_path

def generate_spectrogram(audio_path, output_image="spectrogram.png"):
    """スペクトログラムを生成"""
    print(f"Loading audio from {audio_path}...")
    y, sr = librosa.load(audio_path, sr=None)
    
    print(f"Generating spectrogram...")
    # メルスペクトログラム
    S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)
    S_dB = librosa.power_to_db(S, ref=np.max)
    
    # 可視化
    plt.figure(figsize=(14, 6))
    librosa.display.specshow(S_dB, sr=sr, x_axis='time', y_axis='mel', fmax=8000)
    plt.colorbar(format='%+2.0f dB')
    plt.title('Mel Spectrogram')
    plt.tight_layout()
    plt.savefig(output_image, dpi=150)
    plt.close()
    
    print(f"Spectrogram saved to {output_image}")
    return output_image

def analyze_audio(audio_path):
    """音声の基本情報を分析"""
    print(f"Analyzing audio...")
    y, sr = librosa.load(audio_path, sr=None)
    
    # テンポ検出
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    # tempoが配列の場合は最初の要素を取得
    if isinstance(tempo, np.ndarray):
        tempo = float(tempo[0]) if len(tempo) > 0 else 0.0
    else:
        tempo = float(tempo)
    
    # 長さ
    duration = librosa.get_duration(y=y, sr=sr)
    
    # RMS energy
    rms = librosa.feature.rms(y=y)[0]
    
    print(f"Sample rate: {sr} Hz")
    print(f"Duration: {duration:.2f} seconds")
    print(f"Estimated tempo: {tempo:.2f} BPM")
    print(f"RMS energy (mean): {np.mean(rms):.4f}")
    
    return {
        "sr": sr,
        "duration": duration,
        "tempo": tempo,
        "rms_mean": np.mean(rms)
    }

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 scripts/analyze_music.py <youtube_url> <output_prefix>")
        sys.exit(1)
    
    url = sys.argv[1]
    output_prefix = sys.argv[2]
    
    # ダウンロード
    audio_path = f"{output_prefix}_audio.m4a"
    download_audio(url, audio_path)
    
    # 分析
    stats = analyze_audio(audio_path)
    
    # スペクトログラム生成
    spectrogram_path = f"{output_prefix}_spectrogram.png"
    generate_spectrogram(audio_path, spectrogram_path)
    
    # 統計情報を保存
    stats_path = f"{output_prefix}_stats.txt"
    with open(stats_path, 'w') as f:
        f.write(f"Duration: {stats['duration']:.2f} seconds\n")
        f.write(f"Sample rate: {stats['sr']} Hz\n")
        f.write(f"Estimated tempo: {stats['tempo']:.2f} BPM\n")
        f.write(f"RMS energy (mean): {stats['rms_mean']:.4f}\n")
    
    print(f"\nAnalysis complete!")
    print(f"  Audio: {audio_path}")
    print(f"  Spectrogram: {spectrogram_path}")
    print(f"  Stats: {stats_path}")

if __name__ == "__main__":
    main()
