"""Transcription mot à mot (faster-whisper) d'un ou plusieurs fichiers audio.

Usage: python transcribe.py <model> <out_dir> <wav> [<wav> ...]
Écrit <out_dir>/<nom>.json avec segments + mots (start/end/prob).
Le prompt initial encourage une transcription verbatim (hésitations conservées)
afin de pouvoir les repérer au montage.
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import soundfile as sf
from faster_whisper import WhisperModel

model_name, out_dir, *wavs = sys.argv[1:]
out = Path(out_dir)
out.mkdir(parents=True, exist_ok=True)

t0 = time.time()
model = WhisperModel(model_name, device="cpu", compute_type="int8", cpu_threads=4)
print(f"model loaded in {time.time() - t0:.1f}s", flush=True)

PROMPT = (
    "Euh... alors, bon, voilà. Hum, donc, en fait, je voulais, je voulais vous dire... "
    "Transcription fidèle, avec les hésitations et les répétitions."
)

for wav in wavs:
    t1 = time.time()
    audio, sr = sf.read(wav, dtype="float32")
    assert sr == 16000, sr
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    segments, info = model.transcribe(
        audio,
        language=None,
        task="transcribe",
        beam_size=5,
        best_of=5,
        temperature=0.0,
        word_timestamps=True,
        vad_filter=False,
        condition_on_previous_text=True,
        initial_prompt=PROMPT,
    )
    segs = []
    for s in segments:
        segs.append(
            {
                "start": s.start,
                "end": s.end,
                "text": s.text,
                "avg_logprob": s.avg_logprob,
                "no_speech_prob": s.no_speech_prob,
                "words": [
                    {"start": w.start, "end": w.end, "word": w.word, "prob": w.probability}
                    for w in (s.words or [])
                ],
            }
        )
    res = {
        "file": wav,
        "model": model_name,
        "language": info.language,
        "language_probability": info.language_probability,
        "duration": info.duration,
        "segments": segs,
    }
    name = Path(wav).stem
    (out / f"{name}.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))
    print(f"== {name}: lang={info.language} ({info.language_probability:.2f}) in {time.time() - t1:.1f}s", flush=True)
    for s in segs:
        print(f"[{s['start']:6.2f}-{s['end']:6.2f}] (nsp={s['no_speech_prob']:.2f}) {s['text']}", flush=True)
