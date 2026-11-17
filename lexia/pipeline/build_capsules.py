"""Construit la timeline de chaque capsule -> remotion/src/data/capsules.json + SRT.

- extraits calés sur les mots (marge 0,12 s avant, 0,28 s après), alignés sur des
  images entières (synchro son/image exacte) ;
- pauses > 0,6 s ramenées à 0,4 s (coupes dans les silences mesurés) ;
- sous-titres = paroles de Me Arbi ; les questions hors champ sont des cartons ;
- photos : placées au premier silence entre deux sous-titres après la position voulue.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
from capsules import CAPSULES, CONTACT, FIXES, OUTRO_PHOTO  # noqa: E402

FPS = 30
OUTRO = 150  # 5 s
PHOTO_DUR = 42
NBSP = " "
SIL = json.loads((ROOT / "analysis/silences.json").read_text())


def words_of(src):
    d = json.loads((ROOT / f"analysis/transcripts/{src}_16k.json").read_text())
    ws = []
    for s in d["segments"]:
        for w in s["words"]:
            t = w["word"].strip()
            if not t:
                continue
            if ws and (t.startswith("'") or t.startswith("-") or re.fullmatch(r"[?!.,;:]+", t)):
                ws[-1]["text"] += t
                ws[-1]["end"] = w["end"]
                continue
            ws.append(dict(text=t, start=w["start"], end=w["end"]))
    for w in ws:
        t = FIXES.get(w["text"], w["text"]).replace("'", "’")
        t = re.sub(r"\s*([!?;:])$", NBSP + r"\1", t)
        w["text"] = t
    return ws


def norm(s):
    return re.sub(r"[^\w]", "", s.lower().replace("’", "").replace("'", ""))


def line_break(text, one=24):
    if len(text) <= one:
        return -1
    toks = text.split(" ")
    best = None
    for i in range(1, len(toks)):
        a, b = " ".join(toks[:i]), " ".join(toks[i:])
        sc = abs(len(a) - len(b)) - (14 if a.endswith(",") else 0)
        if toks[i - 1].lower() in ("à", "de", "d’un", "d’une", "des", "la", "le", "les", "un", "une", "qui", "on", "au", "en", "et", "du"):
            sc += 12
        if max(len(a), len(b)) > 30:
            sc += 40
        if best is None or sc < best[0]:
            best = (sc, i)
    return best[1]


def srt_t(f):
    t = f / FPS
    return f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d},{int(round((t % 1) * 1000)) % 1000:03d}"


def build(cap):
    segs = []  # src, srcFrom, srcTo (images)
    for src, t0, t1 in cap["parts"]:
        ws = [w for w in words_of(src) if t0 - 0.05 <= w["start"] < t1]
        a = max(t0, ws[0]["start"] - 0.12) if ws else t0
        b = min(t1 + 0.3, ws[-1]["end"] + 0.28) if ws else t1
        fa, fb = int(round(a * FPS)), int(round(b * FPS))
        # pauses longues dans l'extrait
        cur = fa
        for s0, s1 in SIL[src]["silences"]:
            if s1 - s0 >= 0.6 and fa < s0 * FPS and s1 * FPS < fb:
                c0, c1 = int(round((s0 + 0.2) * FPS)), int(round((s1 - 0.2) * FPS))
                segs.append([src, cur, c0])
                cur = c1
        segs.append([src, cur, fb])
    tl = 0
    out = []
    for src, s0, s1 in segs:
        out.append(dict(src=src, srcFrom=s0, srcTo=s1, tlFrom=tl, tlTo=tl + (s1 - s0)))
        tl += s1 - s0
    body = tl
    faces = json.loads((ROOT / "analysis/faces.json").read_text())
    for s in out:
        pts = [p for p in faces[s["src"]] if s["srcFrom"] / FPS - 1 <= p["t"] <= s["srcTo"] / FPS + 1] or faces[s["src"]]
        s["cx"] = round(sum(p["cx"] for p in pts) / len(pts), 3)
        s["cy"] = round(sum(p["cy"] for p in pts) / len(pts), 3)

    def to_tl(src, t):
        f = t * FPS
        for s in out:
            if s["src"] == src and s["srcFrom"] - 3 <= f <= s["srcTo"] + 3:
                return s["tlFrom"] + min(max(f, s["srcFrom"]), s["srcTo"]) - s["srcFrom"]
        return None

    # questions hors champ
    qs = []
    for src, a, b, text in cap.get("questions", []):
        ta, tb = to_tl(src, max(a, out[0]["srcFrom"] / FPS if out[0]["src"] == src else a)), to_tl(src, b)
        if ta is None:
            ta = 0
        if tb is None:
            tb = ta + 60
        qs.append(dict(tlFrom=int(ta), tlTo=int(tb), text=text))

    # mots de Me Arbi -> sous-titres
    words = []
    for src, t0, t1 in cap["parts"]:
        for w in words_of(src):
            if not (t0 - 0.05 <= w["start"] < t1):
                continue
            if any(q[0] == src and q[1] - 0.05 <= w["start"] < q[2] for q in cap.get("questions", [])):
                continue
            a, b = to_tl(src, w["start"]), to_tl(src, w["end"])
            if a is None:
                continue
            for osrc, ot, otext in cap.get("overrides", []):
                if osrc == src and abs(ot - w["start"]) < 0.05:
                    w = dict(w, text=otext)
            words.append(dict(text=w["text"], start=round(a, 2), end=round(b if b else a + 6, 2)))
    # nom du cabinet
    for i in range(len(words) - 1):
        if words[i]["text"] == "Lexia":
            words[i + 1]["text"] = words[i + 1]["text"].replace("notaire", "Notaires")
            if i + 3 < len(words) and words[i + 3]["text"] == "services":
                words[i + 3]["text"] = "Services"
    # 1) propositions (phrases / virgules) ; 2) regroupement <= 46 car. ; 3) coupe équilibrée
    FW = ("à", "de", "d’un", "d’une", "des", "la", "le", "les", "un", "une", "qui", "on", "au", "en", "et", "du", "ou", "pour", "que", "dans")
    clauses, cur = [], []
    for w in words:
        cur.append(w)
        if w["text"].rstrip("»\u202f ")[-1:] in ".?!…,":
            clauses.append(cur)
            cur = []
    if cur:
        clauses.append(cur)
    L = lambda ws: len(" ".join(x["text"] for x in ws))
    pieces = []
    for c in clauses:
        while L(c) > 46:
            best = None
            for k in range(2, len(c) - 1):
                a, bb = c[:k], c[k:]
                if L(a) > 46:
                    break
                sc = abs(L(a) - min(L(bb), 46)) + (20 if c[k - 1]["text"].lower() in FW else 0)
                if best is None or sc < best[0]:
                    best = (sc, k)
            k = best[1] if best else len(c) // 2
            pieces.append(c[:k])
            c = c[k:]
        pieces.append(c)
    cues = []
    for pc in pieces:
        prev_end_sent = cues and cues[-1][-1]["text"].rstrip("»\u202f ")[-1:] in ".?!…"
        if cues and not prev_end_sent and L(cues[-1] + pc) <= 46:
            cues[-1] += pc
        else:
            cues.append(pc)
    # amorces courtes (« Donc, », « Également, ») rattachées à la proposition suivante
    fixed = []
    i = 0
    while i < len(cues):
        c = cues[i]
        end_sent = c[-1]["text"].rstrip("»\u202f ")[-1:] in ".?!…"
        if L(c) < 14 and not end_sent and i + 1 < len(cues) and L(c + cues[i + 1]) <= 52:
            cues[i + 1] = c + cues[i + 1]
        else:
            fixed.append(c)
        i += 1
    cues = fixed
    # fusion des sous-titres trop courts
    merged = []
    for c in cues:
        if merged and len(" ".join(x["text"] for x in c)) < 10 and len(" ".join(x["text"] for x in merged[-1] + c)) <= 44:
            merged[-1] += c
        else:
            merged.append(c)
    emph = [[norm(t) for t in e.replace("'", "’").split(" ")] for e in cap["emphasis"]]
    cue_objs = []
    for c in merged:
        text = " ".join(x["text"] for x in c)
        toks = [norm(x["text"]) for x in c]
        flags = [False] * len(c)
        for e in emph:
            for i in range(len(c) - len(e) + 1):
                if toks[i:i + len(e)] == e:
                    for k in range(i, i + len(e)):
                        flags[k] = True
        if text and text[0].islower():
            c[0]["text"] = c[0]["text"][0].upper() + c[0]["text"][1:] if False else c[0]["text"]
        cue_objs.append(dict(text=text, words=c, start=c[0]["start"], end=c[-1]["end"], emphasis=flags,
                             lineBreak=line_break(text)))
    for i, c in enumerate(cue_objs):
        c["displayStart"] = round(c["start"] - 2, 2)
    for i, c in enumerate(cue_objs):
        nxt = cue_objs[i + 1]["displayStart"] if i + 1 < len(cue_objs) else body
        c["displayEnd"] = round(min(max(c["end"] + 6, min(c["end"] + 18, nxt)), nxt - 1), 2)

    # photos : premier « trou » entre sous-titres après la position voulue
    photos = []
    gaps = [(cue_objs[i]["end"], cue_objs[i + 1]["start"]) for i in range(len(cue_objs) - 1)]
    for name, pos in cap["photos"]:
        target = pos * body
        cands = [g for g in gaps if g[0] >= target - 15] or gaps
        g = cands[0] if cands else (target, target)
        start = int(max(20, min(body - PHOTO_DUR - 10, g[0] + 2)))
        if any(abs(start - p["tlFrom"]) < PHOTO_DUR + 20 for p in photos):
            start = int(min(body - PHOTO_DUR - 10, start + PHOTO_DUR + 30))
        photos.append(dict(file=f"photos/{name}", tlFrom=start, dur=PHOTO_DUR))

    # cadrages : alternance large / serré à chaque coupe et toutes les ~2 phrases
    framing = [dict(tlFrom=0, scale=1.0, push=0.035)]
    big = False
    for i, s in enumerate(out[1:], 1):
        big = not big
        framing.append(dict(tlFrom=s["tlFrom"], scale=1.13 if big else 1.0, push=0.025))
    for i, c in enumerate(cue_objs):
        if i % 3 == 2 and all(abs(c["displayStart"] - f["tlFrom"]) > 75 for f in framing):
            # dans le silence juste avant la phrase
            big = not big
            framing.append(dict(tlFrom=int(c["start"] - 4), scale=1.13 if big else 1.0, push=0.025))
    framing.sort(key=lambda f: f["tlFrom"])
    return dict(id=cap["id"], title=cap["title"], short=cap["short"], segments=out, bodyEnd=body,
                durationInFrames=body + OUTRO - 12, questions=qs, cues=cue_objs, photos=photos, framing=framing)


GAP = 18  # images de respiration entre deux chapitres (transition + carton)


def build_full(caps):
    """Montage unique : les capsules officielles bout à bout (sans le bêtisier C10),
    un carton de chapitre et une transition dynamique à chaque nouveau sujet,
    un seul carton final."""
    full = dict(id="FULL", title="Me Rania Arbi répond à vos questions", short="Le montage complet",
                segments=[], questions=[], cues=[], photos=[], framing=[], chapters=[])
    off = 0
    for n, c in enumerate(caps, 1):
        sh = lambda f: round(f + off, 2)
        full["chapters"].append(dict(n=n, tlFrom=off, title=c["title"]))
        for s in c["segments"]:
            full["segments"].append(dict(s, tlFrom=s["tlFrom"] + off, tlTo=s["tlTo"] + off))
        for q in c["questions"]:
            full["questions"].append(dict(q, tlFrom=q["tlFrom"] + off, tlTo=q["tlTo"] + off))
        for cue in c["cues"]:
            full["cues"].append(dict(cue, start=sh(cue["start"]), end=sh(cue["end"]), displayStart=sh(cue["displayStart"]),
                                     displayEnd=sh(cue["displayEnd"]),
                                     words=[dict(w, start=sh(w["start"]), end=sh(w["end"])) for w in cue["words"]]))
        for ph in c["photos"]:
            full["photos"].append(dict(ph, tlFrom=ph["tlFrom"] + off))
        for fr in c["framing"]:
            full["framing"].append(dict(fr, tlFrom=fr["tlFrom"] + off))
        off += c["bodyEnd"]
    full["bodyEnd"] = off
    full["durationInFrames"] = off + OUTRO - 12
    return full


def main():
    caps = [build(c) for c in CAPSULES]
    full = build_full([c for c in caps if c["id"] != "C10"])
    data = dict(fps=FPS, width=2160, height=3840, contact=CONTACT, outroPhoto=f"photos/{OUTRO_PHOTO}",
                capsules=caps + [full])
    out = ROOT / "remotion/src/data/capsules.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=1))
    (ROOT / "deliverables").mkdir(exist_ok=True)
    for c in data["capsules"]:
        lines = []
        k = 1
        for q in c["questions"]:
            lines += [str(k), f"{srt_t(q['tlFrom'])} --> {srt_t(q['tlTo'])}", "[Question] " + q["text"], ""]
            k += 1
        for cue in c["cues"]:
            t = cue["text"]
            br = cue["lineBreak"]
            if br > 0:
                toks = t.split(" ")
                t = " ".join(toks[:br]) + "\n" + " ".join(toks[br:])
            lines += [str(k), f"{srt_t(cue['displayStart'])} --> {srt_t(cue['displayEnd'])}", t, ""]
            k += 1
        (ROOT / f"deliverables/{c['id']}_SOUS-TITRES.srt").write_text("\n".join(lines), encoding="utf-8")
        print(f"{c['id']} {c['durationInFrames'] / FPS:5.1f} s | {len(c['segments'])} seg | {len(c['cues'])} sous-titres | photos {[p['tlFrom'] for p in c['photos']]} | {c['title']}")
        print("     " + " / ".join(x["text"] for x in c["cues"])[:400])


if __name__ == "__main__":
    main()
