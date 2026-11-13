import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
from horus.util import profile, resources


class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.settings = profile.settings
        self.original = self.settings._to_json_dict(None)
        self.addCleanup(self.settings._load_json_dict, self.original, None)

    def test_settings_json_round_trip_preserves_arrays_and_unicode(self):
        self.settings['serial_name'] = 'Port été'
        self.settings['camera_matrix'] = np.eye(3)
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / 'settings.json')
            self.settings.save_settings(path)
            payload = json.loads(Path(path).read_text())
            self.assertEqual(payload['settings_version'], 1)
            self.assertEqual(payload['preferences']['serial_name']['value'], 'Port été')
            self.settings['serial_name'] = ''
            self.settings['camera_matrix'] = np.zeros((3, 3))
            self.settings.load_settings(path)
        self.assertEqual(self.settings['serial_name'], 'Port été')
        np.testing.assert_array_equal(self.settings['camera_matrix'], np.eye(3))

    def test_bool_string_cast_retains_historical_behavior(self):
        self.settings['invert_motor'] = 'False'
        self.assertIs(self.settings['invert_motor'], True)
        self.settings['invert_motor'] = False
        self.assertIs(self.settings['invert_motor'], False)

    def test_numeric_cast_and_range_are_preserved(self):
        self.settings['brightness_control'] = '999'
        self.assertEqual(self.settings['brightness_control'], 255)

    def test_default_array_is_copied(self):
        matrix = self.settings.get_default('camera_matrix')
        matrix[0, 0] = -1
        self.assertNotEqual(self.settings.get_default('camera_matrix')[0, 0], -1)

    def test_localization_installs_under_python3(self):
        import builtins
        from unittest.mock import patch
        with patch.object(builtins, '_', create=True):
            resources.setup_localization('English')
            self.assertEqual(builtins._('scan'), 'scan')
