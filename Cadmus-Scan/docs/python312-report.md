# Gryphon Scan — lot 1, état au 13 novembre 2026

> Rapport historique. La cible a ensuite été changée à la demande de l'utilisateur
> vers Python 3.13 / NumPy 2.1 : voir [l'état actuel](python313-report.md).

Les changements sont appliqués dans `/home/pik0fr/Projets/gryphon-scan`, branche
`migration/python312`. **La validation du lot sous Python 3.12 reste bloquée.**
Le moteur complet et l'application graphique ne sont pas encore migrés.

## Provenance et limites de la copie locale

L'accès Git/PyPI du terminal échoue : résolution DNS impossible de `github.com`
et `pypi.org`. Aucun dépôt Gryphon Scan n'a été trouvé dans les dossiers examinés.
Les fichiers ont été récupérés via le connecteur GitHub à partir de `develop`,
commit `e172c0445bb2cbb6116aaeaae771a3a498b99bf3`.

305 fichiers sur 307 ont été restaurés avec vérification de leur empreinte Git.
Le commit racine local est un import de cette copie, sans historique amont.
Deux fichiers binaires trop volumineux n'ont pas pu être récupérés :

- `doc/readthedocs/source/_static/scanner-components/stepper-motor.png` ;
- `pkg/win32/drivers/CDM v2.10.00 WHQL Certified.exe`.

Leurs empreintes sont dans [l'inventaire](python312-audit.json). Aucun fichier
factice ne les remplace. Les notices et la licence GPL existantes sont conservées.
Le patch fourni à côté du dépôt contient les seuls changements du lot : appliqué
sur une copie complète du commit amont, il préserve ces deux fichiers.

## Changements appliqués

| Fichiers | Changement |
|---|---|
| `pyproject.toml`, `requirements-core.txt`, `requirements-dev.txt`, `requirements-gui.txt`, `.gitignore` | Configuration pytest/Ruff, dépendances séparées, caches exclus. Packaging historique conservé. |
| `.github/workflows/python312.yml` | Matrice Python 3.12 Windows/Linux/macOS, compilation, lint du cœur migré, pytest et pip check sans matériel. Non exécutée ici. |
| `engine/driver/board.py` | G-code en `str`, écriture ASCII en `bytes`, lecture ASCII avec remplacement, reset binaire, handshake décodé, init encodée une fois, API série actuelles, découverte par `list_ports`. Callback hors gestion des erreurs série, appelé une seule fois. Fermeture du port en cas d'échec de connexion. |
| `util/profile.py`, `util/resources.py` | `MutableMapping`, types natifs, `str`, `range`, installation gettext Python 3. Le comportement historique `bool('False') == True` est conservé et testé. |
| `engine/scan/ciclop_scan.py` | `queue.Queue`, `range`, `print()`. Vidage par `get_nowait()`/`task_done()`, sans remplacer la file ni prétendre résoudre la durée de vie des anciens threads. |
| `engine/algorithms/point_cloud_generation.py` | Indentation et assertion sur `d` corrigées. `np.matrix`, produits matriciels, signes d'angle et `cv2.undistortPoints` conservés. |
| `engine/calibration/calibration_data.py` | `hashlib.md5`, import du pilote différé au seul accès caméra pour permettre les imports numériques sans wxPython. |
| `engine/driver/camera_usb.py` | Syntaxe, `range`, remplacement de `distutils.version` supprimé sous Python 3.12 par `packaging.version.Version`. Backends matériels non validés. |
| `horus` | Interpréteur Python 3 et `str(e)` au lieu de `e.message`. |

Corrections supplémentaires de syntaxe uniquement pour compiler l'arbre :
`engine/driver/uvc/mac/{cf_string,raw}.py`, `gui/util/opengl_helpers.py`,
`gui/workbench/calibration/pages/{cloud_correction,laser_triangulation,pattern_settings,platform_extrinsics,scanner_autocheck}.py`,
`gui/workbench/scanning/main.py`, `util/{gryphon_util,point_cloud_tools}.py`,
`util/mesh_loaders/ply.py`. Dans `engine/calibration/platform_by_lasers.py`, seule
l'instruction dont l'indentation était absente a été indentée ; l'algorithme
incomplet et son `for/else` restent à examiner au lot 2.

Les cinq modules de test couvrent les valeurs initiales de ScanCapture, son
troisième emplacement de fond et l'isolation des images, le protocole série,
les réglages JSON/NumPy, la triangulation synthétique, la distorsion et les
transformations du plateau. `test/conftest.py` initialise les ressources comme
le lanceur, sans importer la GUI ni ouvrir de matériel.

## Versions proposées

La base proposée est Python 3.12, NumPy 1.26.4, SciPy 1.13.1 et OpenCV contrib
4.10.0.84. Les distributions publiées sont consultables sur
[NumPy/PyPI](https://pypi.org/project/numpy/1.26.4/),
[SciPy/PyPI](https://pypi.org/project/scipy/1.13.1/) et
[OpenCV/PyPI](https://pypi.org/project/opencv-contrib-python/4.10.0.84/).
Cette vérification de publication ne valide pas leur fonctionnement avec Gryphon Scan.

wxPython 4.2.2, Matplotlib 3.8.4 et PyOpenGL 3.1.7 constituent une base GUI à
valider séparément. [wxPython 4.2.2](https://wxpython.org/news/2024-09-11-wxpython-422-release/index.html)
inclut des corrections Python 3.12. Sous Linux, il faut prévoir la construction
et les bibliothèques système lorsque les wheels wxPython ne conviennent pas.
Les dépendances directes sont épinglées ; ce n'est pas un verrouillage transitif
complet. Ne pas installer plusieurs distributions OpenCV dans le même environnement.

## Résultats réellement obtenus

Environnement : Linux/NixOS, Python **3.13.15**, environnement `.venv`.
Python 3.12 absent. pyserial 3.5 est accessible dans le store Nix via PYTHONPATH.
NumPy, OpenCV, SciPy, pytest et Ruff ne sont pas installés ; leur installation
est empêchée par l'accès réseau. Les versions épinglées visent Python 3.12.

| Commande avec `.venv/bin/python` | Résultat |
|---|---|
| `-m compileall -q -f src/horus` | Code 0, 101 fichiers Python compilables sous 3.13. Deux avertissements préexistants `is not ''` dans `util/version.py`. |
| `-m py_compile horus` | Code 0. |
| `-m unittest test_serial_protocol test_scan_capture_py3 test_board -v` | **16 tests réussis**, aucun port ouvert. PYTHONPATH inclut `src`, `test/engine` et le paquet pyserial système. |
| `-m unittest discover -s test/engine -v` | Échec : 16 tests réussis, **2 modules en erreur d'import NumPy** : `test_profile_py3`, `test_point_cloud_py3`. Leurs 10 tests ne sont pas exécutés. |
| `-m ruff check src/horus --select E4,E7,E9,F821,F822,F823` | Non exécuté : module Ruff absent, code 1. |
| `-m pytest -q` | Non exécuté : module pytest absent, code 1. |
| `-m pip check` | Code 0, mais seulement pour les paquets disponibles. Ne valide pas les fichiers requirements non installés. |
| `git diff --check` | Code 0. |

Les commandes exactes, PYTHONPATH et sorties sont conservés dans
[validation/results.json](validation/results.json) et les fichiers voisins.
Les tentatives `pip install --retries 0 --timeout 5 pytest ruff numpy pyserial`
ont échoué ; le diagnostic `pip -vv` confirme l'échec DNS vers PyPI.

Un contrôle syntaxique `ast.parse(feature_version=(3,12))` passe sur les 101
fichiers ; il ne remplace pas une exécution sous Python 3.12. L'audit amont
constate 16 fichiers initialement non compilables, et relève encore **89
références à des noms/API Python 2** hors des modules migrés. Il ne s'agit pas
d'un résultat Ruff : voir [python312-audit.json](python312-audit.json).

Cinq tests série ont également été exécutés contre le code amont : ils
reproduisent deux échecs d'assertion (réponse et double callback) et trois
erreurs (reset en texte, assemblage bytes/str, `xrange`). Ils passent avec le
pilote modifié. Les tests série passent aussi avec un profil déjà importé,
pour vérifier leur indépendance de l'ordre de collecte.

`test/conftest.py` s'applique à pytest. Pour lancer ensuite toute la suite avec
unittest directement, initialiser également `resources.set_base_path('res')`
avant la découverte, comme le fait ce fichier pour pytest.

## Reprise de validation et lot 2

Dans un environnement ayant Python 3.12 et le réseau :

```sh
python3.12 -m venv .venv312
# Activer .venv312 (Windows : py -3.12 -m venv .venv312).
python -m pip install -r requirements-dev.txt
python -m compileall -q src/horus
python -m ruff check src/horus --select E4,E7,E9,F821,F822,F823
python -m pytest -q
python -m pip check
```

La CI limite le lint bloquant aux modules du cœur migré et aux tests ; l'audit
Ruff de tout l'arbre restera susceptible d'échouer sur les noms hérités.
Aucun résultat Windows/macOS, graphique ou scanner réel n'est revendiqué.

Prochaines étapes : exécuter les 26 tests sous 3.12, puis migrer segmentation,
ROI et calibrations avec références numériques ; corriger la calibration
`platform_by_lasers` (noms non définis et logique incomplète) ; définir et tester
le cycle de connexion `Driver` (son appel à `self.__init__()` et les callbacks
restent à corriger), l'arrêt des threads de scan et les accès série concurrents.
L'attente d'une réponse G-code reste historique, sans nouvelle limite arbitraire
susceptible d'interrompre les mouvements longs. Les backends caméra, UVC macOS,
wxPython/Matplotlib/OpenGL, l'export PLY et la photogrammétrie nécessitent ensuite
des tests dédiés. Le packaging multiplateforme devra intégrer les ressources
dans le paquet et remplacer les chemins Linux absolus de `setup.py` ; ces
ressources et le packaging historique sont conservés dans ce premier lot.
