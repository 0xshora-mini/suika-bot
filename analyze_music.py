#!/usr/bin/env python3
"""
音楽分析スクリプト - PP69のHey phoneを分析
"""
import sys
import librosa
import numpy as np
import subprocess
import os

def download_audio(url, output_path="audio.m4a"):
    """YouTubeから音声をダウンロード"""
    print(f"Downloading audio from {url}...")
    subprocess.run([
        "yt-dlp",
        "-f", "bestaudio",
        "-o", output_path,
        url
    ], check=True)
    return output_path

def analyze_audio(audio_path):
    """音声ファイルを分析"""
    print(f"Loading audio: {audio_path}")
    y, sr = librosa.load(audio_path, sr=None)
    
    print(f"Sample rate: {sr} Hz")
    print(f"Duration: {len(y)/sr:.2f} seconds")
    
    # テンポとビート検出
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    print(f"\nTempo: {tempo:.2f} BPM")
    print(f"Number of beats detected: {len(beats)}")
    
    # ハイハット検出（高周波成分を抽出）
    # ハイハットは通常5kHz以上の高周波帯域に含まれる
    stft = librosa.stft(y)
    freqs = librosa.fft_frequencies(sr=sr)
    
    # 5kHz以上の高周波帯域を抽出
    high_freq_mask = freqs >= 5000
    high_freq_energy = np.abs(stft[high_freq_mask, :])
    avg_high_freq = np.mean(high_freq_energy, axis=0)
    
    # ハイハットっぽい瞬間を検出（高周波エネルギーのピーク）
    threshold = np.percentile(avg_high_freq, 90)
    hihat_moments = avg_high_freq > threshold
    hihat_count = np.sum(hihat_moments)
    
    print(f"\nHigh-frequency (hihat-like) events: {hihat_count}")
    print(f"Hihat events per second: {hihat_count / (len(y)/sr):.2f}")
    
    # スペクトル特性
    spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
    
    print(f"\nSpectral centroid (avg): {np.mean(spectral_centroids):.2f} Hz")
    print(f"Spectral rolloff (avg): {np.mean(spectral_rolloff):.2f} Hz")
    
    # エネルギー分析
    rms = librosa.feature.rms(y=y)[0]
    print(f"\nAverage energy (RMS): {np.mean(rms):.4f}")
    print(f"Max energy: {np.max(rms):.4f}")
    
    # ZCR（ゼロ交差率）- パーカッシブな要素の指標
    zcr = librosa.feature.zero_crossing_rate(y)[0]
    print(f"\nZero crossing rate (avg): {np.mean(zcr):.4f}")
    
    return {
        "tempo": tempo,
        "beats": len(beats),
        "duration": len(y)/sr,
        "hihat_events": hihat_count,
        "spectral_centroid": np.mean(spectral_centroids),
        "energy": np.mean(rms)
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_music.py <youtube_url>")
        sys.exit(1)
    
    url = sys.argv[1]
    audio_file = "temp_audio.m4a"
    
    try:
        # ダウンロード
        download_audio(url, audio_file)
        
        # 分析
        results = analyze_audio(audio_file)
        
        print("\n" + "="*50)
        print("ANALYSIS SUMMARY")
        print("="*50)
        for key, value in results.items():
            print(f"{key}: {value}")
        
    finally:
        # クリーンアップ
        if os.path.exists(audio_file):
            os.remove(audio_file)
            print(f"\nCleaned up: {audio_file}")

if __name__ == "__main__":
    main()
