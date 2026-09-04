-- Création de la base de donnée nécessaire
CREATE DATABASE IF NOT EXISTS greencheck;

-- Création de l'utilisateur greencheck
CREATE USER 'greencheck_user'@'%' IDENTIFIED BY 'greencheck_pass';

-- Ajout des droits pour cet utilisateur
GRANT ALL PRIVILEGES ON greencheck.* TO 'greencheck_user'@'%';

-- Application des changements
FLUSH PRIVILEGES;