-- Migration 001 — Fiche plante et type de culture (13/10/2026)
--
--   plant.family               : famille botanique de la plante (nom latin, fournie par Pl@ntNet)
--   analysis.plant_cultivation : type de culture saisi par l'utilisateur (« En pot » / « Pleine terre »)
--
-- Pourquoi un script ? Au démarrage, le backend appelle create_all(), qui crée les tables
-- MANQUANTES mais ne modifie jamais une table existante. Sur une base déjà créée, il faut donc
-- ajouter les colonnes à la main. Sur une base neuve, ce script est inutile (create_all crée tout).
--
-- Idempotent : peut être relancé sans erreur (IF NOT EXISTS). Les lignes existantes gardent NULL.
--
-- Exécution :  mariadb -u greencheck_user -p greencheck < migrations/001_family_et_type_de_culture.sql

USE greencheck;

ALTER TABLE plant    ADD COLUMN IF NOT EXISTS family            VARCHAR(255) NULL;
ALTER TABLE analysis ADD COLUMN IF NOT EXISTS plant_cultivation VARCHAR(255) NULL;
