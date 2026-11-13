import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import types
import unittest
from unittest.mock import patch


class SystemTests(unittest.TestCase):
    def load_system(self):
        path = Path(__file__).resolve().parents[2] / 'src/horus/util/system.py'
        spec = importlib.util.spec_from_file_location('system_under_test', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_resources_can_import_when_gui_imports_are_unavailable(self):
        code = '''
import importlib.abc
import json
import sys

class BlockGui(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == 'wx' or fullname.startswith('wx.'):
            raise ImportError('GUI deliberately unavailable')

sys.meta_path.insert(0, BlockGui())
from horus.util import resources, system
print(json.dumps({'resource_path': resources.resource_base_path,
                  'gui_imported': 'wx' in sys.modules}))
'''
        env = os.environ.copy()
        source = str(Path(__file__).resolve().parents[2] / 'src')
        env['PYTHONPATH'] = source + os.pathsep + env.get('PYTHONPATH', '')
        result = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {'resource_path': '', 'gui_imported': False})

    def test_os_detection_does_not_require_wx(self):
        expected = {'Linux': (True, False, False), 'Darwin': (False, True, False),
                    'Windows': (False, False, True), 'FreeBSD': (False, False, False)}
        for name, flags in expected.items():
            with self.subTest(name=name), patch('platform.system', return_value=name):
                module = self.load_system()
                self.assertEqual((module.is_linux(), module.is_darwin(), module.is_windows()), flags)

    def test_gui_version_checks_preserve_legacy_results(self):
        expected = {'2.8.12': (True, False), '3.0.2': (False, True), '4.2.2': (False, False)}
        module = self.load_system()
        for version, flags in expected.items():
            with self.subTest(version=version):
                fake = types.ModuleType('wx')
                fake.__version__ = version
                with patch.dict(sys.modules, {'wx': fake}):
                    self.assertEqual((module.is_wx28(), module.is_wx30()), flags)
