"""Les diagnostics que le moteur sait reconnaître, et comment on les « décrit » au modèle.

Principe du zero-shot : le modèle n'a jamais été entraîné sur NOS diagnostics. On lui donne
à la place une ou plusieurs PHRASES (en anglais, langue d'entraînement du modèle) qui décrivent
ce qu'on voit sur une photo pour chaque diagnostic. Il mesure ensuite à quel point la photo
ressemble à chaque phrase, et le diagnostic dont les phrases ressemblent le plus à la photo gagne.

Les CLÉS de ce dictionnaire sont les noms EXACTS des lignes de la table `disease`
(voir seed_diagnostics.sql à la racine du dépôt) : c'est ce texte que le moteur renvoie au
backend, qui s'en sert pour retrouver le bon Result en base. Un test vérifie que les deux
listes restent identiques (tests/test_labels.py).

Plusieurs phrases par diagnostic : on les moyenne (« prompt ensembling »). Une seule phrase
est fragile (un mot mal choisi fausse tout) ; plusieurs formulations lissent ce défaut.
"""

DIAGNOSTICS: dict[str, list[str]] = {
    # --- État « Sain » ---------------------------------------------------------------
    "Aucune maladie détectée": [
        "a photo of a healthy houseplant with firm, green, shiny leaves",
        "a photo of a thriving green plant with no spots, no yellowing and no damage",
    ],
    # --- État « Attention » : problèmes de conditions de culture ----------------------
    "Excès d'arrosage": [
        "a photo of an overwatered plant with yellowing, soft and drooping leaves",
        "a photo of a plant in soggy waterlogged soil with yellow lower leaves and rot",
    ],
    "Manque d'eau": [
        "a photo of an underwatered plant with dry, crispy, brown leaf edges and wilting",
        "a photo of a thirsty plant with limp, curled and dried leaves in dry soil",
    ],
    "Excès de lumière": [
        "a photo of a sunburned plant with bleached, scorched, brown patches on the leaves",
        "a photo of a plant with leaves faded and burnt by too much direct sunlight",
    ],
    "Carence nutritive": [
        "a photo of a plant with pale yellow leaves and green veins, a nutrient deficiency",
        "a photo of a plant with stunted growth and uniformly yellowing, discolored leaves",
    ],
    # --- État « Malade » : maladies infectieuses et infestations ----------------------
    "Taches foliaires fongiques": [
        "a photo of a leaf with brown spots surrounded by a yellow halo, a fungal leaf spot",
        "a photo of a leaf with round dark brown lesions with concentric rings",
    ],
    "Oïdium": [
        "a photo of a leaf covered with white powdery mildew",
        "a photo of a plant with a white flour-like powder coating on its leaves",
    ],
    "Rouille": [
        "a photo of a leaf with orange and brown rust pustules",
        "a photo of a leaf with rusty orange powdery spots on its underside",
    ],
    "Mildiou": [
        "a photo of a leaf with yellow patches and grey downy mold, downy mildew",
        "a photo of a plant with dark water-soaked blotches and fuzzy grey mold on leaves",
    ],
    "Maladie bactérienne": [
        "a photo of a leaf with dark, water-soaked, angular spots caused by a bacterial infection",
        "a photo of a plant with slimy black spots and soft rotting tissue, bacterial disease",
    ],
    "Maladie virale": [
        "a photo of a leaf with a yellow and green mosaic pattern, a plant virus",
        "a photo of a plant with distorted, curled, mottled leaves caused by a viral disease",
    ],
    "Ravageurs": [
        "a photo of a plant infested with insects such as aphids, mealybugs or spider mites",
        "a photo of a leaf eaten by pests, with insects, webbing or sticky white cottony clusters",
    ],
}
