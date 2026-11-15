# Souper de Noël 2026 : film vertical 9:16 (4K)

Montage complet d'un film vertical de 62,6 s à partir de 6 vidéos WhatsApp :
un timelapse d'ouverture (les courses, puis le bureau), une transition ralentie
jusqu'à 1x, puis le message face caméra (WA0048) à vitesse normale, sous-titré,
et un carton final.

## Livrables (`deliverables/`)

| Fichier | Contenu |
|---|---|
| `FINAL_MASTER_4K.mp4` | Version principale : HEVC Main10, 2160×3840, 30 i/s, Rec.709, AAC 320 kb/s 48 kHz, sous-titres incrustés |
| `FINAL_WEB.mp4` | Version partage : H.264 High, 1080×1920, AAC 192 kb/s 48 kHz, sous-titres incrustés |
| `FINAL_SUBTITLES.srt` | Sous-titres français synchronisés sur le film monté (UTF-8) |
| `PLANCHE_CONTACT.jpg` | Planche de contact des séquences retenues (plans, vitesses, timecodes) |
| `RAPPORT_TECHNIQUE.md` | Rapport de production et de validation du rendu |
| `qc_report.json` | Mesures brutes du contrôle qualité |

## Organisation

```
film/
├── sources/            liens en lecture seule vers les vidéos originales (non versionnés)
├── pipeline/           scripts de production (Python/FFmpeg)
│   ├── edl.py              ← décisions de montage (plans, vitesses, coupes, cadrages, textes)
│   ├── build_timeline.py   EDL -> remotion/src/data/timeline.json + SRT
│   ├── stabilize.sh        stabilisation vidstab 2 passes
│   ├── remap.py            speed ramps PCHIP + frame-blending (obturateur 180°)
│   ├── grading.py, make_lut.py   balance par source + LUT « film look » (grade/film_look.cube)
│   ├── grade_upscale.py    étalonnage + agrandissement 4K (spline36 + CAS)
│   ├── audio_voice.py      chaîne voix + montage synchronisé
│   ├── compose_music.py    partition originale (MIDI + FluidSynth + synthèse)
│   ├── mix_master.py       ducking, -14 LUFS, true-peak -1 dBTP
│   ├── encode_deliverables.sh, qc.py, contact_sheet.py
│   └── run_all.sh          chaîne complète
├── remotion/           projet Remotion 4.0.543 (montage, transitions, typographie, sous-titres)
│   ├── src/Film.tsx, src/Root.tsx, src/components/*.tsx
│   └── public/ (media/, audio/, fonts/, grain/)
├── grade/film_look.cube
└── analysis/           transcriptions, mesures, planches de contact des sources
```

## Prévisualiser et modifier dans Remotion Studio

```bash
cd remotion
npm install
npm run dev          # ouvre Remotion Studio
```

Deux compositions : **Film** (avec sous-titres) et **FilmSansSousTitres**.
Ce qui se règle dans le panneau des props du Studio, sans toucher au code :
- `endCard.details` : ajoute la date, le lieu ou le lien d'inscription au carton final (vide = masqué) ;
- `endCard.title`, `kicker`, `tagline`, `cta` : textes du carton ;
- `burnSubtitles`, `grain`, `vignette` ;
- `audio` : `mix` (mixage masterisé) ou `stems` (voix, musique, effets, ambiance séparés).

Pour changer le montage lui-même (plans, vitesses, coupes, cadrages, mots-clés) :
modifier `pipeline/edl.py`, puis relancer `build_timeline.py` (et `remap.py` /
`grade_upscale.py` si les plans du timelapse changent, `audio_voice.py` +
`compose_music.py` + `mix_master.py` si la durée change).

## Re-rendre

```bash
cd remotion
npx remotion render Film out/master_prores.mov --codec=prores --prores-profile=hq \
  --concurrency=4 --color-space=bt709 --image-format=jpeg --jpeg-quality=98
cd .. && pipeline/encode_deliverables.sh && .venv/bin/python pipeline/qc.py
```

## Licences et droits

- Musique : composition originale créée pour ce film (aucune œuvre tierce). Les
  instruments viennent de la banque MuseScore General (licence MIT ; certaines
  parties sont dans le domaine public ou sous CC0). Percussions et effets sont synthétisés.
- Polices : Inter et Instrument Serif (SIL Open Font License 1.1), voir `remotion/public/fonts/`.
- Remotion : gratuit pour les particuliers et les entreprises de 3 personnes au plus ;
  au-delà, une licence entreprise est requise (https://www.remotion.dev/docs/license).
