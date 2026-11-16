# Rapport technique : film « Souper de Noël 2026 »

*Film vertical 9:16, 2160×3840, 30 i/s, 1878 images (62.60 s). Montage Remotion 4.0.543, traitements FFmpeg 6.1.1, transcription faster-whisper large-v3.*

## 1. Résumé

| Livrable | Format | Taille | Débit |
|---|---|---|---|
| `FINAL_MASTER_4K.mp4` | HEVC Main 10 2160×3840 yuv420p10le, AAC 311 kb/s 48 kHz | 459.1 Mo | 58.67 Mb/s |
| `FINAL_WEB.mp4` | H264 High 1080×1920, AAC 197 kb/s 48 kHz | 77.9 Mo | 9.96 Mb/s |
| `FINAL_SUBTITLES.srt` | SRT UTF-8, 23 sous-titres | | |
| `PLANCHE_CONTACT.jpg` | planche des séquences retenues | | |
| `../remotion/` | projet Remotion complet, modifiable | | |

**Contrôle qualité : tous les contrôles sont conformes.** Loudness du master : -14.0 LUFS intégrés, true-peak -1.0 dBTP.

## 2. Analyse des sources

| Fichier | Durée | Image (affichage) | i/s | Loudness | Netteté méd. | Tremblement | Contenu | Rôle |
|---|---|---|---|---|---|---|---|---|
| WA0042 | 8.13 s | 720×1280 | 30 | -26.0 LUFS | 1343.8 | 0.38 | Courses : allée, elle pousse le chariot vers la caméra | Timelapse S1 |
| WA0044 | 10.10 s | 720×1280 (rot. −90°) | 30 | -29.3 LUFS | 901.1 | 0.69 | Courses : allée, orbite au rayon, décor de Noël | Timelapse S2 |
| WA0045 | 13.40 s | 720×1280 (rot. −90°) | 30 | -26.3 LUFS | 700.9 | 0.85 | Courses : elle se retourne et avance en dansant, sourire | Timelapse S3 |
| WA0047 | 20.70 s | 720×1280 | 30 | -27.8 LUFS | 1135.2 | 0.35 | Courses : choisit des produits, panoramique sur les rayons | Timelapse S4 |
| WA0048 | 47.80 s | 720×1280 | 30 | -19.0 LUFS | 458.7 | 0.17 | **Message face caméra** (parole FR), bureau aux coquelicots, drapeau du Québec | Message (1x) |
| WA0049 | 56.86 s | 720×1280 | 30 | -30.1 LUFS | 298.5 | 0.81 | Bureau : statue de la Justice, dossiers, téléphone, couloirs ; se termine assise au bureau aux coquelicots | Timelapse O1–O6 + A1 (ralenti) |

Toutes les sources sont des vidéos WhatsApp : H.264 Baseline, environ 2 Mb/s, AAC environ 60 kb/s, verticales. Les métadonnées de date ont été supprimées par WhatsApp, l'ordre retenu est donc celui de la numérotation.

**Identification du message.** Contrairement à l'hypothèse de départ, **la dernière vidéo par numérotation (WA0049) ne contient pas le message** : on y entend seulement des bribes d'ambiance (« Où est-ce qu'on va ? »). Le message principal est **WA0048** (langue détectée : français, probabilité 1.00). WA0049 a donc été placé **à la fin du timelapse** : il illustre « ton entreprise », et son dernier plan se déroule dans le décor même du message (le tableau de coquelicots), ce qui donne le raccord de la transition signature. C'est la seule entorse à l'ordre de numérotation, motivée par la narration.

**Transcription du message (WA0048), texte intégral :**

> Femme entrepreneur, femme battante, femme de foi. L'année 2026, ça a été quelque chose. Tu as porté ta famille, tu as porté ton entreprise, tu as porté ta foi. Mais cette fois-ci, c'est à ton tour de te laisser porter. Lors de notre souper annuel 2026, le souper de Noël. Donc, je t'invite à venir célébrer, à venir rendre grâce avec des femmes qui entreprennent, mais surtout des femmes qui comprennent. Lors d'une soirée chaleureuse, lors d'une soirée pleine de témoignages, pleine d'émotions. Ne viens pas seule, viens accompagnée d'une sœur, d'une amie. Les places partent rapidement, donc n'hésite pas à t'inscrire aussi rapidement. À très vite!

## 3. Structure narrative et timeline

1. **Timelapse** 0:00 → 0:12.00 (12.0 s, soit 19% du film) : « ta famille » (courses), puis « ton entreprise » (bureau). Le rythme des coupes s'accélère : une coupe par mesure, puis à chaque temps.
2. **Transition signature** 0:12.00 → 0:15.30 : impact musical sur l'entrée dans le bureau aux coquelicots, ralenti progressif de 10x à 1x, ambiance réelle du bureau, voix en J-cut (« Femme entrepreneur, »), puis raccord par zoom flouté sur le tableau présent dans les deux plans.
3. **Message** à vitesse 1x : 0:15.30 → 0:59.60.
4. **Carton final** : 0:59.00 → 1:02.60.

| Plan | Source | Extrait source | Durée | Vitesse moy. | Transition d'entrée | Description |
|---|---|---|---|---|---|---|
| S1 | WA0042 | 0.10 → 8.05 s | 2.00 s | ×3.98 | open | allée, elle pousse le chariot vers la caméra (≈4x) |
| S2 | WA0044 | 0.00 → 10.05 s | 2.00 s | ×5.03 | cut | allée puis orbite autour d'elle au rayon (4.5–5.5x) |
| S3 | WA0045 | 0.00 → 13.30 s | 2.00 s | ×6.65 | whip | dos, demi-tour, elle avance en dansant, sourire (9x → 5.6x) |
| S4 | WA0047 | 3.70 → 20.60 s | 2.00 s | ×8.45 | zoom | arrive au chariot, choisit, repart ; panoramique final (8.5x) |
| O1 | WA0049 | 0.05 → 1.20 s | 0.50 s | ×2.3 | whip | statue de la Justice (insert) |
| O2 | WA0049 | 2.70 → 9.30 s | 1.00 s | ×6.6 | cut | au bureau, se lève, sort avec les dossiers (6.6x) |
| O3 | WA0049 | 9.30 → 16.60 s | 0.50 s | ×14.6 | cut | couloir (14.6x) |
| O4 | WA0049 | 16.60 → 28.60 s | 1.00 s | ×12.0 | cut | accueil, bureau, téléphone (12x) |
| O5 | WA0049 | 28.60 → 36.20 s | 0.50 s | ×15.2 | cut | déplacements à l'accueil (15.2x) |
| O6 | WA0049 | 41.00 → 48.60 s | 0.50 s | ×15.2 | cut | marche avec les dossiers (15.2x) |
| A1 | WA0049 | 49.40 → 56.83 s | 3.30 s | ×2.25 | impact | entre dans le bureau aux coquelicots, pose les dossiers, s'assoit ; 10x → 1x |

La musique est à 120 BPM : 1 mesure = 2 s = 60 images, 1 temps = 15 images. Toutes les coupes du timelapse tombent sur un temps, et l'impact tombe sur le premier temps de la mesure 7, sur la tonique.

### Montage du message (WA0048, vitesse 1x, jamais accéléré)

| Segment | Source | Timeline |
|---|---|---|
| 1 | 0.233 → 4.200 s | 0:13.67 → 0:17.63 |
| 2 | 4.400 → 7.367 s | 0:17.63 → 0:20.60 |
| 3 | 7.800 → 34.167 s | 0:20.60 → 0:46.97 |
| 4 | 34.400 → 38.867 s | 0:46.97 → 0:51.43 |
| 5 | 39.133 → 47.300 s | 0:51.43 → 0:59.60 |

Coupes (jump cuts) : 4 pauses trop longues ramenées à environ 0,40 s, soit 34 images (1.13 s) retirées. Chaque coupe tombe dans un silence mesuré à l'énergie (plancher de −65 dB), avec au moins 0,17 s de marge avant l'attaque et après la fin du mot. Coupes et segments sont alignés sur des frontières d'images exactes, d'où une synchronisation son/image strictement conservée.
Pauses expressives **conservées** : le rythme du triptyque « Femme entrepreneur, / femme battante, / femme de foi » (environ 0,5 s chacune), « 2026, » (0,5 s), « accompagnée, » (0,47 s), et la respiration avant « À très vite ! ». Les répétitions (« tu as porté… », « lors d'une soirée… », « rapidement… rapidement ») sont des anaphores voulues par l'oratrice : elles sont gardées.

Cadrages : punch-ins façon « deux caméras », placés dans les silences et ancrés sur la position du visage (détection YuNet sur 239/239 échantillons). Le recentrage horizontal est borné pour qu'aucun bord ne soit jamais découvert, et chaque plan comporte un push-in lent de 2 à 3,5 %.

| Timeline | Échelle | Intention |
|---|---|---|
| 0:15.27 | ×1.00 (+3.5 %) | ouverture large, léger push-in |
| 0:17.63 | ×1.10 (+2.0 %) | « L'année 2026 » (jump cut) |
| 0:20.60 | ×1.00 (+3.0 %) | « Tu as porté… » (jump cut) |
| 0:24.63 | ×1.16 (+2.0 %) | « Mais cette fois-ci » — bascule émotionnelle |
| 0:28.13 | ×1.00 (+3.0 %) | « Lors de notre souper annuel… » |
| 0:32.97 | ×1.10 (+2.0 %) | « Donc, je t'invite… » |
| 0:41.27 | ×1.00 (+3.0 %) | « Lors d'une soirée chaleureuse… » |
| 0:46.97 | ×1.12 (+2.0 %) | « Ne viens pas seule » (jump cut) |
| 0:51.43 | ×1.00 (+3.0 %) | « Les places partent… » (jump cut) |
| 0:57.30 | ×1.14 (+3.0 %) | « À très vite ! » — signature intime |

## 4. Traitements image

**Stabilisation** (libvidstab, 2 passes, détection shakiness 8 / accuracy 15) : mode *strong* (lissage ±40 images, zoom dynamique) pour WA0042 et WA0045 ; mode *gentle* (lissage ±12, zoom fixe 5 %, correction plafonnée, bords comblés par l'image précédente) pour les plans à mouvements de caméra volontaires (orbite, panoramiques, marche). Un premier essai en zoom dynamique sur tous les clips cadrait trop serré : il a été rejeté après contrôle visuel.

| Clip | Tremblement avant | après |
|---|---|---|
| WA0042 | 0.38 | 0.31 |
| WA0044 | 0.69 | 0.88 |
| WA0045 | 0.85 | 0.31 |
| WA0047 | 0.35 | 0.24 |
| WA0049 | 0.81 | 0.67 |

*(Tremblement : énergie haute fréquence de la translation globale, mesurée par corrélation de phase. Sur WA0044, l'orbite volontaire biaise la mesure.)*

**Accélérations** : courbes de vitesse interpolées en PCHIP (monotones, dérivée continue) pour des speed ramps fluides. Chaque image de sortie intègre en lumière linéaire toutes les images source couvertes par un obturateur virtuel de 180°, ce qui donne un flou de bouger proportionnel à la vitesse. Sous 2,5x, l'image la plus proche est utilisée, pour éviter les fantômes.

**Étalonnage** : balance des blancs par source, mesurée sur des surfaces neutres (sol, murs), vers un blanc chaud commun (R/G 1,05 ; B/G 0,935). WA0048 est aligné sur le mur du même bureau vu dans WA0049 (R/G 1,07), ce qui rend le raccord invisible.
Le LUT 3D `grade/film_look.cube` (33³, calculé en Oklab) applique une courbe filmique douce (noirs mats, épaule progressive), atténue les cyans, verts et bleus saturés (emballages), préserve les rouges, ors et tons chair, et ajoute un split-toning discret limité aux zones peu saturées pour protéger la peau.

| Source | Gains R / G / B |
|---|---|
| WA0042 | 0.999 / 0.999 / 1.015 |
| WA0044 | 1.030 / 1.033 / 0.998 |
| WA0045 | 1.021 / 1.020 / 1.011 |
| WA0047 | 0.994 / 0.987 / 1.010 |
| WA0048 | 0.970 / 1.008 / 1.008 |
| WA0049 | 1.024 / 1.019 / 1.015 |

**Agrandissement 4K, transparence :** les sources font **720×1280** (environ 2 Mb/s). L'agrandissement x3 vers 2160×3840 (zscale spline36, débruitage léger hqdn3d, netteté adaptative CAS 0,50 à 0,55, grain fin) est de haute qualité, mais **il ne crée pas de vrais détails 4K**. L'image reste fidèle à la définition d'origine. Aucun upscaler par IA n'a été utilisé : environnement CPU seul, et risque d'aspect artificiel sur les visages.

## 5. Typographie et sous-titres

- Polices : **Instrument Serif** (titres, mots-clés en italique) et **Inter** (sous-titres, surtitres), toutes deux sous licence SIL OFL, chargées localement.
- Logo « Femmes de foi en affaires » : l'emblème doré a été extrait du visuel fourni puis vectorisé (potrace, dégradé or), ce qui le garde net en 4K. Le nom a été recomposé en Inter espacé, car il était rogné par le cercle dans le visuel d'origine. Le logo apparaît au moment où « Le souper de Noël » se dévoile, sur un médaillon bordeaux pour le détacher du foulard doré, puis sur le carton final. Seules les plages 915–1040 et 1760–1877 ont été re-rendues et insérées dans le rendu existant (`pipeline/splice_encode.sh`). Aux raccords, l'écart avec le rendu d'origine est de 0,2/255, soit du bruit de compression.
- Palette : blanc, or champagne `#EBC98F` (contraste ≥ 7:1 sur le bordeaux de la robe), voile bordeaux pour le carton.
- Moments typographiques : étiquettes « Tu as porté / ta famille », « … / ton entreprise » (reprises des mots du message) ; triptyque « Femme entrepreneur, Femme battante, Femme de foi. » ; révélation « Souper annuel · 2026 / Le souper de Noël » avec particules dorées ; signature « À très vite ! » ; carton final.
- Sous-titres incrustés : 120 px (environ 5,6 % de la largeur), placés à 70–77 % de la hauteur, sous le visage et au-dessus des interfaces sociales. Lecture progressive (mot prononcé à 100 %, mots suivants à 55 %), mots importants en serif italique doré avec une légère impulsion. Les coupures de ligne sont calculées (après les virgules, jamais un mot-outil en fin de ligne).
- SRT : 23 sous-titres, 00:00:14,002 → 00:00:58,440, chevauchements : aucun. Orthographe et ponctuation corrigées (apostrophes typographiques, espace fine avant « ! ») sans modifier les propos.

## 6. Son

- **Voix** (WA0048, mono, bande AAC limitée à 14 kHz, plancher −65 dB) : passe-haut 75 Hz, débruitage FFT très léger, EQ −3 dB à 320 Hz (effet « carton » du micro de téléphone), +3 dB à 3,2 kHz (intelligibilité), +1,5 dB au-delà de 8 kHz, de-esser, compression 3:1 douce. La voix d'origine est intacte et jamais accélérée.
- **Musique : composition originale** écrite pour l'image (ré majeur, 120 BPM). Timelapse en ostinato de piano et cordes en crescendo (vi–IV–I–V), roulement puis silence d'une croche avant l'impact sur la tonique, halo tenu pendant le ralenti. Sous la voix, un tapis piano feutré, cordes et chœur (I–V/3–vi–iii/5–IV–I/3–IV–V). Célesta et harpe accompagnent la révélation du souper, une montée douce soutient « Les places partent… », et la cadence IV–V–I se résout juste après « À très vite ! ». Rendu FluidSynth avec la banque MuseScore General (licence MIT) ; percussions, montée, impact et whooshes sont synthétisés. Aucune musique tierce.
- **Effets** : whooshes synchronisés sur les whip pans, montée et cymbale inversée avant l'impact, impact (sub + attaque), scintillement à la révélation, cloche sur le carton, ambiance réelle du bureau sur la fin du ralenti.
- **Mixage** : ducking de la musique piloté par l'enveloppe de la voix (anticipation 60 ms, attaque 60 ms, relâche 450 ms, −8 dB). Musique environ 17,5 LU sous la voix pendant le message. Normalisation ITU-R BS.1770 et limiteur true-peak suréchantillonné x4.

| Mesure (fichier final) | Master 4K | Web |
|---|---|---|
| Loudness intégrée | -14.0 LUFS | -14.0 LUFS |
| Plage dynamique (LRA) | 5.1 LU | 5.1 LU |
| True-peak | -1.0 dBTP | -1.0 dBTP |

## 7. Rendu et encodage

- Remotion 4.0.543 (Chrome Headless Shell 158), composition `Film` 2160×3840 à 30 i/s, espace couleur bt709, captures JPEG qualité 98, mezzanine **ProRes 422 HQ**.
- Master : x265 CRF 15, Main10 4:2:0, GOP 2 s, aq-mode 3 (contre le banding), SAO désactivé et psy-rd 2.0 (préservation du grain), balises Rec.709, `hvc1`, faststart. Preset `fast` : `slow` tournait à 0,25–0,4 image/s sur les 4 vCPU (environ 2 h d'encodage). Sur un extrait de test, le débit à CRF 15 était identique entre presets (environ 52 Mb/s, dicté par le grain), donc l'écart visuel à ce niveau de qualité est négligeable.
- Web : x264 preset slow, CRF 18 plafonné à 10 Mb/s (fichier plus léger à partager), High@4.2, réduction lanczos avec tramage, balises Rec.709, faststart.
- Audio : multiplexé directement depuis le mixage master WAV 24 bits, donc une seule compression AAC.

## 8. Contrôle qualité (mesures sur les fichiers finaux)

| Contrôle | Master 4K | Web |
|---|---|---|
| frames_ok | ✅ | ✅ |
| fps_ok | ✅ | ✅ |
| aspect_9_16 | ✅ | ✅ |
| rec709_tags | ✅ | ✅ |
| audio_48k_stereo | ✅ | ✅ |
| loudness_ok | ✅ | ✅ |
| av_duration_delta_s | 0.0 | 0.0 |
| no_unexpected_black | ✅ | ✅ |
| freezes_only_on_end_card | ✅ | ✅ |
| audio_in_sync | ✅ | ✅ |
| images | 1878 | 1878 |
| durée | 62.6 s | 62.6 s |
| décalage audio / mix de référence | 0.0 ms | 0.0 ms |
| segments noirs | aucun | aucun |
| gels détectés | [[61.2333, 61.8]] | [[61.2667, 61.8]] |
| synchro voix / source WA0048 (par segment) | [0.02, -0.31, -0.02, 0.04, 0.04] ms | (même mix) |

**Synchronisation son/image, démontrée par trois mesures directes indépendantes (1 à 3) :**
1. Image : sur une mire numérotée, le composant vidéo de Remotion affiche exactement l'image source attendue (`trimBefore`), et la signature de mouvement du film correspond à celle de `message.mp4` (décalage 0 ou 1 image, à la précision de la mesure).
2. Son : la voix montée est alignée sur la source à moins de 0,5 ms près dans chaque segment. La latence de 27,9 ms introduite par la chaîne de traitement (limiteur à anticipation, débruiteur FFT) a été détectée lors du contrôle, puis mesurée par intercorrélation et compensée.
3. Fichiers finaux : l'image du MP4 est alignée sur la source, à image près : tronçon 625–735 → +0 (corr. 0.996), tronçon 1050–1235 → -1 (corr. 0.97), tronçon 1250–1400 → +0 (corr. 0.903), tronçon 1550–1710 → +0 (corr. 0.906). Les valeurs ±1 correspondent à une égalité de corrélation avec 0, dans la limite de résolution de la mesure. L'audio des MP4 est identique au mix de référence (décalage indiqué dans le tableau).
4. Un contrôle labial indirect (activité de la bouche corrélée à l'énergie de la voix) a aussi été essayé. Sa corrélation est trop faible (environ 0,1) et bimodale (pics à 0 et à −8 images, soit une période syllabique) pour trancher. Il n'est pas retenu comme critère : les mesures directes 1 à 3 sont concordantes et démontrent la synchronisation.

Le seul noir présent est le fondu d'ouverture voulu (0,33 s) et la fermeture au noir finale. Les « gels » éventuellement détectés en fin de film correspondent au carton final, quasi statique par conception. Les images clés ont aussi été vérifiées visuellement : chaque transition, la transition signature image par image, chaque sous-titre et chaque moment typographique (voir `PLANCHE_CONTACT.jpg`).

## 9. Limites et recommandations

- **Définition** : agrandissement de qualité, mais sans vrai détail 4K (voir section 4). Sur un très grand écran, l'image restera celle d'une source 720p WhatsApp bien traitée.
- **Musique** : composition originale avec des instruments échantillonnés libres. Pour une diffusion de prestige, une piste orchestrale sous licence pourra la remplacer (`pipeline/compose_music.py` / `mix_master.py`, ou `audio: "stems"` dans Remotion).
- **Carton final** : les sources ne donnent ni date, ni lieu, ni lien d'inscription, et rien n'a été inventé. La prop `endCard.details` permet de les ajouter puis de relancer le rendu.
- **Ordre des clips** : WA0049 est placé avant WA0048 (voir section 2).
- **Remotion** : gratuit pour les particuliers et les entreprises de 3 personnes au plus ; au-delà, une licence entreprise est requise.

## 10. Reproduire ou modifier

Voir `README.md`. La chaîne complète est dans `pipeline/run_all.sh`, et les décisions de montage dans `pipeline/edl.py`.
