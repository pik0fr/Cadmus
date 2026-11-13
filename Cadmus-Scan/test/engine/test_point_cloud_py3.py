import unittest

import numpy as np
from horus.engine.algorithms.point_cloud_generation import PointCloudGeneration


class PointCloudTests(unittest.TestCase):
    def setUp(self):
        self.engine = PointCloudGeneration()
        self.data = self.engine.calibration_data
        self.saved = self.data.__dict__.copy()
        self.addCleanup(self.restore_calibration)
        # Assign the underlying camera data; these fixtures do not need image-size calibration.
        self.data._camera_matrix = np.diag([2., 2., 1.])
        self.data._distortion_vector = np.zeros(5)
        self.data.platform_rotation = np.eye(3)
        self.data.platform_translation = np.zeros(3)

    def restore_calibration(self):
        self.data.__dict__.clear()
        self.data.__dict__.update(self.saved)

    def test_plane_intersection_and_negative_rotation_keep_3_by_n(self):
        result = self.engine.compute_point_cloud(np.pi / 2, [[2, 0], [0, 2]], None,
                                                d=10., n=[0., 0., 1.])
        np.testing.assert_allclose(result, [[0., 10.], [-10., 0.], [10., 10.]], atol=1e-6)
        self.assertEqual(result.shape, (3, 2))

    def test_radial_distortion_is_removed(self):
        self.data._camera_matrix = np.array([[1000., 0., 320.], [0., 1000., 240.], [0., 0., 1.]])
        self.data._distortion_vector = np.array([.1, 0., 0., 0., 0.])
        # Ideal (.2,.1), radial factor 1 + .1*(.2**2 + .1**2) = 1.005.
        result = self.engine.compute_camera_point_cloud([[521.], [340.5]], 10., [0., 0., 1.])
        np.testing.assert_allclose(result, [[2.], [1.], [10.]], atol=1e-5)

    def test_platform_rotation_and_translation_are_applied_in_camera_frame(self):
        self.data.platform_rotation = np.array([[0., -1., 0.], [1., 0., 0.], [0., 0., 1.]])
        self.data.platform_translation = np.array([1., 2., 3.])
        result = self.engine.compute_platform_point_cloud([[2.], [0.]], None,
                                                         d=10., n=[0., 0., 1.])
        # Camera (10,0,10) minus translation is (9,-2,7); R.T gives (-2,-9,7).
        np.testing.assert_allclose(result, [[-2.], [-9.], [7.]], atol=1e-6)

    def test_missing_plane_distance_is_rejected_before_projection(self):
        with self.assertRaisesRegex(AssertionError, 'Plane distance'):
            self.engine.compute_platform_point_cloud([[0.], [0.]], None, n=[0., 0., 1.])

    def test_empty_projection_has_three_rows(self):
        self.assertEqual(self.engine.compute_camera_point_cloud([[], []], 10., [0., 0., 1.]).shape,
                         (3, 0))
