import sys
import types
import unittest
from unittest.mock import patch

from horus.engine.driver.board import Board, WrongFirmware


class FakeSerial:
    def __init__(self, *args, lines=None, **kwargs):
        self.lines = list(lines if lines is not None else [b'ok\r\n'])
        self.is_open = True
        self.timeout = kwargs.get('timeout', 2)
        self.writes = []
        self.error = None

    def reset_input_buffer(self):
        pass

    def reset_output_buffer(self):
        pass

    def write(self, value):
        if not isinstance(value, bytes):
            raise TypeError('serial writes must be bytes')
        if self.error:
            raise self.error
        self.writes.append(value)
        return len(value)

    def readline(self):
        return self.lines.pop(0) if self.lines else b'ok\r\n'

    def readlines(self):
        result, self.lines = self.lines, []
        return result

    def close(self):
        self.is_open = False


class SerialProtocolTests(unittest.TestCase):
    def setUp(self):
        self.board = Board()
        self.port = FakeSerial()
        self.board._serial_port = self.port
        self.board._is_connected = True
        self.sleep = patch('horus.engine.driver.board.time.sleep')
        self.sleep.start()
        self.addCleanup(self.sleep.stop)

    def test_command_is_ascii_bytes_and_response_text(self):
        self.assertEqual(self.board._send_command('G50'), 'ok\r\n')
        self.assertEqual(self.port.writes, [b'G50\r\n'])

    def test_read_lines_decodes_with_replacement(self):
        self.port.lines = [b'12\r\n', b'\xff\r\n']
        self.assertEqual(self.board.read(True), '12\r\n\ufffd\r\n')

    def test_reset_sends_control_x_bytes(self):
        self.board._reset()
        self.assertEqual(self.port.writes, [b'\x18\r\n'])

    def test_motor_laser_and_lights_preserve_gcode(self):
        self.board.parent = types.SimpleNamespace(board=self.board)
        self.board.motor_invert(True)
        self.board.motor_move(1.5)
        self.board.lasers_on()
        self.board.lasers_off()
        self.board.set_light(0, 300)
        self.board.lights_off()
        self.assertEqual(self.port.writes, [b'G1X-1.500000\r\n', b'M71T1\r\n',
                         b'M71T2\r\n', b'M70T1\r\n', b'M70T2\r\n',
                         b'M71T3F255\r\n', b'M70T3\r\n'])

    def test_write_failure_calls_callback_once(self):
        self.port.error = OSError('disconnected')
        responses = []
        self.board._send_command('G50', responses.append)
        self.assertEqual(responses, [''])
        self.assertEqual(self.board._tries, 1)

    def test_callback_exception_is_not_retried(self):
        def callback(response):
            raise ValueError('consumer error')
        with self.assertRaisesRegex(ValueError, 'consumer error'):
            self.board._send_command('G50', callback)
        self.assertEqual(self.board._tries, 0)

    def test_disconnected_command_calls_callback_once_without_writing(self):
        self.board._is_connected = False
        responses = []
        self.board._send_command('G50', responses.append)
        self.assertEqual(responses, [''])
        self.assertEqual(self.port.writes, [])

    def test_repeated_io_failures_notify_unplug_once(self):
        notifications = []
        self.board.parent = types.SimpleNamespace(unplugged=False)
        self.board.set_unplug_callback(lambda: notifications.append('unplugged'))
        self.port.error = OSError('unplugged')
        for _ in range(6):
            self.board._send_command('G50')
        self.assertEqual(notifications, ['unplugged'])
        self.assertTrue(self.board.parent.unplugged)

    def test_bytes_commands_are_rejected_at_application_boundary(self):
        with self.assertRaises(TypeError):
            self.board._send_command(b'G50')
        self.assertEqual(self.port.writes, [])

    def test_port_discovery_returns_device_names(self):
        ports = [types.SimpleNamespace(device='COM7'), types.SimpleNamespace(device='/dev/ttyUSB0')]
        with patch('horus.engine.driver.board.list_ports.comports', return_value=ports):
            self.assertEqual(self.board.get_serial_list(), ['COM7', '/dev/ttyUSB0'])

    def connect_with_lines(self, lines):
        port = FakeSerial(lines=lines)
        self.connected_port = port
        settings = dict(firmware_string='Horus 0.2', init_string='$1=255',
                        motor_speed_control=200, motor_acceleration_control=100,
                        invert_motor=False)
        fake_profile = types.ModuleType('horus.util.profile')
        fake_profile.settings = settings
        with patch.dict(sys.modules, {'horus.util.profile': fake_profile}), \
                patch('horus.util.profile', fake_profile, create=True), \
                patch('horus.engine.driver.board.serial.Serial', return_value=port):
            self.board.connect()
        return port

    def test_handshake_decodes_firmware_and_encodes_init_once(self):
        port = self.connect_with_lines([b'boot\r\n', b'Horus 0.2\r\n'])
        self.assertTrue(self.board._is_connected)
        self.assertEqual(port.writes, [b'\x18\r\n', b'$1=255\r\n', b'G1F200\r\n',
                                     b'$120=100\r\n', b'G50\r\n'])

    def test_wrong_firmware_closes_port(self):
        with patch('horus.engine.driver.board.time.monotonic', side_effect=[0, 0, 2]):
            with self.assertLogs('horus.engine.driver.board', level='ERROR'), \
                    self.assertRaises(WrongFirmware):
                self.connect_with_lines([b'boot\r\n', b'other firmware\r\n'])
        self.assertFalse(self.board._is_connected)
        self.assertIsNone(self.board._serial_port)
        self.assertFalse(self.connected_port.is_open)
