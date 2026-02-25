import librosa
import librosa.display
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import glob

songs = glob.glob("*.mp3")
songs.sort()

for song in songs:
    print(f"Processing: {song}")
    y, sr = librosa.load(song, sr=None)
    
    # スペクトログラム生成
    D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
    
    plt.figure(figsize=(14, 5))
    librosa.display.specshow(D, sr=sr, x_axis='time', y_axis='hz')
    plt.colorbar(format='%+2.0f dB')
    plt.title(f'Spectrogram - {song}')
    plt.tight_layout()
    plt.savefig(f'{song}_spectrum.png', dpi=150)
    plt.close()
    
    print(f"Saved: {song}_spectrum.png")

print("All done!")
