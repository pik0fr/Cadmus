# Intégration du logiciel dans Cadmus

## Plan de reprise

1. Importer le code local migré, commit `082f36b`, sous `Cadmus-Scan/`,
   en conservant la licence, les notices et les ressources disponibles.
2. Garder l'historique existant du dépôt Cadmus et son dossier matériel.
   Déplacer la CI à la racine avec le répertoire de travail `Cadmus-Scan`.
3. Publier une branche `migration/python313`, ouvrir une proposition de
   changements et exécuter les tests Python 3.13 / NumPy 2.1 dans GitHub Actions.
4. Corriger les échecs réels du cœur migré avant de poursuivre le moteur/GUI.
   Consigner les contrôles exécutés et les limites matérielles.

Cette reprise met en œuvre la suite du premier lot demandée dans la conversation.
Elle conserve les calculs géométriques et le nom interne du paquet `horus`.
La documentation historique a été conservée dans `README_Gryphon.md`.

## Provenance et limites initiales

Source amont : `tangentially/gryphon-scan`, branche `develop`, commit
`e172c0445bb2cbb6116aaeaae771a3a498b99bf3`.

La copie locale initiale ne contient pas deux fichiers amont :

- `doc/readthedocs/source/_static/scanner-components/stepper-motor.png` ;
- `pkg/win32/drivers/CDM v2.10.00 WHQL Certified.exe`.

Leurs empreintes sont dans `python312-audit.json`. Aucun fichier factice ne les
remplace. La provenance complète et les limites du packaging historique sont
documentées dans `python312-report.md`.

Le terminal local ne peut pas télécharger les dépendances PyPI. Les anciens
journaux de validation conservés dans ce dossier décrivent cet environnement
local et ne constituent pas des résultats de GitHub Actions.

## Résultats de la reprise — 13 novembre 2026

Le logiciel est publié dans [la proposition #1](https://github.com/pik0fr/Cadmus/pull/1),
branche `migration/python313`. Le dépôt local actif est maintenant le dépôt
Cadmus ; l'ancien checkout Gryphon Scan est conservé.

La [validation GitHub Actions](https://github.com/pik0fr/Cadmus/actions/runs/43449511489)
du commit `f9e68619f354ca13b6a23e618ec2aa187569dc47` est réussie :

| Système | pytest | Compilation | Ruff du cœur | pip check |
|---|---|---|---|---|
| Linux | 29 réussis | Réussie | Réussi | Réussi |
| Windows | 29 réussis | Réussie | Réussi | Réussi |
| macOS | 29 réussis | Réussie | Réussi | Réussi |

Les trois jobs importent NumPy **2.1.3**, SciPy **1.14.1** et OpenCV **4.11.0**
(distribution `opencv-contrib-python==4.11.0.86`) sous Python 3.13. Les preuves
et liens individuels sont conservés dans [validation-ci/results.json](validation-ci/results.json).

Les tests couvrent le protocole série, ScanCapture, les réglages JSON/NumPy,
la triangulation synthétique, la correction de distorsion, les transformations
du plateau et les imports système sans interface graphique. Les dix avertissements
par job concernent `np.matrix`, volontairement conservé pour préserver les calculs.

Deux problèmes ont été corrigés à partir des résultats réels de la CI : les
comparaisons de types et le nettoyage de l'alias gettext dans `profile.py`, puis
le chargement prématuré de wxPython depuis `util/system.py`. Trois tests ajoutés
reproduisent ce dernier problème et vérifient les drapeaux système et les
contrôles de versions wxPython historiques.

Le contrôle local passe 19 tests sans dépendances numériques. Les 29 tests
complets ont été exécutés sur les runners GitHub, et non dans le terminal local.

## Suite du travail

Le premier cœur testé est validé sur les trois OS. Cela ne valide pas la GUI,
les backends caméra, les calibrations complètes ni un scan réel. Le lint est
limité aux modules migrés : les références Python 2 restantes de l'ancien arbre
restent à traiter. La suite porte sur la segmentation/ROI et les calibrations,
le cycle de connexion et d'arrêt des threads, puis wxPython, les exports et les
tests avec caméra et carte série. Les deux ressources amont absentes restent
à récupérer.
