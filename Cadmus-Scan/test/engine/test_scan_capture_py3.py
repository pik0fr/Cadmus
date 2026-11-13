import unittest

from horus.engine.scan.scan_capture import ScanCapture


class ScanCaptureTests(unittest.TestCase):
    def test_initial_state_retains_background_slot(self):
        capture = ScanCapture(lasers=2)
        self.assertEqual(capture.theta, 0)
        self.assertIsNone(capture.texture)
        self.assertEqual(capture.lasers, [None, None, None])

    def test_instances_do_not_share_images(self):
        first, second = ScanCapture(lasers=2), ScanCapture(lasers=2)
        first.lasers[0] = object()
        self.assertIsNone(second.lasers[0])
