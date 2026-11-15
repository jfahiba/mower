"""Contrôle visuel d'un fichier audio : spectrogramme + RMS 400 ms + repères de la timeline."""
import json, sys
import numpy as np, soundfile as sf, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import spectrogram
src, out = sys.argv[1], sys.argv[2]
extra = sys.argv[3:]  # autres fichiers à superposer (RMS)
tl = json.load(open("/home/user/mower/film/remotion/src/data/timeline.json"))
fps = tl["fps"]
marks = [(tl["impactFrame"]/fps, "impact"), (tl["message"]["audioStart"]/fps, "voix"), (tl["message"]["videoIn"]/fps, "raccord"),
         (tl["moments"][1]["tlFrom"]/fps, "souper"), (tl["moments"][2]["tlFrom"]/fps, "à très vite"), (tl["endCard"]["tlFrom"]/fps, "carton")]
def rms_curve(path):
    m, sr = sf.read(path); x = m.mean(1) if m.ndim > 1 else m
    hop, win = int(0.1*sr), int(0.4*sr)
    r = np.array([20*np.log10(np.sqrt((x[i:i+win]**2).mean())+1e-9) for i in range(0, len(x)-win, hop)])
    return np.arange(len(r))*0.1, r, x, sr
t, r, x, sr = rms_curve(src)
fig, ax = plt.subplots(2, 1, figsize=(16, 7), sharex=True)
f, tt, S = spectrogram(x, sr, nperseg=4096, noverlap=3072)
ax[0].pcolormesh(tt, f, 10*np.log10(S+1e-12), shading='auto', vmin=-120, vmax=-40, cmap='magma')
ax[0].set_yscale('symlog', linthresh=200); ax[0].set_ylim(30, 16000)
ax[1].plot(t, r, label=src.split('/')[-1])
for e in extra:
    te, re_, _, _ = rms_curve(e); ax[1].plot(te, re_, label=e.split('/')[-1], alpha=0.8)
ax[1].legend(loc='lower left'); ax[1].grid(True); ax[1].set_ylim(-70, 0)
for v, l in marks:
    for a in ax: a.axvline(v, color='c', lw=0.8)
    ax[1].text(v, -5, l, rotation=90, fontsize=8)
plt.tight_layout(); plt.savefig(out, dpi=70)
