"""EDL des 10 capsules « Me Rania Arbi répond à vos questions » (Lexia Notaires).

Chaque capsule : une question (titre), des extraits de source (secondes, sur les
mots), éventuellement des passages où l'interlocuteur hors champ pose la question
(affichés en carton « Question » au lieu de sous-titres), des incrustations photo
(avec déclic d'appareil) et des mots-clés mis en valeur.
"""

CAPSULES = [
    dict(id="C01", title="Que se passe-t-il le jour du mariage ?", short="Le grand jour",
         parts=[("WA0078", 0.45, 8.6), ("WA0078", 34.4, 50.8)],
         questions=[("WA0078", 45.6, 46.45, "Vous êtes ?")],
         photos=[("photo_01.jpg", 0.45)],
         emphasis=["célébrer un mariage", "sceller l'union", "formellement", "au terme de la loi", "Maître Arbi", "Lexia Notaires"]),
    dict(id="C02", title="Le contrat de mariage, c'est avant ou après ?", short="Contrat de mariage",
         parts=[("WA0078", 9.5, 34.3)],
         photos=[("photo_03.jpg", 0.35), ("photo_14.jpg", 0.8)],
         emphasis=["contrat de mariage", "avant la célébration", "régime matrimonial", "au terme de la loi"]),
    dict(id="C03", title="Après le mariage, que deviennent les documents ?", short="Les documents",
         parts=[("WA0076", 0.0, 32.0)],
         questions=[("WA0076", 0.0, 1.70, "Que fait-on des documents après le mariage ?")],
         photos=[("photo_02.jpg", 0.55)],
         emphasis=["directeur d'État civil", "statistiques du Canada", "une copie", "certificat de mariage"]),
    dict(id="C04", title="Mariage ou union de fait : pourquoi se marier ?", short="Pourquoi se marier",
         parts=[("WA0077", 0.0, 20.7)],
         questions=[("WA0077", 0.0, 11.36,
                     "Pourquoi c'est important de faire célébrer son mariage, plutôt que de rester conjoints de fait ? Ça change quoi au quotidien ?")],
         photos=[("photo_10.jpg", 0.8)],
         emphasis=["contrat de mariage", "très important", "régime matrimonial"]),
    dict(id="C05", title="Les 3 régimes matrimoniaux au Québec", short="Régimes matrimoniaux",
         parts=[("WA0077", 20.6, 43.65)],
         photos=[("photo_06.jpg", 0.5)],
         emphasis=["trois régimes matrimoniaux", "société d'acquêts", "régime légal", "séparation des biens", "communauté de biens meubles"]),
    dict(id="C06", title="Pourquoi signer un contrat de mariage ?", short="Se protéger",
         parts=[("WA0077", 43.7, 66.8)],
         photos=[("photo_15.jpg", 0.3), ("photo_09.jpg", 0.75)],
         emphasis=["se protéger", "imposées légalement", "d'autres clauses", "d'un commun accord", "moduler"]),
    dict(id="C07", title="Ne pas se marier : quels risques ?", short="La protection du mariage",
         parts=[("WA0077", 71.0, 82.5), ("WA0077", 83.0, 96.2)],
         questions=[("WA0077", 71.0, 82.5,
                     "Pour ceux qui ne veulent pas se marier, quels conseils leur donner ? Quels avantages à se marier au Québec, avec des enfants ou des biens ?")],
         photos=[("photo_04.jpg", 0.62)],
         emphasis=["protection supplémentaire", "séparation de biens", "les dettes"]),
    dict(id="C08", title="L'union parentale, c'est quoi concrètement ?", short="L'union parentale",
         parts=[("WA0079", 0.95, 27.2)],
         photos=[("photo_11.jpg", 0.55)],
         emphasis=["union parentale", "automatiquement", "enfant commun", "patrimoine familial", "la famille réside"]),
    dict(id="C09", title="Quels biens entrent dans le patrimoine familial ?", short="Patrimoine familial",
         parts=[("WA0079", 27.2, 62.7)],
         photos=[("photo_13.jpg", 0.4), ("photo_08.jpg", 0.78)],
         emphasis=["véhicule automobile", "chalet", "patrimoine familial", "union parentale", "droits et des obligations", "enfant commun"]),
    dict(id="C10", title="Retour sur un mariage célébré", short="Dans les coulisses",
         parts=[("WA0075", 1.4, 24.7)],
         overrides=[("WA0075", 17.84, "très…"), ("WA0075", 19.44, "« Coupé ! »"), ("WA0075", 23.32, "prête\u202f!")],
         photos=[("photo_05.jpg", 0.42)],
         emphasis=["très bien passé", "satisfaits", "honorée", "sceller", "au terme de la loi", "pas prête"]),
]

OUTRO_PHOTO = "photo_07.jpg"

# Corrections orthographiques (propos inchangés)
FIXES = {
    "matrimonials": "matrimoniaux", "matrimonials,": "matrimoniaux,",
    "d'acqué,": "d'acquêts,", "d'acqué": "d'acquêts",
    "l'exia": "Lexia", "intérieurement": "antérieurement",
    "statistiques": "statistiques",
}

CONTACT = dict(
    firm="Lexia Notaires",
    firm2="& Services juridiques",
    person="Me Rania Arbi, notaire",
    email="contact@lexianotaires.ca",
    phone="514-303-3272",
    offices=["Montréal — Beaubien / Langelier", "Vieux-Saint-Eustache", "Rosemère — chemin de la Grande-Côte"],
)
