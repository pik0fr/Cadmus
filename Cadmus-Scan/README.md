# Cadmus-Scan

Cadmus-Scan est la partie logicielle du projet **Cadmus**, issue de Gryphon Scan
et de Horus. La cible de développement est **Python 3.13 avec NumPy 2.1.3**.

La migration est en cours : le protocole série et un premier socle numérique
passent 29 tests sans matériel sous Linux, Windows et macOS avec NumPy 2.1.3.
L'interface graphique, les calibrations
complètes et le scan sur matériel réel restent à migrer et à valider.

## Développement

Depuis ce dossier, avec Python 3.13 :

```sh
python3.13 -m venv .venv
# Activer .venv ; sous Windows : py -3.13 -m venv .venv
python -m pip install -r requirements-dev.txt
python -m compileall -q src/horus
python -m pytest -q
python -m pip check
```

Les dépendances graphiques candidates sont séparées dans `requirements-gui.txt`.
La CI située à la racine du dépôt teste le cœur sous Windows, Linux et macOS.
Ces tests n'ouvrent aucun port série et n'utilisent aucune caméra.

## Documentation et origine

- [État de l'intégration Cadmus](docs/cadmus-integration.md)
- [Configuration Python 3.13 / NumPy 2.1](docs/python313-report.md)
- [Rapport initial de migration](docs/python312-report.md)
- [Documentation historique Gryphon Scan](README_Gryphon.md)
- [Configuration matérielle personnalisée](README_custom_machine.md)
- [Partie matérielle Cadmus-Scanner](../Cadmus-Scanner/)

Le code issu de Gryphon Scan conserve sa licence [GPL-2.0](LICENSE) et les
notices de ses auteurs. Le paquet Python interne conserve le nom `horus`
pendant la migration pour préserver les imports existants.
