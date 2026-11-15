# Projet Remotion : « Souper de Noël 2026 » (vertical 9:16, 2160×3840)

Montage programmable du film : timelapse, transitions, message, typographie,
sous-titres et carton final. Voir `../README.md` pour la chaîne complète
(préparation des médias, son, encodage, contrôle qualité).

```bash
npm install
npm run dev                       # Remotion Studio (prévisualisation, props éditables)
npx remotion render Film out/master_prores.mov --codec=prores --prores-profile=hq \
  --concurrency=4 --color-space=bt709 --image-format=jpeg --jpeg-quality=98
npx remotion render FilmSansSousTitres out/clean.mov --codec=prores --prores-profile=hq
node scripts/stills.mjs 0.25 459 930 1850   # images clés (planche de contrôle)
```

| Fichier | Rôle |
|---|---|
| `src/Root.tsx` | compositions `Film` et `FilmSansSousTitres`, props par défaut (carton final…) |
| `src/Film.tsx` | empilement des calques (images, finitions, typographie, sous-titres, son) |
| `src/components/Timelapse.tsx` | plans accélérés et transitions (whip, zoom, impact, zoom de raccord) |
| `src/components/MessageTrack.tsx` | message : jump cuts, punch-ins ancrés sur le visage, entrée par le tableau |
| `src/components/Typography.tsx` | chapitres, triptyque, révélation, signature, particules |
| `src/components/Subtitles.tsx` | sous-titres FR incrustés (lecture progressive, mots-clés) |
| `src/components/EndCard.tsx` | carton final (textes modifiables via les props) |
| `src/components/Finish.tsx` | vignettage, grain, flashs, fondus |
| `src/data/timeline.json` | timeline générée par `../pipeline/build_timeline.py` |

Les médias (`public/media`, `public/audio`, `public/grain`) sont générés par le
pipeline et ne sont pas versionnés.
