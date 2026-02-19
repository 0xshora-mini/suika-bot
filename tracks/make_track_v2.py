"""
SUIKA TRACK #002 - 進化版
コンセプト: 5/4拍子は残す。でも人間が聞いて気持ちいい音に。
変えること:
- 和音に解決感を入れる（Am → G → F → E7 の流れ）
- メロディをもっと歌わせる（音符を少なく、間を大事に）
- パッドの音量バランス整える
- 808をもっと太く、ミックスをクリーンに
"""

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

SR = 44100
BPM = 128  # 少し落ち着いたテンポ
BEAT = 60 / BPM
STEP = BEAT / 4
BEATS_PER_BAR = 5
BAR = BEAT * BEATS_PER_BAR
BARS = 16
TOTAL = BAR * BARS

buf = [np.zeros(int(TOTAL * SR + SR)), np.zeros(int(TOTAL * SR + SR))]

def hp(sig, cutoff):
    sos = butter(2, cutoff, btype='high', fs=SR, output='sos')
    return sosfilt(sos, sig)

def lp(sig, cutoff):
    sos = butter(2, cutoff, btype='low', fs=SR, output='sos')
    return sosfilt(sos, sig)

def mix_into(buf, clip, pos, pan=0.0, vol=1.0):
    start = int(pos * SR)
    end = start + len(clip)
    if start >= len(buf[0]): return
    if end > len(buf[0]):
        clip = clip[:len(buf[0])-start]
        end = len(buf[0])
    l = clip * vol * (1 - max(0, pan))
    r = clip * vol * (1 + min(0, pan))
    buf[0][start:end] += l
    buf[1][start:end] += r

# ── INSTRUMENTS ──────────────────────────────────────────

def make_808(freq=55, dur=1.0, vol=0.9):
    t = np.linspace(0, dur, int(SR * dur))
    # pitch sweep: start high, settle
    sweep = freq * (1 + 1.8 * np.exp(-12 * t))
    phase = 2 * np.pi * np.cumsum(sweep) / SR
    amp = np.exp(-2.5 * t)
    click = np.exp(-250 * t) * 0.35
    sub = np.sin(phase * 0.5) * amp * 0.35
    sig = (np.sin(phase) * amp + sub + click) * vol
    return np.clip(sig, -1, 1)

def make_snare(vol=0.65, bright=False):
    dur = 0.3
    t = np.linspace(0, dur, int(SR * dur))
    noise = np.random.randn(len(t)) * np.exp(-20 * t)
    tone = np.sin(2 * np.pi * 200 * t) * np.exp(-28 * t)
    sig = noise * 0.65 + tone * 0.35
    if bright:
        sig = hp(sig, 3000)
    else:
        sig = hp(sig, 200)
    return np.clip(sig * vol, -1, 1)

def make_hihat(open_hat=False, vol=0.3):
    dur = 0.18 if open_hat else 0.04
    t = np.linspace(0, dur, int(SR * dur))
    decay = 12 if open_hat else 90
    noise = np.random.randn(len(t)) * np.exp(-decay * t)
    noise = hp(noise, 9000)
    return np.clip(noise * vol, -1, 1)

def make_pad(freq, dur, vol=0.1, warmth=True):
    t = np.linspace(0, dur, int(SR * dur))
    # Warm detuned pads
    sig = (
        np.sin(2*np.pi*freq*t) +
        np.sin(2*np.pi*freq*1.003*t) * 0.85 +
        np.sin(2*np.pi*freq*0.997*t) * 0.85 +
        np.sin(2*np.pi*freq*2.0*t) * 0.2 +   # octave
        np.sin(2*np.pi*freq*1.5*t) * 0.15     # fifth
    )
    # slow attack
    a = int(min(0.5*SR, len(t)//3))
    r_len = int(min(0.6*SR, len(t)//3))
    env = np.ones(len(t))
    env[:a] = np.linspace(0, 1, a)
    env[-r_len:] = np.linspace(1, 0, r_len)
    sig = sig * env * vol
    sig = lp(sig, 900 if warmth else 1400)
    return sig

def make_melody_note(freq, dur, vol=0.13, vibrato=True):
    n = int(SR * dur)
    t = np.linspace(0, dur, n)
    # vibrato kicks in after 0.1s
    vib = np.zeros(n)
    onset = int(0.12 * SR)
    if vibrato and n > onset:
        vib[onset:] = np.sin(2*np.pi*5.2*t[onset:]) * 0.012
    phase = 2*np.pi*np.cumsum(freq * (1 + vib)) / SR
    sig = np.sin(phase) * 0.8 + np.sin(phase*2) * 0.15 + np.sin(phase*3) * 0.05
    # envelope: pluck-like
    env = np.exp(-2.5 * t) + np.exp(-0.8 * t) * 0.5
    env /= env.max()
    # attack
    a = int(0.008 * SR)
    env[:a] = np.linspace(0, env[a], a)
    sig = sig * env * vol
    sig = lp(sig, 2500)
    sig = hp(sig, 150)
    return sig

def make_bass_note(freq, dur, vol=0.45):
    """Sub-bass melody note under chords"""
    n = int(SR * dur)
    t = np.linspace(0, dur, n)
    sig = np.sin(2*np.pi*freq*t)
    sig += np.sin(2*np.pi*freq*2*t) * 0.3
    env = np.exp(-1.5 * t) * 0.6 + np.exp(-0.3 * t) * 0.4
    env /= env.max()
    a = int(0.01 * SR)
    env[:a] = np.linspace(0, env[a], a)
    sig = sig * env * vol
    sig = lp(sig, 300)
    return sig

# ── CHORD PROGRESSION (5小節ループ) ───────────────────────
# Am - F - C - G - E7  → 解決感があって暗い（美しい）
# 各コードを1拍ずつ、5拍で1バー

# Root freqs (Hz)
# Am: A2=110, C3=130.8, E3=164.8
# F:  F2=87.3, A2=110, C3=130.8
# C:  C2=65.4, E2=82.4, G2=98
# G:  G2=98,  B2=123.5, D3=146.8
# E7: E2=82.4, G#2=103.8, B2=123.5, D3=146.8

chord_schedule = [
    # (bar_offset, beat_offset, root_hz, chord_freqs, bass_hz)
    # bar 0-1: Am
    (0, 0, 55.0, [110.0, 130.8, 164.8], 55.0),
    # bar 2-3: F
    (2, 0, 43.65, [87.3, 110.0, 130.8], 43.65),
    # bar 4-5: C
    (4, 0, 32.7, [65.4, 82.4, 98.0], 32.7),
    # bar 6-7: G
    (6, 0, 49.0, [98.0, 123.5, 146.8], 49.0),
    # bar 8-9: E7
    (8, 0, 41.2, [82.4, 103.8, 123.5, 146.8], 41.2),
    # repeat
    (10, 0, 55.0, [110.0, 130.8, 164.8], 55.0),
    (12, 0, 43.65, [87.3, 110.0, 130.8], 43.65),
    (14, 0, 32.7, [65.4, 82.4, 98.0], 32.7),
]

chord_dur = BAR * 2

for (bar, beat, root, freqs, bass) in chord_schedule:
    pos = bar * BAR + beat * BEAT
    if pos >= TOTAL: continue
    # Pads (soft, layered)
    for i, f in enumerate(freqs):
        pan = [-0.4, 0.0, 0.4, 0.1][i % 4]
        pad = make_pad(f, chord_dur, vol=0.09)
        mix_into(buf, pad, pos, pan=pan)
    # Bass pad (very sub)
    bass_sig = make_pad(bass, chord_dur, vol=0.12, warmth=True)
    bass_sig = lp(bass_sig, 200)
    mix_into(buf, bass_sig, pos, pan=0.0)

# ── DRUMS ────────────────────────────────────────────────
for bar in range(BARS):
    t0 = bar * BAR

    # Kick: beat 1, beat 3 (5/4 の核)
    k_beats = [0, 2] if bar % 4 != 3 else [0, 2, 4]
    for kb in k_beats:
        freq = 58 + (bar // 4) * 4
        kick = make_808(freq=freq, dur=0.9, vol=0.82)
        mix_into(buf, kick, t0 + kb*BEAT)

    # 808 sub stab on beat 4 (3/4 through bar — 5/4の浮遊感)
    if bar > 3:
        stab = make_808(freq=41.2, dur=0.4, vol=0.55)
        mix_into(buf, stab, t0 + 3.5*BEAT)

    # Snare: beat 2, beat 4
    for sb in [1, 3]:
        sn = make_snare(vol=0.6, bright=(bar > 11))
        mix_into(buf, sn, t0 + sb*BEAT, pan=0.04)

    # Hi-hats: 20 steps (5*4), with groove
    hat_grid = [1,0,1,1, 0,1,1,0, 1,0,1,1, 0,1,0,1, 1,0,1,0]
    for step, on in enumerate(hat_grid):
        if not on: continue
        swing = 0.014 if step % 2 else 0
        open_h = step in [7, 14, 19]
        vol = 0.25 + (0.05 if bar > 7 else 0)
        hat = make_hihat(open_hat=open_h, vol=vol)
        pan = -0.3 + (step % 5) * 0.15
        mix_into(buf, hat, t0 + step*STEP + swing, pan=pan)

# ── MELODY (A minor pentatonic, 人が歌えるライン) ──────────
# A3=220, C4=261.6, D4=293.7, E4=329.6, G4=392
# フレーズ: 少ない音で、間を大事に

melody_phrase_A = [
    # (beat_in_bar, freq, dur_beats)
    (0.0,   329.6, 1.5),   # E4
    (1.5,   293.7, 1.0),   # D4
    (2.5,   261.6, 0.75),  # C4
    (3.25,  220.0, 1.75),  # A3 (hold to end of bar)
]

melody_phrase_B = [
    (0.0,   392.0, 1.0),   # G4
    (1.0,   329.6, 0.5),   # E4
    (1.5,   293.7, 1.5),   # D4
    (3.0,   261.6, 2.0),   # C4
]

melody_phrase_C = [  # 解決フレーズ
    (0.0,   329.6, 0.5),
    (0.5,   349.2, 0.5),   # F4
    (1.0,   329.6, 0.5),
    (1.5,   220.0, 3.5),   # A3 long
]

phrases = [
    (4,  melody_phrase_A),
    (6,  melody_phrase_B),
    (8,  melody_phrase_A),
    (10, melody_phrase_C),
    (12, melody_phrase_A),
    (14, melody_phrase_B),
]

for (start_bar, phrase) in phrases:
    t0 = start_bar * BAR
    for (beat, freq, dur_beats) in phrase:
        n = make_melody_note(freq, dur_beats * BEAT, vol=0.12)
        mix_into(buf, n, t0 + beat*BEAT, pan=-0.15)

# Harmony (3rd above melody, soft)
harmony_phrases = [
    (8,  [(0.0, 392.0, 1.5), (1.5, 349.2, 1.0), (2.5, 329.6, 2.5)]),
    (12, [(0.0, 392.0, 1.5), (1.5, 349.2, 1.0), (2.5, 329.6, 2.5)]),
]
for (start_bar, phrase) in harmony_phrases:
    t0 = start_bar * BAR
    for (beat, freq, dur_beats) in phrase:
        n = make_melody_note(freq, dur_beats * BEAT, vol=0.06, vibrato=False)
        mix_into(buf, n, t0 + beat*BEAT, pan=0.2)

# ── MASTER MIX ───────────────────────────────────────────
stereo = np.stack(buf, axis=1)
stereo = stereo[:int(TOTAL * SR)]

# High pass full mix
stereo[:, 0] = hp(stereo[:, 0], 28)
stereo[:, 1] = hp(stereo[:, 1], 28)

# Normalize
peak = np.max(np.abs(stereo))
if peak > 0:
    stereo = stereo / peak * 0.86

# Soft limiter
stereo = np.tanh(stereo * 1.15) / 1.15

out_path = '/Users/shora-mini/shora-bot/suika-bot/tracks/suika_002.wav'
sf.write(out_path, stereo, SR)
dur_s = TOTAL
print(f"Done: {out_path} ({dur_s:.1f}s, {BARS} bars @ {BPM}bpm, {BEATS_PER_BAR}/4)")
