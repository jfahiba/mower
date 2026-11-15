"""EDL — décisions de montage (source unique de vérité).

Toutes les durées sont en secondes ; la timeline tourne à 30 i/s, 120 BPM
(1 temps = 15 images, 1 mesure = 60 images) pour que chaque coupe tombe
exactement sur la grille musicale.

Structure narrative
-------------------
1. Timelapse (0 → 12 s) : « tu as porté ta famille » (courses, WA0042→0047)
   puis « tu as porté ton entreprise » (bureau, WA0049), rythme qui s'intensifie.
2. Transition signature (12 → 15,3 s) : impact musical sur l'entrée dans le
   bureau aux coquelicots, ralenti 10x → 1x, ambiance réelle, puis la voix
   arrive en J-cut (« Femme entrepreneur… ») sur le plan où elle s'assoit, et
   raccord par zoom sur le tableau de coquelicots présent dans les deux plans.
3. Message (WA0048) à vitesse 1x, pauses longues resserrées, punch-ins.
4. Carton final.

Note : WA0049 (bureau) est numéroté après WA0048 (message) mais ne contient pas
le message : il est placé en fin de timelapse car il se termine dans le décor
même du message (raccord) et illustre « ton entreprise ».
"""

FPS = 30
WIDTH = 2160
HEIGHT = 3840
BPM = 120
BEAT = 60.0 / BPM  # 0.5 s

# --------------------------------------------------------------------------
# 1. TIMELAPSE — plans accélérés (sources stabilisées work/stab/*.mp4)
#    remap : clés (t_sortie_relative, t_source) interpolées en PCHIP (monotone,
#            dérivée continue) => speed ramps fluides. Vitesse = pente.
#    Frame-blending à obturateur 180° (flou de bouger proportionnel à la vitesse).
# --------------------------------------------------------------------------
TIMELAPSE = [
    # --- Les courses : « ta famille » ------------------------------------
    dict(id="S1", src="WA0042", frames=60, stab="strong", trans_in="open",
         remap=[(0.0, 0.10), (1.0, 4.00), (2.0, 8.05)],
         note="allée, elle pousse le chariot vers la caméra (≈4x)"),
    dict(id="S2", src="WA0044", frames=60, stab="gentle", trans_in="cut",
         remap=[(0.0, 0.00), (0.70, 3.85), (1.45, 7.20), (2.0, 10.05)],
         note="allée puis orbite autour d'elle au rayon (4.5–5.5x)"),
    dict(id="S3", src="WA0045", frames=60, stab="strong", trans_in="whip",
         remap=[(0.0, 0.00), (0.55, 5.00), (1.55, 10.60), (2.0, 13.30)],
         note="dos, demi-tour, elle avance en dansant, sourire (9x → 5.6x)"),
    dict(id="S4", src="WA0047", frames=60, stab="gentle", trans_in="zoom",
         remap=[(0.0, 3.70), (1.30, 14.90), (2.0, 20.60)],
         note="arrive au chariot, choisit, repart ; panoramique final (8.5x)"),
    # --- Le bureau : « ton entreprise » (rythme qui s'intensifie) ---------
    dict(id="O1", src="WA0049", frames=15, stab="gentle", trans_in="whip",
         remap=[(0.0, 0.05), (0.5, 1.20)],
         note="statue de la Justice (insert)"),
    dict(id="O2", trans_in="cut", src="WA0049", frames=30, stab="gentle",
         remap=[(0.0, 2.70), (1.0, 9.30)],
         note="au bureau, se lève, sort avec les dossiers (6.6x)"),
    dict(id="O3", trans_in="cut", src="WA0049", frames=15, stab="gentle",
         remap=[(0.0, 9.30), (0.5, 16.60)],
         note="couloir (14.6x)"),
    dict(id="O4", trans_in="cut", src="WA0049", frames=30, stab="gentle",
         remap=[(0.0, 16.60), (1.0, 28.60)],
         note="accueil, bureau, téléphone (12x)"),
    dict(id="O5", trans_in="cut", src="WA0049", frames=15, stab="gentle",
         remap=[(0.0, 28.60), (0.5, 36.20)],
         note="déplacements à l'accueil (15.2x)"),
    dict(id="O6", trans_in="cut", src="WA0049", frames=15, stab="gentle",
         remap=[(0.0, 41.00), (0.5, 48.60)],
         note="marche avec les dossiers (15.2x)"),
    # --- Arrivée : impact + ralenti jusqu'à 1x ----------------------------
    dict(id="A1", src="WA0049", frames=99, stab="gentle", trans_in="impact",
         remap=[(0.0, 49.40), (0.45, 52.10), (1.00, 54.30), (1.50, 55.03), (3.30, 56.83)],
         note="entre dans le bureau aux coquelicots, pose les dossiers, s'assoit ; 10x → 1x"),
]

# --------------------------------------------------------------------------
# 2. MESSAGE (WA0048) — vitesse 1x
#    Le son du message démarre en J-cut sur A1 ; l'image du message apparaît
#    à MESSAGE_VIDEO_IN (dans la pause entre « entrepreneur, » et « femme battante »).
#    CUTS : intervalles source supprimés (pauses trop longues), choisis dans des
#    silences mesurés (analysis/WA0048_silences.json), marges conservées :
#    ≥ 0,20 s après la fin d'un mot (queue/respiration), ≥ 0,15 s avant l'attaque.
# --------------------------------------------------------------------------
MESSAGE_SRC = "WA0048"
# (valeurs en images source @30 i/s : synchro son/image exacte à chaque coupe)
MESSAGE_AUDIO_IN_F = 7     # 0,233 s : juste avant la fricative « F » (attaque à ~0,32 s)
MESSAGE_VIDEO_IN_F = 56    # 1,867 s : coupe image dans le silence 1,595–2,110
MESSAGE_OUT_F = 1419       # 47,30 s : sourire final conservé ~1,5 s après « À très vite ! »

CUTS_F = [  # [début, fin) en images source supprimées
    (126, 132),    # 4,200–4,400  pause 620 ms après « foi. »            -> 420 ms
    (221, 234),    # 7,367–7,800  pause 830 ms après « quelque chose. »  -> 397 ms
    (1025, 1032),  # 34,167–34,400 pause 630 ms après « émotions. »      -> 397 ms
    (1166, 1174),  # 38,867–39,133 pause 665 ms après « amie. »          -> 398 ms
]
# Pauses expressives volontairement conservées : rythme du triptyque
# « Femme entrepreneur, / femme battante, / femme de foi » (≈0,5 s), « 2026, »
# (0,5 s), « accompagnée, » (0,47 s), « … rapidement. / À très vite ! » (0,37 s).

# Cadrages (punch-ins). Chaque entrée : à partir du temps source t, échelle cible
# et éventuel recentrage. Les changements sont des coupes franches (style
# « deux caméras ») placées dans les silences, sauf "push" (zoom lent continu).
FRAMING = [
    dict(t=1.85, scale=1.00, push=0.035, note="ouverture large, léger push-in"),
    dict(t=4.305, scale=1.10, push=0.02, note="« L'année 2026 » (jump cut)"),
    dict(t=7.575, scale=1.00, push=0.03, note="« Tu as porté… » (jump cut)"),
    dict(t=11.82, scale=1.16, push=0.02, note="« Mais cette fois-ci » — bascule émotionnelle"),
    dict(t=15.35, scale=1.00, push=0.03, note="« Lors de notre souper annuel… »"),
    dict(t=20.16, scale=1.10, push=0.02, note="« Donc, je t'invite… »"),
    dict(t=28.48, scale=1.00, push=0.03, note="« Lors d'une soirée chaleureuse… »"),
    dict(t=34.28, scale=1.12, push=0.02, note="« Ne viens pas seule » (jump cut)"),
    dict(t=39.01, scale=1.00, push=0.03, note="« Les places partent… » (jump cut)"),
    dict(t=44.99, scale=1.14, push=0.03, note="« À très vite ! » — signature intime"),
]

# --------------------------------------------------------------------------
# 3. TYPOGRAPHIE
# --------------------------------------------------------------------------
# Étiquettes de chapitre du timelapse (reprennent les mots du message).
CHAPTERS = [
    dict(kicker="Tu as porté", title="ta famille", start=0.55, end=3.70),
    dict(kicker="Tu as porté", title="ton entreprise", start=8.15, end=11.30),
]

# Mots mis en valeur dans les sous-titres (accent doré + italique serif).
EMPHASIS = [
    "entrepreneur", "battante", "foi", "2026", "famille", "entreprise",
    "à ton tour", "te laisser porter", "souper de Noël", "célébrer", "rendre grâce",
    "entreprennent", "comprennent", "chaleureuse", "témoignages", "émotions",
    "Ne viens pas seule", "sœur", "amie", "partent rapidement", "t'inscrire",
    "À très vite",
]

# Moments typographiques spéciaux (remplacent les sous-titres le temps du moment).
# t_src en temps source du message.
TITLE_MOMENTS = [
    dict(kind="triad", t_src_start=0.30, t_src_end=4.10,
         lines=[("Femme", "entrepreneur", 0.40), ("Femme", "battante", 2.11), ("Femme", "de foi", 3.34)]),
    dict(kind="event", t_src_start=17.95, t_src_end=21.30,
         kicker="Souper annuel · 2026", title="Le souper de Noël"),
    dict(kind="signoff", t_src_start=44.95, t_src_end=47.30, title="À très vite !"),
]

# Carton final (modifiable : date, lieu, lien d'inscription…)
END_CARD = dict(
    duration=3.6,
    kicker="Souper annuel · 2026",
    title="Le souper de Noël",
    tagline="Femme entrepreneur · Femme battante · Femme de foi",
    cta="Les places partent rapidement — inscris-toi.",
    details="",  # ex. « Samedi 13 décembre · Montréal » — vide = non affiché
)

# --------------------------------------------------------------------------
# 4. REPÈRES SON (en secondes de timeline)
# --------------------------------------------------------------------------
# Les whooshes/impacts sont dérivés des transitions des plans (trans_in).
RISER_BARS = 1.0          # montée sur la dernière mesure avant l'impact (2 s)
TRANSITION_TO_MESSAGE = "matchZoom"  # zoom-through ancré sur le tableau de coquelicots
PAINTING_ANCHOR_A1 = (0.16, 0.13)    # position du tableau dans le dernier plan de A1
PAINTING_ANCHOR_MSG = (0.20, 0.14)   # position du tableau dans le message (début)
