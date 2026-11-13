from pathlib import Path

from horus.util import resources

# Match the launcher before importing profile, which resolves the platform mesh.
resources.set_base_path(str(Path(__file__).resolve().parents[1] / 'res'))
