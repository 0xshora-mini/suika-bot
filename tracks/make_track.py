"""
SUIKA TRACK #001
ジャンル: dark ambient trap fusion
コンセプト: 常識破壊。4/4を拒否した5/4拍子のtrap。不協和音のpad。人の感情を壊す808。
"""

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

SR = 44100
BPM = 140
BEAT = 60 / BPM
STEP = BEAT / 4  # 16th note

def env(t, attack=0.005, decay=0.1, sustain=0.6, release=0.3, dur=1.0):
    out = np.zeros(len(t))
    a = int(attack * SR)
    d = int(decay * SR)
    r = int(release * SR)
    s_end = len(t) - r
    out[:a] = np.linspace(0, 1, a)
    out[a:a+d] = np.linspace(1, sustain, d)
    out[a+d:s_end] = sustain
    out[s_end:] = np.linspace(sustain, 0, r)
    return out

def make_808(freq=55, dur=1.2, vol=0.9):
    t = np.linspace(0, dur, int(SR * dur))
    sweep = freq * np.exp(-3 * t) + freq * 0.3
    phase = 2 * np.pi * np.cumsum(sweep) / SR
    amp = np.exp(-3 * t)
    click = np.exp(-300 * t) * 0.4
    sig = (np.sin(phase) * amp + click) * vol
    # sub harmonics for weight
    sig += np.sin(phase * 0.5) * amp * 0.3 * vol
    return np.clip(sig, -1, 1)

def make_snare(dur=0.35, vol=0.65):
    t = np.linspace(0, dur, int(SR * dur))
    noise = np.random.randn(len(t)) * np.exp(-18 * t)
    tone = np.sin(2 * np.pi * 185 * t) * np.exp(-25 * t)
    tone2 = np.sin(2 * np.pi * 310 * t) * np.exp(-30 * t) * 0.5
    sig = (noise * 0.6 + tone * 0.25 + tone2 * 0.15) * vol
    return np.clip(sig, -1, 1)

def make_hihat(dur=0.04, vol=0.35, open_hat=False):
    dur = 0.18 if open_hat else dur
    t = np.linspace(0, dur, int(SR * dur))
    decay = 40 if not open_hat else 15
    noise = np.random.randn(len(t)) * np.exp(-decay * t)
    # high pass
    sos = butter(4, 8000, btype='high', fs=SR, output='sos')
    noise = sosfilt(sos, noise)
    return np.clip(noise * vol, -1, 1)

def make_pad(freq, dur, vol=0.08, detune=0.003):
    t = np.linspace(0, dur, int(SR * dur))
    # 3 slightly detuned oscillators
    sig = (
        np.sin(2*np.pi*freq*t) +
        np.sin(2*np.pi*freq*(1+detune)*t) * 0.8 +
        np.sin(2*np.pi*freq*(1-detune)*t) * 0.8
    )
    # add 5th harmonic for darkness
    sig += np.sin(2*np.pi*freq*1.5*t) * 0.3
    # slow attack, slow release envelope
    e = np.ones(len(t))
    a = int(0.6*SR); r_len = int(0.8*SR)
    e[:a] = np.linspace(0, 1, a)
    e[-r_len:] = np.linspace(1, 0, r_len)
    sig = sig * e * vol
    # low pass to make it dreamy
    sos = butter(3, 1200, btype='low', fs=SR, output='sos')
    sig = sosfilt(sos, sig)
    return sig

def make_lead(freq, dur, vol=0.12):
    """Glitchy detuned lead"""
    t = np.linspace(0, dur, int(SR * dur))
    # square-ish wave
    sig = np.sign(np.sin(2*np.pi*freq*t)) * 0.5
    sig += np.sin(2*np.pi*freq*t)
    # pitch modulation (vibrato/glitch)
    lfo = np.sin(2*np.pi*5.5*t) * 0.008
    phase = 2*np.pi*np.cumsum(freq*(1+lfo))/SR
    sig2 = np.sin(phase)
    sig = sig * 0.4 + sig2 * 0.6
    e = env(t, attack=0.01, decay=0.05, sustain=0.7, release=0.2, dur=dur)
    sig = sig * e * vol
    sos = butter(2, 3000, btype='low', fs=SR, output='sos')
    return sosfilt(sos, sig)

def mix_into(buf, clip, pos, pan=0.0):
    """Mix a mono clip into stereo buffer at sample position with pan"""
    start = int(pos * SR)
    end = start + len(clip)
    if end > len(buf[0]):
        clip = clip[:len(buf[0])-start]
        end = len(buf[0])
    l = clip * (1 - max(0, pan))
    r = clip * (1 + min(0, pan))
    buf[0][start:end] += l
    buf[1][start:end] += r

# 5/4拍子 = 5 beats per bar (破壊する)
BEATS_PER_BAR = 5
BAR = BEAT * BEATS_PER_BAR
BARS = 16
TOTAL = BAR * BARS
buf = [np.zeros(int(TOTAL * SR)), np.zeros(int(TOTAL * SR))]

# -- CHORD PROGRESSION (暗い、不安定) --
# Am - F#dim - Bm7b5 - E7alt の5/4アレンジ
chord_roots = [
    55.0,   # A2
    46.25,  # F#2
    61.74,  # B2
    41.20,  # E2
]
chord_names = ['Am', 'F#dim', 'Bm7b5', 'E7alt']

# Build pads
pad_dur = BAR * 2
for i, root in enumerate(chord_roots):
    repeat = BARS // (len(chord_roots) * 2)
    for rep in range(4):
        pos = (i * BAR * 2) + (rep * BAR * len(chord_roots) * 2)
        if pos >= TOTAL:
            break
        # Root + flat 5th + minor 7th = darker
        for mult, pan in [(1.0, -0.3), (1.5*0.94, 0.0), (1.78, 0.3), (2.67, -0.1)]:
            pad = make_pad(root * mult, pad_dur, vol=0.07)
            mix_into(buf, pad, pos, pan=pan)

# -- DRUMS (5/4 trap pattern) --
# 5/4: kick on 1, 3 / snare on 2, 4 / floating 5th beat
for bar in range(BARS):
    bar_start = bar * BAR
    # Kick pattern: beat 1, beat 3, and sometimes syncopated
    kick_beats = [0, 2, 3.5] if bar % 2 == 0 else [0, 2.5, 4]
    for kb in kick_beats:
        freq = 65 if bar > 7 else 55
        kick = make_808(freq=freq, dur=0.9, vol=0.85)
        mix_into(buf, kick, bar_start + kb * BEAT, pan=0.0)

    # Snare: beat 2, beat 4
    for sb in [1, 3]:
        sn = make_snare(vol=0.6 + (0.1 if bar > 7 else 0))
        mix_into(buf, sn, bar_start + sb * BEAT, pan=0.05)

    # Hi-hats: 16th grid with gaps (not every 16th)
    hat_pattern = [1,0,1,1, 0,1,1,0, 1,0,1,1, 0,1,0,1, 1,0,1,0]  # 5/4 = 20 16th notes
    for step, active in enumerate(hat_pattern):
        if active:
            swing_offset = 0.012 if step % 2 == 1 else 0
            open_h = (step in [7, 15, 19])
            hat = make_hihat(open_hat=open_h, vol=0.3 + (0.05 if bar > 11 else 0))
            pos = bar_start + step * STEP + swing_offset
            pan = -0.3 + (step % 3) * 0.2
            mix_into(buf, hat, pos, pan=pan)

# -- LEAD MELODY (5/4の流れに逆らうメロ) --
# 不協和だが記憶に残るフレーズ
melody = [
    # (beat_offset_in_bar, freq, dur_beats)
    (0.0,   220.0, 0.5),   # A3
    (0.5,   233.1, 0.75),  # Bb3 (blue note)
    (1.25,  196.0, 0.5),   # G3
    (2.0,   246.9, 1.0),   # B3
    (3.0,   220.0, 0.5),   # A3
    (3.5,   185.0, 1.5),   # F#3
]

for bar in range(4, BARS):  # Enter at bar 5
    bar_start = bar * BAR
    if bar % 4 == 0:  # alternate melody
        mel_use = melody[3:]
    else:
        mel_use = melody[:4]
    for (beat, freq, dur_beats) in mel_use:
        if bar > 11:  # higher octave in second half
            freq *= 2
        lead = make_lead(freq, dur_beats * BEAT, vol=0.10)
        pos = bar_start + beat * BEAT
        mix_into(buf, lead, pos, pan=-0.2)

# -- MASTER --
stereo = np.stack(buf, axis=1)
# Normalize
peak = np.max(np.abs(stereo))
if peak > 0:
    stereo = stereo / peak * 0.88

# Gentle limiter
stereo = np.tanh(stereo * 1.1) / 1.1

# High pass full mix (remove sub rumble below 30Hz)
sos_hp = butter(2, 30, btype='high', fs=SR, output='sos')
stereo[:, 0] = sosfilt(sos_hp, stereo[:, 0])
stereo[:, 1] = sosfilt(sos_hp, stereo[:, 1])

out_path = '/Users/shora-mini/shora-bot/suika-bot/tracks/suika_001.wav'
sf.write(out_path, stereo, SR)
print(f"Done: {out_path} ({TOTAL:.1f}s, {BARS} bars, {BEATS_PER_BAR}/4 拍子)")
