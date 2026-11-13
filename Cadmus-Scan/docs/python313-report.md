# Cadmus-Scan — Python 3.13 et NumPy 2.1

La cible de développement remplace la base Python 3.12 / NumPy 1.26 du lot 1,
à la demande de l'utilisateur. La branche locale est `migration/python313`.

## Dépendances directes

| Paquet | Version retenue |
|---|---|
| NumPy | 2.1.3 |
| SciPy | 1.14.1 |
| OpenCV contrib | 4.11.0.86 |
| pyserial | 3.5 |
| packaging | 24.2 |
| Matplotlib (GUI) | 3.9.4 |
| wxPython (GUI) | 4.2.2 |
| PyOpenGL (GUI) | 3.1.7 |

[NumPy 2.1](https://numpy.org/doc/2.1/release/2.1.0-notes.html) prend en charge
Python 3.13 ; [2.1.3](https://pypi.org/project/numpy/2.1.3/) est la version
corrective retenue de cette série. [SciPy 1.14.1](https://docs.scipy.org/doc/scipy/release/1.14.1-notes.html)
ajoute les wheels Python 3.13. Les distributions d'[OpenCV contrib 4.11.0.86](https://pypi.org/project/opencv-contrib-python/4.11.0.86/)
et de [Matplotlib 3.9.4](https://pypi.org/project/matplotlib/3.9.4/) sont publiées
sur PyPI ; Matplotlib fournit des wheels CPython 3.13. Cela ne constitue pas
une validation du fonctionnement de la GUI Gryphon Scan.

`requirements-dev.txt` et `requirements-gui.txt` incluent la nouvelle base core.
Une seule distribution OpenCV doit être installée. La configuration Ruff cible
`py313`. La CI `python313.yml` cible Python 3.13 sur Windows, Linux et macOS,
et importe explicitement NumPy/SciPy/OpenCV avant les tests pour détecter
les erreurs de chargement des extensions binaires.

## Portée et validation

Les algorithmes, conventions géométriques et fichiers de réglages n'ont pas
été modifiés par ce changement de dépendances. `np.matrix` est conservé ;
les tests numériques existants protègent les formes 3×N, la distorsion et
les rotations/translations. La compatibilité complète de l'application avec
NumPy 2.1 reste à valider : changer la dépendance ne migre pas automatiquement
les modules Python 2 encore présents.

L'environnement local disponible est Python 3.13.15. La tentative d'installation
de NumPy 2.1.3 et des autres dépendances échoue toujours sur l'accès PyPI.
NumPy/OpenCV/SciPy, pytest et Ruff ne sont donc pas installés dans `.venv`.
Les commandes et résultats de cette reprise sont conservés dans
`validation-python313/results.json` et les fichiers voisins.

Contrôles effectués lors de cette reprise : compilation de tout `src/horus`
et du lanceur réussie ; 16 tests série/ScanCapture réussis ; découverte complète
en échec sur les deux modules de test qui importent NumPy. pytest et Ruff sont
absents. `pip check` retourne 0 pour les seuls paquets disponibles, ce qui ne
valide pas les nouvelles dépendances non installées. `git diff --check` passe.

Les 16 tests sans dépendances numériques restent exécutables avec le paquet
pyserial du système. Les 10 tests des réglages et de la géométrie ne peuvent
pas être exécutés tant que NumPy/OpenCV manquent. La CI n'a pas été lancée et
aucune validation Windows/macOS ni matérielle n'est revendiquée.

## Installation dans un environnement avec accès réseau

```sh
python3.13 -m venv .venv
# Activer l'environnement ; Windows : py -3.13 -m venv .venv
python -m pip install -r requirements-dev.txt
python -c "import numpy, scipy, cv2; print(numpy.__version__, scipy.__version__, cv2.__version__)"
python -m compileall -q src/horus
python -m pytest -q
python -m pip check
```

Le fichier `requirements-gui.txt` ajoute une base graphique séparée, non
validée. Les limites de la copie locale (deux ressources amont absentes), du
packaging historique et du moteur restent décrites dans le
[rapport du premier lot](python312-report.md).
