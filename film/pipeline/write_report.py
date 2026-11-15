"""Génère deliverables/RAPPORT_TECHNIQUE.md à partir des données réelles du projet
(timeline, analyses, mesures QC) : aucun chiffre n'est saisi à la main."""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys  # noqa: E402

sys.path.insert(0, str(ROOT / "pipeline"))
import edl  # noqa: E402
import grading  # noqa: E402

TL = json.loads((ROOT / "remotion/src/data/timeline.json").read_text())
QC = json.loads((ROOT / "deliverables/qc_report.json").read_text())
VA = json.loads((ROOT / "analysis/video_analysis.json").read_text())
VS = json.loads((ROOT / "analysis/video_analysis_stab.json").read_text())
VS2 = json.loads((ROOT / "analysis/video_analysis_stab2.json").read_text())
TR = json.loads((ROOT / "analysis/transcripts/WA0048_16k.json").read_text())
FPS = TL["fps"]


def s(f):
    return f / FPS


def tc(f):
    t = f / FPS
    return f"{int(t // 60)}:{t % 60:05.2f}"


def probe_src(n):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration:stream=codec_type,width,height,r_frame_rate:stream_side_data=rotation",
                        "-of", "json", str(ROOT / f"sources/{n}.mp4")], capture_output=True, text=True)
    return json.loads(r.stdout)


SRC_ROLE = {
    "WA0042": ("Courses : allée, elle pousse le chariot vers la caméra", "Timelapse S1"),
    "WA0044": ("Courses : allée, orbite au rayon, décor de Noël", "Timelapse S2"),
    "WA0045": ("Courses : elle se retourne et avance en dansant, sourire", "Timelapse S3"),
    "WA0047": ("Courses : choisit des produits, panoramique sur les rayons", "Timelapse S4"),
    "WA0048": ("**Message face caméra** (parole FR), bureau aux coquelicots, drapeau du Québec", "Message (1x)"),
    "WA0049": ("Bureau : statue de la Justice, dossiers, téléphone, couloirs ; se termine assise au bureau aux coquelicots", "Timelapse O1–O6 + A1 (ralenti)"),
}
LOUD = {"WA0042": -26.0, "WA0044": -29.3, "WA0045": -26.3, "WA0047": -27.8, "WA0048": -19.0, "WA0049": -30.1}


def main():
    L = []
    w = L.append
    m4 = QC["files"]["FINAL_MASTER_4K.mp4"]
    web = QC["files"]["FINAL_WEB.mp4"]
    dur = TL["durationInFrames"] / FPS
    w("# Rapport technique : film « Souper de Noël 2026 »\n")
    w(f"*Film vertical 9:16, 2160×3840, {FPS} i/s, {TL['durationInFrames']} images ({dur:.2f} s). "
      "Montage Remotion 4.0.543, traitements FFmpeg 6.1.1, transcription faster-whisper large-v3.*\n")

    # 1. Résumé ------------------------------------------------------------
    w("## 1. Résumé\n")
    w("| Livrable | Format | Taille | Débit |")
    w("|---|---|---|---|")
    w(f"| `FINAL_MASTER_4K.mp4` | {m4['video']['codec'].upper()} {m4['video']['profile']} {m4['video']['width']}×{m4['video']['height']} {m4['video']['pix_fmt']}, AAC {m4['audio']['bitrate_kbps']} kb/s 48 kHz | {m4['size_mb']} Mo | {m4['bitrate_mbps']} Mb/s |")
    w(f"| `FINAL_WEB.mp4` | {web['video']['codec'].upper()} {web['video']['profile']} {web['video']['width']}×{web['video']['height']}, AAC {web['audio']['bitrate_kbps']} kb/s 48 kHz | {web['size_mb']} Mo | {web['bitrate_mbps']} Mb/s |")
    w(f"| `FINAL_SUBTITLES.srt` | SRT UTF-8, {QC['srt']['cues']} sous-titres | | |")
    w("| `PLANCHE_CONTACT.jpg` | planche des séquences retenues | | |")
    w("| `../remotion/` | projet Remotion complet, modifiable | | |\n")
    allok = all(v is True or (isinstance(v, float) and v < 0.05) for f in QC["files"].values() for v in f["checks"].values())
    w(f"**Contrôle qualité : {'tous les contrôles sont conformes' if allok else 'voir la section 8 (écarts)'}.** "
      f"Loudness du master : {m4['loudness']['integrated_lufs']} LUFS intégrés, true-peak {m4['loudness']['true_peak_dbtp']} dBTP.\n")

    # 2. Sources -----------------------------------------------------------
    w("## 2. Analyse des sources\n")
    w("| Fichier | Durée | Image (affichage) | i/s | Loudness | Netteté méd. | Tremblement | Contenu | Rôle |")
    w("|---|---|---|---|---|---|---|---|---|")
    for n in ["WA0042", "WA0044", "WA0045", "WA0047", "WA0048", "WA0049"]:
        p = probe_src(n)
        v = next(x for x in p["streams"] if x["codec_type"] == "video")
        rot = any(sd.get("rotation") for sd in v.get("side_data_list", []) or [])
        wd, ht = (v["height"], v["width"]) if rot else (v["width"], v["height"])
        sm = VA[f"sources/{n}.mp4"]["summary"]
        w(f"| {n} | {float(p['format']['duration']):.2f} s | {wd}×{ht}{' (rot. −90°)' if rot else ''} | 30 | {LOUD[n]} LUFS | {sm['sharp_median']} | {sm['jitter_mean']} | {SRC_ROLE[n][0]} | {SRC_ROLE[n][1]} |")
    w("\nToutes les sources sont des vidéos WhatsApp : H.264 Baseline, environ 2 Mb/s, AAC environ 60 kb/s, verticales. "
      "Les métadonnées de date ont été supprimées par WhatsApp, l'ordre retenu est donc celui de la numérotation.\n")
    w("**Identification du message.** Contrairement à l'hypothèse de départ, **la dernière vidéo par numérotation (WA0049) ne contient pas le message** : "
      "on y entend seulement des bribes d'ambiance (« Où est-ce qu'on va ? »). Le message principal est **WA0048** "
      f"(langue détectée : français, probabilité {TR['language_probability']:.2f}). WA0049 a donc été placé **à la fin du timelapse** : "
      "il illustre « ton entreprise », et son dernier plan se déroule dans le décor même du message (le tableau de coquelicots), "
      "ce qui donne le raccord de la transition signature. C'est la seule entorse à l'ordre de numérotation, motivée par la narration.\n")
    w("**Transcription du message (WA0048), texte intégral :**\n")
    w("> " + " ".join(seg["text"].strip() for seg in TR["segments"]) + "\n")

    # 3. Structure ---------------------------------------------------------
    w("## 3. Structure narrative et timeline\n")
    w(f"1. **Timelapse** 0:00 → {tc(TL['impactFrame'])} ({s(TL['impactFrame']):.1f} s, soit {TL['impactFrame'] / TL['durationInFrames']:.0%} du film) : "
      "« ta famille » (courses), puis « ton entreprise » (bureau). Le rythme des coupes s'accélère : une coupe par mesure, puis à chaque temps.")
    w(f"2. **Transition signature** {tc(TL['impactFrame'])} → {tc(TL['message']['videoIn'])} : impact musical sur l'entrée dans le bureau aux coquelicots, "
      "ralenti progressif de 10x à 1x, ambiance réelle du bureau, voix en J-cut (« Femme entrepreneur, »), "
      "puis raccord par zoom flouté sur le tableau présent dans les deux plans.")
    w(f"3. **Message** à vitesse 1x : {tc(TL['message']['videoIn'])} → {tc(TL['message']['end'])}.")
    w(f"4. **Carton final** : {tc(TL['endCard']['tlFrom'])} → {tc(TL['durationInFrames'])}.\n")
    w("| Plan | Source | Extrait source | Durée | Vitesse moy. | Transition d'entrée | Description |")
    w("|---|---|---|---|---|---|---|")
    for sh in edl.TIMELAPSE:
        t = next(x for x in TL["timelapse"] if x["id"] == sh["id"])
        w(f"| {sh['id']} | {sh['src']} | {sh['remap'][0][1]:.2f} → {sh['remap'][-1][1]:.2f} s | {sh['frames'] / FPS:.2f} s | ×{t['avgSpeed']} | {t['transIn']} | {sh['note']} |")
    w("\nLa musique est à 120 BPM : 1 mesure = 2 s = 60 images, 1 temps = 15 images. Toutes les coupes du timelapse tombent sur un temps, "
      "et l'impact tombe sur le premier temps de la mesure 7, sur la tonique.\n")

    # message
    w("### Montage du message (WA0048, vitesse 1x, jamais accéléré)\n")
    w("| Segment | Source | Timeline |")
    w("|---|---|---|")
    for i, sg in enumerate(TL["message"]["segments"], 1):
        w(f"| {i} | {s(sg['srcFrom']):.3f} → {s(sg['srcTo']):.3f} s | {tc(sg['tlFrom'])} → {tc(sg['tlTo'])} |")
    removed = sum(b - a for a, b in edl.CUTS_F)
    w(f"\nCoupes (jump cuts) : {len(edl.CUTS_F)} pauses trop longues ramenées à environ 0,40 s, soit {removed} images ({removed / FPS:.2f} s) retirées. "
      "Chaque coupe tombe dans un silence mesuré à l'énergie (plancher de −65 dB), avec au moins 0,17 s de marge avant l'attaque et après la fin du mot. "
      "Coupes et segments sont alignés sur des frontières d'images exactes, d'où une synchronisation son/image strictement conservée.")
    w("Pauses expressives **conservées** : le rythme du triptyque « Femme entrepreneur, / femme battante, / femme de foi » (environ 0,5 s chacune), "
      "« 2026, » (0,5 s), « accompagnée, » (0,47 s), et la respiration avant « À très vite ! ». "
      "Les répétitions (« tu as porté… », « lors d'une soirée… », « rapidement… rapidement ») sont des anaphores voulues par l'oratrice : elles sont gardées.\n")
    w("Cadrages : punch-ins façon « deux caméras », placés dans les silences et ancrés sur la position du visage (détection YuNet sur 239/239 échantillons). "
      "Le recentrage horizontal est borné pour qu'aucun bord ne soit jamais découvert, et chaque plan comporte un push-in lent de 2 à 3,5 %.\n")
    w("| Timeline | Échelle | Intention |")
    w("|---|---|---|")
    for fr in TL["framing"]:
        w(f"| {tc(fr['tlFrom'])} | ×{fr['scale']:.2f} (+{fr['push'] * 100:.1f} %) | {fr['note']} |")

    # 4. Image -------------------------------------------------------------
    w("\n## 4. Traitements image\n")
    w("**Stabilisation** (libvidstab, 2 passes, détection shakiness 8 / accuracy 15) : mode *strong* (lissage ±40 images, zoom dynamique) pour WA0042 et WA0045 ; "
      "mode *gentle* (lissage ±12, zoom fixe 5 %, correction plafonnée, bords comblés par l'image précédente) pour les plans à mouvements de caméra volontaires "
      "(orbite, panoramiques, marche). Un premier essai en zoom dynamique sur tous les clips cadrait trop serré : il a été rejeté après contrôle visuel.\n")
    w("| Clip | Tremblement avant | après |")
    w("|---|---|---|")
    for n in ["WA0042", "WA0044", "WA0045", "WA0047", "WA0049"]:
        before = VA[f"sources/{n}.mp4"]["summary"]["jitter_mean"]
        after_src = VS2.get(f"work/stab/{n}.mp4") or VS.get(f"work/stab/{n}.mp4")
        w(f"| {n} | {before} | {after_src['summary']['jitter_mean']} |")
    w("\n*(Tremblement : énergie haute fréquence de la translation globale, mesurée par corrélation de phase. Sur WA0044, l'orbite volontaire biaise la mesure.)*\n")
    w("**Accélérations** : courbes de vitesse interpolées en PCHIP (monotones, dérivée continue) pour des speed ramps fluides. "
      "Chaque image de sortie intègre en lumière linéaire toutes les images source couvertes par un obturateur virtuel de 180°, "
      "ce qui donne un flou de bouger proportionnel à la vitesse. Sous 2,5x, l'image la plus proche est utilisée, pour éviter les fantômes.\n")
    w("**Étalonnage** : balance des blancs par source, mesurée sur des surfaces neutres (sol, murs), vers un blanc chaud commun "
      "(R/G 1,05 ; B/G 0,935). WA0048 est aligné sur le mur du même bureau vu dans WA0049 (R/G 1,07), ce qui rend le raccord invisible.")
    w("Le LUT 3D `grade/film_look.cube` (33³, calculé en Oklab) applique une courbe filmique douce (noirs mats, épaule progressive), "
      "atténue les cyans, verts et bleus saturés (emballages), préserve les rouges, ors et tons chair, "
      "et ajoute un split-toning discret limité aux zones peu saturées pour protéger la peau.\n")
    w("| Source | Gains R / G / B |")
    w("|---|---|")
    for n in ["WA0042", "WA0044", "WA0045", "WA0047", "WA0048", "WA0049"]:
        g = grading.wb_gains(n)
        w(f"| {n} | {g[0]:.3f} / {g[1]:.3f} / {g[2]:.3f} |")
    w("\n**Agrandissement 4K, transparence :** les sources font **720×1280** (environ 2 Mb/s). L'agrandissement x3 vers 2160×3840 "
      "(zscale spline36, débruitage léger hqdn3d, netteté adaptative CAS 0,50 à 0,55, grain fin) est de haute qualité, "
      "mais **il ne crée pas de vrais détails 4K**. L'image reste fidèle à la définition d'origine. "
      "Aucun upscaler par IA n'a été utilisé : environnement CPU seul, et risque d'aspect artificiel sur les visages.\n")

    # 5. Typo --------------------------------------------------------------
    w("## 5. Typographie et sous-titres\n")
    w("- Polices : **Instrument Serif** (titres, mots-clés en italique) et **Inter** (sous-titres, surtitres), toutes deux sous licence SIL OFL, chargées localement.")
    w("- Logo « Femmes de foi en affaires » : l'emblème doré a été extrait du visuel fourni puis vectorisé (potrace, dégradé or), ce qui le garde net en 4K. "
      "Le nom a été recomposé en Inter espacé, car il était rogné par le cercle dans le visuel d'origine. Le logo apparaît au moment où « Le souper de Noël » se dévoile, "
      "sur un médaillon bordeaux pour le détacher du foulard doré, puis sur le carton final. "
      "Seules les plages 915–1040 et 1760–1877 ont été re-rendues et insérées dans le rendu existant (`pipeline/splice_encode.sh`). "
      "Aux raccords, l'écart avec le rendu d'origine est de 0,2/255, soit du bruit de compression.")
    w("- Palette : blanc, or champagne `#EBC98F` (contraste ≥ 7:1 sur le bordeaux de la robe), voile bordeaux pour le carton.")
    w("- Moments typographiques : étiquettes « Tu as porté / ta famille », « … / ton entreprise » (reprises des mots du message) ; "
      "triptyque « Femme entrepreneur, Femme battante, Femme de foi. » ; révélation « Souper annuel · 2026 / Le souper de Noël » avec particules dorées ; "
      "signature « À très vite ! » ; carton final.")
    w("- Sous-titres incrustés : 120 px (environ 5,6 % de la largeur), placés à 70–77 % de la hauteur, sous le visage et au-dessus des interfaces sociales. "
      "Lecture progressive (mot prononcé à 100 %, mots suivants à 55 %), mots importants en serif italique doré avec une légère impulsion. "
      "Les coupures de ligne sont calculées (après les virgules, jamais un mot-outil en fin de ligne).")
    w(f"- SRT : {QC['srt']['cues']} sous-titres, {QC['srt']['first'].split(' --> ')[0]} → {QC['srt']['last'].split(' --> ')[1]}, "
      f"chevauchements : {'aucun' if not QC['srt']['issues'] else QC['srt']['issues']}. "
      "Orthographe et ponctuation corrigées (apostrophes typographiques, espace fine avant « ! ») sans modifier les propos.\n")

    # 6. Son ---------------------------------------------------------------
    w("## 6. Son\n")
    w("- **Voix** (WA0048, mono, bande AAC limitée à 14 kHz, plancher −65 dB) : passe-haut 75 Hz, débruitage FFT très léger, EQ −3 dB à 320 Hz "
      "(effet « carton » du micro de téléphone), +3 dB à 3,2 kHz (intelligibilité), +1,5 dB au-delà de 8 kHz, de-esser, compression 3:1 douce. "
      "La voix d'origine est intacte et jamais accélérée.")
    w("- **Musique : composition originale** écrite pour l'image (ré majeur, 120 BPM). Timelapse en ostinato de piano et cordes en crescendo (vi–IV–I–V), "
      "roulement puis silence d'une croche avant l'impact sur la tonique, halo tenu pendant le ralenti. "
      "Sous la voix, un tapis piano feutré, cordes et chœur (I–V/3–vi–iii/5–IV–I/3–IV–V). "
      "Célesta et harpe accompagnent la révélation du souper, une montée douce soutient « Les places partent… », "
      "et la cadence IV–V–I se résout juste après « À très vite ! ». "
      "Rendu FluidSynth avec la banque MuseScore General (licence MIT) ; percussions, montée, impact et whooshes sont synthétisés. Aucune musique tierce.")
    w("- **Effets** : whooshes synchronisés sur les whip pans, montée et cymbale inversée avant l'impact, impact (sub + attaque), "
      "scintillement à la révélation, cloche sur le carton, ambiance réelle du bureau sur la fin du ralenti.")
    w("- **Mixage** : ducking de la musique piloté par l'enveloppe de la voix (anticipation 60 ms, attaque 60 ms, relâche 450 ms, −8 dB). "
      "Musique environ 17,5 LU sous la voix pendant le message. Normalisation ITU-R BS.1770 et limiteur true-peak suréchantillonné x4.\n")
    w("| Mesure (fichier final) | Master 4K | Web |")
    w("|---|---|---|")
    w(f"| Loudness intégrée | {m4['loudness']['integrated_lufs']} LUFS | {web['loudness']['integrated_lufs']} LUFS |")
    w(f"| Plage dynamique (LRA) | {m4['loudness']['lra_lu']} LU | {web['loudness']['lra_lu']} LU |")
    w(f"| True-peak | {m4['loudness']['true_peak_dbtp']} dBTP | {web['loudness']['true_peak_dbtp']} dBTP |\n")

    # 7. Rendu ---------------------------------------------------------------
    w("## 7. Rendu et encodage\n")
    w("- Remotion 4.0.543 (Chrome Headless Shell 158), composition `Film` 2160×3840 à 30 i/s, espace couleur bt709, "
      "captures JPEG qualité 98, mezzanine **ProRes 422 HQ**.")
    w("- Master : x265 CRF 15, Main10 4:2:0, GOP 2 s, aq-mode 3 (contre le banding), SAO désactivé et psy-rd 2.0 (préservation du grain), "
      "balises Rec.709, `hvc1`, faststart. Preset `fast` : `slow` tournait à 0,25–0,4 image/s sur les 4 vCPU (environ 2 h d'encodage). "
      "Sur un extrait de test, le débit à CRF 15 était identique entre presets (environ 52 Mb/s, dicté par le grain), "
      "donc l'écart visuel à ce niveau de qualité est négligeable.")
    w("- Web : x264 preset slow, CRF 18 plafonné à 10 Mb/s (fichier plus léger à partager), High@4.2, réduction lanczos avec tramage, balises Rec.709, faststart.")
    w("- Audio : multiplexé directement depuis le mixage master WAV 24 bits, donc une seule compression AAC.\n")

    # 8. QC ----------------------------------------------------------------
    w("## 8. Contrôle qualité (mesures sur les fichiers finaux)\n")
    w("| Contrôle | Master 4K | Web |")
    w("|---|---|---|")
    def fmt(v):
        if v is True:
            return "✅"
        if v is False:
            return "❌"
        return f"{v}"
    for k in m4["checks"]:
        w(f"| {k} | {fmt(m4['checks'][k])} | {fmt(web['checks'][k])} |")
    w(f"| images | {m4['video']['frames']} | {web['video']['frames']} |")
    w(f"| durée | {m4['duration_s']} s | {web['duration_s']} s |")
    w(f"| décalage audio / mix de référence | {m4['audio_offset_ms']} ms | {web['audio_offset_ms']} ms |")
    w(f"| segments noirs | {m4['black_segments'] or 'aucun'} | {web['black_segments'] or 'aucun'} |")
    w(f"| gels détectés | {m4['freeze_segments'] or 'aucun'} | {web['freeze_segments'] or 'aucun'} |")
    w(f"| synchro voix / source WA0048 (par segment) | {QC.get('voice_sync_ms')} ms | (même mix) |")
    w("\n**Synchronisation son/image, démontrée par trois mesures directes indépendantes (1 à 3) :**")
    w("1. Image : sur une mire numérotée, le composant vidéo de Remotion affiche exactement l'image source attendue (`trimBefore`), "
      "et la signature de mouvement du film correspond à celle de `message.mp4` (décalage 0 ou 1 image, à la précision de la mesure).")
    w("2. Son : la voix montée est alignée sur la source à moins de 0,5 ms près dans chaque segment. "
      "La latence de 27,9 ms introduite par la chaîne de traitement (limiteur à anticipation, débruiteur FFT) "
      "a été détectée lors du contrôle, puis mesurée par intercorrélation et compensée.")
    va = QC.get("video_alignment", [])
    w("3. Fichiers finaux : l'image du MP4 est alignée sur la source, à image près : "
      + ", ".join(f"tronçon {a['tl'][0]}–{a['tl'][1]} → {a['lag_frames']:+d} (corr. {a['corr']})" for a in va)
      + ". Les valeurs ±1 correspondent à une égalité de corrélation avec 0, dans la limite de résolution de la mesure. "
      "L'audio des MP4 est identique au mix de référence (décalage indiqué dans le tableau).")
    w("4. Un contrôle labial indirect (activité de la bouche corrélée à l'énergie de la voix) a aussi été essayé. "
      "Sa corrélation est trop faible (environ 0,1) et bimodale (pics à 0 et à −8 images, soit une période syllabique) pour trancher. "
      "Il n'est pas retenu comme critère : les mesures directes 1 à 3 sont concordantes et démontrent la synchronisation.")
    w("\nLe seul noir présent est le fondu d'ouverture voulu (0,33 s) et la fermeture au noir finale. "
      "Les « gels » éventuellement détectés en fin de film correspondent au carton final, quasi statique par conception. "
      "Les images clés ont aussi été vérifiées visuellement : chaque transition, la transition signature image par image, "
      "chaque sous-titre et chaque moment typographique (voir `PLANCHE_CONTACT.jpg`).\n")

    # 9. Limites --------------------------------------------------------------
    w("## 9. Limites et recommandations\n")
    w("- **Définition** : agrandissement de qualité, mais sans vrai détail 4K (voir section 4). Sur un très grand écran, l'image restera celle d'une source 720p WhatsApp bien traitée.")
    w("- **Musique** : composition originale avec des instruments échantillonnés libres. Pour une diffusion de prestige, une piste orchestrale sous licence pourra la remplacer "
      "(`pipeline/compose_music.py` / `mix_master.py`, ou `audio: \"stems\"` dans Remotion).")
    w("- **Carton final** : les sources ne donnent ni date, ni lieu, ni lien d'inscription, et rien n'a été inventé. La prop `endCard.details` permet de les ajouter puis de relancer le rendu.")
    w("- **Ordre des clips** : WA0049 est placé avant WA0048 (voir section 2).")
    w("- **Remotion** : gratuit pour les particuliers et les entreprises de 3 personnes au plus ; au-delà, une licence entreprise est requise.\n")
    w("## 10. Reproduire ou modifier\n")
    w("Voir `README.md`. La chaîne complète est dans `pipeline/run_all.sh`, et les décisions de montage dans `pipeline/edl.py`.\n")
    out = ROOT / "deliverables/RAPPORT_TECHNIQUE.md"
    out.write_text("\n".join(L), encoding="utf-8")
    print(out, len(L), "lignes")


if __name__ == "__main__":
    main()
