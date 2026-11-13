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
