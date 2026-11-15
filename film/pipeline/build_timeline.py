"""Construit la timeline dérivée de l'EDL (pipeline/edl.py).

Sorties :
  remotion/src/data/timeline.json  (lu par la composition Remotion et le pipeline audio)
  deliverables/FINAL_SUBTITLES.srt (sous-titres FR synchronisés sur le film monté)

Les mots (faster-whisper large-v3) sont recalés sur les silences mesurés à
l'énergie (début de mot = fin du silence qui le précède, etc.), puis projetés
sur la timeline à travers les segments du message (jump cuts).
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
import edl  # noqa: E402

FPS = edl.FPS
NBSP = " "  # espace fine insécable (typographie française avant ! ? ; :)


# ---------------------------------------------------------------------------
# Timelapse
# ---------------------------------------------------------------------------
def build_timelapse():
    shots = []
    f = 0
    for s in edl.TIMELAPSE:
        dur = s["frames"]
        keys = s["remap"]
        assert abs(keys[-1][0] * FPS - dur) < 0.51, (s["id"], keys[-1][0] * FPS, dur)
        src_span = keys[-1][1] - keys[0][1]
        shots.append(
            dict(
                id=s["id"],
                src=s["src"],
                file=f"media/{s['id']}.mp4",
                from_=f,
                durationInFrames=dur,
                transIn=s.get("trans_in", "cut"),
                avgSpeed=round(src_span / (dur / FPS), 2),
                note=s.get("note", ""),
            )
        )
        f += dur
    return shots, f


# ---------------------------------------------------------------------------
# Message : segments source -> timeline
# ---------------------------------------------------------------------------
def build_message(video_in_tl):
    a_in, v_in, out = edl.MESSAGE_AUDIO_IN_F, edl.MESSAGE_VIDEO_IN_F, edl.MESSAGE_OUT_F
    cuts = sorted(edl.CUTS_F)
    kept = []
    cur = a_in
    for c0, c1 in cuts:
        kept.append((cur, c0))
        cur = c1
    kept.append((cur, out))
    # le son démarre en J-cut : la source v_in tombe sur video_in_tl
    assert kept[0][0] <= v_in < kept[0][1]
    tl = video_in_tl - (v_in - a_in)
    segs = []
    for s0, s1 in kept:
        segs.append(dict(srcFrom=s0, srcTo=s1, tlFrom=tl, tlTo=tl + (s1 - s0)))
        tl += s1 - s0
    return segs, tl


def src_to_tl(t_src, segs, snap=0.0):
    """Temps source (s) -> image timeline (float). None si dans une coupe
    (sauf si à moins de `snap` secondes d'une borne de segment : accroché)."""
    fs = t_src * FPS
    for s in segs:
        if s["srcFrom"] <= fs < s["srcTo"] + 1e-6:
            return s["tlFrom"] + (fs - s["srcFrom"])
    if snap > 0:
        best = None
        for s in segs:
            for edge, tl in ((s["srcFrom"], s["tlFrom"]), (s["srcTo"], s["tlTo"])):
                d = abs(fs - edge) / FPS
                if d <= snap and (best is None or d < best[0]):
                    best = (d, tl)
        if best:
            return best[1]
    return None


# ---------------------------------------------------------------------------
# Mots : recalage sur les silences, nettoyage typographique
# ---------------------------------------------------------------------------
def load_words():
    d = json.loads((ROOT / "analysis/transcripts/WA0048_16k.json").read_text())
    sil = json.loads((ROOT / "analysis/WA0048_silences.json").read_text())["silences"]
    words = []
    for seg in d["segments"]:
        for w in seg["words"]:
            words.append(dict(text=w["word"].strip(), start=w["start"], end=w["end"]))
    # fusionne les élisions découpées par Whisper (« L » + « 'année », « t » + « 'invite »)
    merged = []
    for w in words:
        if merged and w["text"].startswith("'"):
            merged[-1]["text"] += w["text"]
            merged[-1]["end"] = w["end"]
        elif merged and w["text"].startswith("-"):
            merged[-1]["text"] += w["text"]
            merged[-1]["end"] = w["end"]
        else:
            merged.append(dict(w))
    # recalage : si un silence (≥120 ms) chevauche le début d'un mot, le mot
    # commence à la fin du silence ; s'il chevauche la fin, il finit au début.
    for w in merged:
        for s0, s1, _ in sil:
            if s1 - s0 < 0.12:
                continue
            if s0 - 0.05 <= w["start"] < s1 and s1 < w["end"]:
                w["start"] = s1
            if s0 < w["end"] <= s1 and s0 > w["start"]:
                w["end"] = s0
    for w in merged:
        t = w["text"].replace("'", "’")
        t = re.sub(r"\s*([!?;:])$", NBSP + r"\1", t)
        w["text"] = t
    return merged


# Découpage éditorial des sous-titres (phrases naturelles, ≤ ~42 caractères/ligne)
CUE_BREAKS = [
    "Femme entrepreneur,",
    "femme battante,",
    "femme de foi.",
    "L’année 2026, ça a été quelque chose.",
    "Tu as porté ta famille,",
    "tu as porté ton entreprise,",
    "tu as porté ta foi.",
    "Mais cette fois-ci, c’est à ton tour",
    "de te laisser porter.",
    "Lors de notre souper annuel 2026,",
    "le souper de Noël.",
    "Donc, je t’invite à venir célébrer,",
    "à venir rendre grâce",
    "avec des femmes qui entreprennent,",
    "mais surtout des femmes qui comprennent.",
    "Lors d’une soirée chaleureuse,",
    "lors d’une soirée pleine de témoignages,",
    "pleine d’émotions.",
    "Ne viens pas seule,",
    "viens accompagnée d’une sœur, d’une amie.",
    "Les places partent rapidement,",
    "donc n’hésite pas à t’inscrire aussi rapidement.",
    "À très vite" + NBSP + "!",
]


def norm(s):
    return re.sub(r"[^\w]", "", s.lower().replace("’", "").replace("'", ""))


def build_cues(words, segs):
    cues = []
    wi = 0
    for text in CUE_BREAKS:
        target = norm(text)
        acc = ""
        cue_words = []
        while wi < len(words) and len(acc) < len(target):
            w = words[wi]
            acc += norm(w["text"])
            cue_words.append(w)
            wi += 1
        if acc != target:
            raise SystemExit(f"Désalignement sous-titres : {text!r} vs {acc!r}")
        # texte affiché = texte éditorial (orthographe/ponctuation corrigées)
        disp_tokens = text.split(" ")
        # associe chaque mot éditorial à un mot Whisper (même ordre ; élisions fusionnées)
        mapped = []
        j = 0
        for tok in disp_tokens:
            tn = norm(tok)
            buf = ""
            start = None
            end = None
            while j < len(cue_words) and len(buf) < len(tn):
                cw = cue_words[j]
                buf += norm(cw["text"])
                start = cw["start"] if start is None else start
                end = cw["end"]
                j += 1
            if tn == "":  # ponctuation isolée
                mapped.append(dict(text=tok, start=mapped[-1]["end"], end=mapped[-1]["end"]))
                continue
            mapped.append(dict(text=tok, start=start, end=end))
        tl_words = []
        for m in mapped:
            a = src_to_tl(m["start"], segs, snap=0.25)
            b = src_to_tl(m["end"], segs, snap=0.25)
            tl_words.append(dict(text=m["text"], start=round(a, 2), end=round(b, 2)))
        cues.append(dict(text=text, words=tl_words, start=tl_words[0]["start"], end=tl_words[-1]["end"]))
    # tenue d'affichage : on prolonge chaque sous-titre jusqu'au suivant si l'écart < 0,6 s
    for i, c in enumerate(cues):
        c["displayStart"] = round(c["start"] - 2, 2)  # 2 images d'anticipation (lecture)
    for i, c in enumerate(cues):
        nxt = cues[i + 1]["displayStart"] if i + 1 < len(cues) else c["end"] + 0.8 * FPS
        want = max(c["end"] + 6, min(c["end"] + 0.6 * FPS, nxt))
        c["displayEnd"] = round(min(want, nxt - 1), 2)  # jamais de chevauchement
    return cues


def emphasis_ranges(text):
    """Indices de mots (dans text.split(' ')) à accentuer."""
    toks = text.split(" ")
    flags = [False] * len(toks)
    ntoks = [norm(t) for t in toks]
    for e in edl.EMPHASIS:
        etoks = [norm(t) for t in e.replace("'", "’").split(" ")]
        L = len(etoks)
        for i in range(len(toks) - L + 1):
            if ntoks[i : i + L] == etoks:
                for k in range(i, i + L):
                    flags[k] = True
    return flags


FUNCTION_WORDS = ("à", "de", "d’une", "des", "la", "le", "les", "ça", "a", "pas", "ta", "ton", "une", "qui", "c’est", "je")


def burn_line_break(text, max_one_line=24):
    """Index du premier mot de la 2e ligne pour l'incrustation (-1 = une seule ligne).
    Coupure préférée après une virgule ; jamais de mot-outil en fin de ligne ;
    lignes équilibrées."""
    if len(text) <= max_one_line:
        return -1
    toks = text.split(" ")
    best = None
    for i in range(1, len(toks)):
        a = " ".join(toks[:i])
        b = " ".join(toks[i:])
        score = abs(len(a) - len(b))
        if a.endswith(","):
            score -= 14
        if toks[i - 1].lower() in FUNCTION_WORDS:
            score += 12
        if max(len(a), len(b)) > 30:
            score += 40
        if best is None or score < best[0]:
            best = (score, i)
    return best[1]


def srt_time(frames):
    t = max(0.0, frames / FPS)
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = int(t % 60)
    ms = int(round((t - int(t)) * 1000))
    if ms == 1000:
        s += 1
        ms = 0
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def wrap2(text, maxc=34):
    """Deux lignes équilibrées pour le SRT si nécessaire."""
    if len(text) <= maxc:
        return text
    toks = text.split(" ")
    best = None
    for i in range(1, len(toks)):
        a = " ".join(toks[:i])
        b = " ".join(toks[i:])
        score = abs(len(a) - len(b))
        if a.endswith(","):
            score -= 14  # coupure naturelle après la ponctuation
        if a.split(" ")[-1] in ("à", "de", "d’une", "des", "la", "le", "ça", "a", "pas"):
            score += 10  # ne pas laisser un mot-outil en fin de ligne
        if best is None or score < best[0]:
            best = (score, a, b)
    return best[1] + "\n" + best[2]


def main():
    shots, tl_end_timelapse = build_timelapse()
    video_in_tl = tl_end_timelapse  # le message apparaît juste après A1
    segs, msg_end = build_message(video_in_tl)
    words = load_words()
    cues = build_cues(words, segs)
    for c in cues:
        c["emphasis"] = emphasis_ranges(c["text"])
        c["lineBreak"] = burn_line_break(c["text"])

    # cadrages : temps source -> image timeline
    framing = []
    for fr in edl.FRAMING:
        tl = src_to_tl(fr["t"], segs, snap=0.3)
        assert tl is not None, fr
        framing.append(dict(tlFrom=int(round(tl)), scale=fr["scale"], push=fr["push"], srcT=fr["t"], note=fr["note"]))

    # moments typographiques
    moments = []
    for m in edl.TITLE_MOMENTS:
        mm = dict(m)
        mm["tlFrom"] = int(round(src_to_tl(m["t_src_start"], segs, snap=0.3)))
        end_tl = src_to_tl(min(m["t_src_end"], edl.MESSAGE_OUT_F / FPS - 1e-3), segs, snap=0.3)
        mm["tlTo"] = int(round(end_tl))
        if m["kind"] == "triad":
            mm["lines"] = [
                dict(a=a, b=b, tl=int(round(src_to_tl(t, segs, snap=0.3)))) for (a, b, t) in m["lines"]
            ]
        moments.append(mm)

    end_card_from = msg_end - 18  # fondu de 18 images sur le sourire final
    duration = msg_end + int(round(edl.END_CARD["duration"] * FPS)) - 18

    chapters = [
        dict(kicker=c["kicker"], title=c["title"], tlFrom=int(round(c["start"] * FPS)), tlTo=int(round(c["end"] * FPS)))
        for c in edl.CHAPTERS
    ]

    # visage (ancrage des punch-ins) : échantillons t_src -> timeline
    faces = json.loads((ROOT / "analysis/WA0048_faces.json").read_text())
    face_track = []
    for fc in faces:
        tl = src_to_tl(fc["t"], segs)
        if tl is not None:
            face_track.append(dict(tl=round(tl, 1), cx=round(fc["cx"], 3), cy=round(fc["cy"], 3)))

    # repères audio dérivés
    sfx = []
    for s in shots:
        if s["transIn"] in ("whip",):
            sfx.append(dict(type="whoosh", tl=s["from_"]))
        elif s["transIn"] == "zoom":
            sfx.append(dict(type="swish", tl=s["from_"]))
        elif s["transIn"] == "impact":
            sfx.append(dict(type="impact", tl=s["from_"]))
    sfx.append(dict(type="riser", tl=shots[-1]["from_"] - int(edl.RISER_BARS * 2 * FPS), toTl=shots[-1]["from_"]))
    sfx.append(dict(type="shimmer", tl=moments[1]["tlFrom"]))  # révélation « souper de Noël »
    sfx.append(dict(type="matchWhoosh", tl=video_in_tl))

    timeline = dict(
        fps=FPS,
        width=edl.WIDTH,
        height=edl.HEIGHT,
        bpm=edl.BPM,
        durationInFrames=duration,
        timelapse=shots,
        timelapseEnd=tl_end_timelapse,
        impactFrame=shots[-1]["from_"],
        message=dict(
            file="media/message.mp4",
            videoIn=video_in_tl,
            audioStart=segs[0]["tlFrom"],
            segments=segs,
            end=msg_end,
        ),
        framing=framing,
        faceTrack=face_track,
        paintingAnchorA1=edl.PAINTING_ANCHOR_A1,
        paintingAnchorMsg=edl.PAINTING_ANCHOR_MSG,
        chapters=chapters,
        moments=moments,
        cues=cues,
        endCard=dict(edl.END_CARD, tlFrom=end_card_from, tlTo=duration),
        sfx=sfx,
    )
    out = ROOT / "remotion/src/data/timeline.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(timeline, ensure_ascii=False, indent=1))

    # SRT
    lines = []
    for i, c in enumerate(cues, 1):
        lines.append(str(i))
        lines.append(f"{srt_time(c['displayStart'])} --> {srt_time(c['displayEnd'])}")
        lines.append(wrap2(c["text"]))
        lines.append("")
    srt = ROOT / "deliverables/FINAL_SUBTITLES.srt"
    srt.parent.mkdir(parents=True, exist_ok=True)
    srt.write_text("\n".join(lines), encoding="utf-8")

    print(f"timelapse: {tl_end_timelapse} images ({tl_end_timelapse / FPS:.2f} s)")
    for s in shots:
        print(f"  {s['id']:3s} {s['src']} [{s['from_']:4d}+{s['durationInFrames']:3d}] in={s['transIn']:7s} ~{s['avgSpeed']}x  {s['note']}")
    print(f"message: son dès {segs[0]['tlFrom']} ({segs[0]['tlFrom'] / FPS:.2f} s), image dès {video_in_tl} ({video_in_tl / FPS:.2f} s), fin {msg_end} ({msg_end / FPS:.2f} s)")
    for s in segs:
        print(f"  src [{s['srcFrom']:5d},{s['srcTo']:5d}) -> tl [{s['tlFrom']:5d},{s['tlTo']:5d})")
    print(f"durée totale: {duration} images = {duration / FPS:.2f} s ; part du timelapse accéléré = {shots[-1]['from_'] / duration:.0%} (+ ralenti)")
    print(f"sous-titres: {len(cues)} ; moments: {[(m['kind'], m['tlFrom'], m['tlTo']) for m in moments]}")
    print(f"sfx: {sfx}")


if __name__ == "__main__":
    main()
