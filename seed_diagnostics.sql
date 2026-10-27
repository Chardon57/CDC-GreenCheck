-- =============================================================================
-- Pré-remplissage des tables de référence du diagnostic
--   disease   : les problèmes que GreenCheck sait nommer
--   treatment : les conseils (un conseil = une ligne, réutilisable)
--   traiter   : quels conseils pour quelle maladie (plusieurs-à-plusieurs)
--   result    : état affiché à l'utilisateur (Sain / Attention / Malade) + maladie associée
--
-- Règle métier : l'état est déterminé par la maladie (une maladie -> un résultat).
--   Sain      : aucune maladie détectée
--   Attention : problème lié aux conditions de culture (arrosage, lumière, nutrition),
--               corrigeable en ajustant l'entretien
--   Malade    : maladie infectieuse ou infestation, qui demande un traitement ou une isolation
--
-- Script RÉEXÉCUTABLE : il n'ajoute que ce qui manque, sans doublon.
-- À lancer APRÈS un premier démarrage du backend (qui crée les tables) :
--   mariadb -u greencheck_user -p greencheck < seed_diagnostics.sql
-- =============================================================================

USE greencheck;
SET NAMES utf8mb4;

-- Tables temporaires : les données à insérer, décrites une seule fois.
DROP TEMPORARY TABLE IF EXISTS seed_disease;
DROP TEMPORARY TABLE IF EXISTS seed_advice;

CREATE TEMPORARY TABLE seed_disease (
    disease_name VARCHAR(255) NOT NULL,
    state        VARCHAR(255) NOT NULL
);

CREATE TEMPORARY TABLE seed_advice (
    disease_name VARCHAR(255) NOT NULL,
    advice       VARCHAR(255) NOT NULL
);

INSERT INTO seed_disease (disease_name, state) VALUES
    ('Aucune maladie détectée', 'Sain'),
    ('Excès d''arrosage', 'Attention'),
    ('Manque d''eau', 'Attention'),
    ('Excès de lumière', 'Attention'),
    ('Carence nutritive', 'Attention'),
    ('Taches foliaires fongiques', 'Malade'),
    ('Oïdium', 'Malade'),
    ('Rouille', 'Malade'),
    ('Mildiou', 'Malade'),
    ('Maladie bactérienne', 'Malade'),
    ('Maladie virale', 'Malade'),
    ('Ravageurs', 'Malade');

INSERT INTO seed_advice (disease_name, advice) VALUES
    ('Aucune maladie détectée', 'Arroser quand le dessus du terreau est sec, et vider la soucoupe pour que l''eau ne stagne pas.'),
    ('Aucune maladie détectée', 'Placer la plante dans une pièce lumineuse adaptée à son espèce, en évitant le plein soleil derrière une vitre en été.'),
    ('Aucune maladie détectée', 'Inspecter régulièrement le dessous des feuilles pour repérer tôt un éventuel souci, et garder le feuillage propre.'),
    ('Excès d''arrosage', 'Laisser le terreau sécher sur les premiers centimètres avant d''arroser à nouveau.'),
    ('Excès d''arrosage', 'Vérifier que le pot est percé et vider la soucoupe un quart d''heure après chaque arrosage.'),
    ('Excès d''arrosage', 'Si le feuillage jaunit et que le terreau reste détrempé, dépoter la plante : couper les racines brunes et molles, puis rempoter dans un terreau frais et drainant.'),
    ('Manque d''eau', 'Arroser lentement et en profondeur, jusqu''à ce que l''eau s''écoule par les trous de drainage.'),
    ('Manque d''eau', 'Si le terreau est dur et repousse l''eau, plonger le pot dans un seau d''eau pendant dix à quinze minutes.'),
    ('Manque d''eau', 'Adopter un rythme d''arrosage régulier et éloigner la plante des sources de chaleur (radiateur, vitre ensoleillée).'),
    ('Excès de lumière', 'Éloigner la plante de la vitre ou filtrer la lumière avec un voilage aux heures les plus ensoleillées.'),
    ('Excès de lumière', 'Couper les feuilles entièrement desséchées : les zones brûlées ne reverdissent pas.'),
    ('Excès de lumière', 'Habituer la plante progressivement à une exposition plus lumineuse plutôt que de la changer brutalement de place.'),
    ('Carence nutritive', 'Apporter un engrais équilibré pour plantes vertes pendant la période de croissance, à la dose indiquée sur l''emballage.'),
    ('Carence nutritive', 'Rempoter dans un terreau frais si la plante n''a pas été rempotée depuis plus de deux ans : le substrat s''épuise.'),
    ('Carence nutritive', 'Arroser avec de l''eau de pluie ou une eau peu calcaire : un excès de calcaire peut bloquer l''absorption du fer et jaunir les feuilles.'),
    ('Taches foliaires fongiques', 'Retirer les feuilles et tiges atteintes avec des ciseaux propres et les jeter aux ordures (pas au compost).'),
    ('Taches foliaires fongiques', 'Arroser au pied, sans mouiller le feuillage, de préférence le matin pour que l''eau s''évapore vite.'),
    ('Taches foliaires fongiques', 'Aérer la pièce et espacer les plantes pour limiter l''humidité stagnante autour du feuillage.'),
    ('Taches foliaires fongiques', 'Si l''atteinte progresse, traiter avec un fongicide autorisé pour le jardinage amateur, en suivant strictement la notice.'),
    ('Oïdium', 'Retirer les feuilles et tiges atteintes avec des ciseaux propres et les jeter aux ordures (pas au compost).'),
    ('Oïdium', 'Aérer la pièce et espacer les plantes pour limiter l''humidité stagnante autour du feuillage.'),
    ('Oïdium', 'Isoler la plante des autres le temps du traitement pour éviter la contamination.'),
    ('Oïdium', 'Traiter avec un produit anti-oïdium autorisé pour le jardinage amateur (par exemple à base de soufre), en suivant la notice.'),
    ('Rouille', 'Retirer les feuilles et tiges atteintes avec des ciseaux propres et les jeter aux ordures (pas au compost).'),
    ('Rouille', 'Arroser au pied, sans mouiller le feuillage, de préférence le matin pour que l''eau s''évapore vite.'),
    ('Rouille', 'Isoler la plante des autres le temps du traitement pour éviter la contamination.'),
    ('Rouille', 'Si l''atteinte progresse, traiter avec un fongicide autorisé pour le jardinage amateur, en suivant strictement la notice.'),
    ('Mildiou', 'Retirer les feuilles et tiges atteintes avec des ciseaux propres et les jeter aux ordures (pas au compost).'),
    ('Mildiou', 'Arroser au pied, sans mouiller le feuillage, de préférence le matin pour que l''eau s''évapore vite.'),
    ('Mildiou', 'Aérer la pièce et espacer les plantes pour limiter l''humidité stagnante autour du feuillage.'),
    ('Mildiou', 'Si l''atteinte progresse, traiter avec un fongicide autorisé pour le jardinage amateur, en suivant strictement la notice.'),
    ('Maladie bactérienne', 'Retirer les feuilles et tiges atteintes avec des ciseaux propres et les jeter aux ordures (pas au compost).'),
    ('Maladie bactérienne', 'Désinfecter les ciseaux ou sécateurs à l''alcool avant et après chaque coupe.'),
    ('Maladie bactérienne', 'Arroser au pied sans éclabousser le feuillage : les bactéries se propagent par les gouttes d''eau.'),
    ('Maladie bactérienne', 'Les traitements sont peu efficaces contre les bactéries : isoler la plante et la jeter aux ordures si l''atteinte progresse malgré tout.'),
    ('Maladie virale', 'Isoler immédiatement la plante : il n''existe pas de traitement curatif contre les virus.'),
    ('Maladie virale', 'Lutter contre les insectes piqueurs (pucerons, aleurodes, thrips) qui transmettent les virus d''une plante à l''autre.'),
    ('Maladie virale', 'Désinfecter les ciseaux ou sécateurs à l''alcool avant et après chaque coupe.'),
    ('Maladie virale', 'Si la plante dépérit, la jeter aux ordures (pas au compost) pour protéger les autres plantes.'),
    ('Ravageurs', 'Isoler la plante et inspecter le dessous des feuilles et les aisselles des tiges, où se cachent cochenilles, pucerons et araignées rouges.'),
    ('Ravageurs', 'Nettoyer le feuillage avec un chiffon humide ; pour les cochenilles, utiliser un coton-tige imbibé d''alcool à 70°.'),
    ('Ravageurs', 'Pulvériser du savon noir dilué ou un produit adapté aux plantes d''intérieur, selon la notice, et renouveler chaque semaine pendant trois semaines.'),
    ('Ravageurs', 'Surveiller les plantes voisines : les ravageurs passent facilement d''une plante à l''autre.');

START TRANSACTION;

-- 1. Maladies
INSERT INTO disease (name)
SELECT s.disease_name
FROM seed_disease s
WHERE NOT EXISTS (SELECT 1 FROM disease d WHERE d.name = s.disease_name);

-- 2. Conseils (un même texte n'est enregistré qu'une fois, même s'il sert à plusieurs maladies)
INSERT INTO treatment (advice)
SELECT DISTINCT s.advice
FROM seed_advice s
WHERE NOT EXISTS (SELECT 1 FROM treatment t WHERE t.advice = s.advice);

-- 3. Liens maladie <-> conseils
INSERT IGNORE INTO traiter (id_disease, id_treatment)
SELECT DISTINCT d.id_disease, t.id_treatment
FROM seed_advice s
JOIN disease   d ON d.name   = s.disease_name
JOIN treatment t ON t.advice = s.advice;

-- 4. Résultats : un état par maladie
INSERT INTO result (label, id_disease)
SELECT s.state, d.id_disease
FROM seed_disease s
JOIN disease d ON d.name = s.disease_name
WHERE NOT EXISTS (
    SELECT 1 FROM result r WHERE r.label = s.state AND r.id_disease = d.id_disease
);

COMMIT;

DROP TEMPORARY TABLE seed_disease;
DROP TEMPORARY TABLE seed_advice;

-- Contrôle : une ligne par résultat, avec le nombre de conseils associés
SELECT r.label AS etat, d.name AS maladie, COUNT(tr.id_treatment) AS nb_conseils
FROM result r
JOIN disease d       ON d.id_disease = r.id_disease
LEFT JOIN traiter tr ON tr.id_disease = d.id_disease
GROUP BY r.id_result, r.label, d.name
ORDER BY FIELD(r.label, 'Sain', 'Attention', 'Malade'), d.name;
