import serial
import serial.tools.list_ports
from .command.mb2_combiner_commands import CombinerLaserCommands
from .parser.combiner_command_parser import LaserCombinerCommandParser
from .models.laser_on_port import LaserOnPort

class MatchBox2CombinerLaser:

    def __init__(self):
        self.port = None
        self.model_number = None
        self.baudrate = 115200
        self.address = None
        self.ser = None

    def connect(self, port: str):
        if port is None:
            raise ValueError("Port must be provided to connect.")
        available_ports = [p.device for p in serial.tools.list_ports.comports()]
        if port not in available_ports:
            raise ValueError(f"Port {port} is not available.")
        try:
            self.port = port
            self.ser = serial.Serial(self.port, baudrate=self.baudrate, timeout=1)
            if self.is_laser_combiner_on_port():
                self.set_access_level(2,35488)
                return
            raise ConnectionError(f"Connection failed: Laser not recognized on port {self.port}.")
        except serial.SerialException as e:
            print(f"Failed to connect: {e}")

    def disconnect(self):
        """Safely disconnects from the serial port."""
        if self.ser is None:
            return

        if self.ser.is_open:
            try:
                self.ser.close()
            except serial.SerialException as e:
                print(f"Error while disconnecting from {self.port}: {e}")

        self.ser = None
        self.port = None
        self.model_number = None
        self.address = None

    def _send_message(self, message: str):
        if self.ser is None or not self.ser.is_open:
            raise ConnectionError("Serial connection is not open.")
        self.ser.write(message.encode())

    def _get_message(self, expected_lines=1):
        DELIMITER = "\n"
        if self.ser is None or not self.ser.is_open:
            raise ConnectionError("Serial connection is not open.")
        response = []
        for _ in range(expected_lines):
            line = self.ser.readline().decode("utf-8", errors="ignore").strip()
            if line:
                response.append(line)
        return DELIMITER.join(response)

    def set_access_level(self, level: int, code: int):
        self._send_message(CombinerLaserCommands.set_access_level(level, code))
        response = self._get_message()
        LaserCombinerCommandParser.parse_error_message(response)
        LaserCombinerCommandParser.parse_response_successful(response)

    def get_access_level(self):
        self._send_message(CombinerLaserCommands.get_access_level())
        response = self._get_message()
        LaserCombinerCommandParser.parse_error_message(response)
        return LaserCombinerCommandParser.parse_laser_access_level(response)

    def get_laser_info(self):
        self._send_message(CombinerLaserCommands.receive_info())
        response = self._get_message(5)
        LaserCombinerCommandParser.parse_error_message(response)
        return LaserCombinerCommandParser.parse_laser_info(response)

    def get_laser_readings(self):
        self._send_message(CombinerLaserCommands.receive_readings())
        response = self._get_message()
        LaserCombinerCommandParser.parse_error_message(response)
        return LaserCombinerCommandParser.parse_laser_readings(response)

    def get_laser_settings(self):
        self._send_message(CombinerLaserCommands.receive_settings())
        response = self._get_message()
        LaserCombinerCommandParser.parse_error_message(response)
        return LaserCombinerCommandParser.parse_laser_settings(response)

    def set_enable_power(self):
        if self.get_laser_readings().power_state == "OFF":
            self._send_message(CombinerLaserCommands.set_enable_power())
            response = self._get_message()
            LaserCombinerCommandParser.parse_error_message(response)
            LaserCombinerCommandParser.parse_response_successful(response)

    def set_laser_warm_up(self):
        if self.get_laser_readings().power_state == "OFF":
            self._send_message(CombinerLaserCommands.set_laser_warm_up_mode())
            response = self._get_message()
            LaserCombinerCommandParser.parse_error_message(response)
            LaserCombinerCommandParser.parse_response_successful(response)

    def set_disable_power(self):
        self._send_message(CombinerLaserCommands.set_disable_power())
        response = self._get_message()
        LaserCombinerCommandParser.parse_error_message(response)
        LaserCombinerCommandParser.parse_response_successful(response)

    def set_diode_enable(self, index: int):
        self._send_message(CombinerLaserCommands.set_diode_enable(index))
        response = self._get_message()
        LaserCombinerCommandParser.parse_error_message(response)
        LaserCombinerCommandParser.parse_response_successful(response)

    def set_diode_disable(self, index: int):
        self._send_message(CombinerLaserCommands.set_diode_disable(index))
        response = self._get_message()
        LaserCombinerCommandParser.parse_error_message(response)
        LaserCombinerCommandParser.parse_response_successful(response)


    def get_enabled_diodes(self):
        self._send_message(CombinerLaserCommands.get_enabled_diodes())
        response = self._get_message()
        LaserCombinerCommandParser.parse_error_message(response)
        return LaserCombinerCommandParser.parse_enabled_diodes(response)


    def set_diode_current(self,index: int,current :int):
        self._send_message(CombinerLaserCommands.set_diode_current(index,current))
        response = self._get_message()
        LaserCombinerCommandParser.parse_error_message(response)
        LaserCombinerCommandParser.parse_response_successful(response)


    def get_set_diode_currents(self):
        self._send_message(CombinerLaserCommands.get_set_diode_currents())
        response = self._get_message()
        LaserCombinerCommandParser.parse_error_message(response)
        return LaserCombinerCommandParser.parse_set_diode_currents(response)


    def set_diode_current_limit(self, index: int, current: int):
        self._send_message(CombinerLaserCommands.set_diode_current_limit(index, current))
        response = self._get_message()
        LaserCombinerCommandParser.parse_error_message(response)
        LaserCombinerCommandParser.parse_response_successful(response)


    def get_diode_current_limits(self):
        self._send_message(CombinerLaserCommands.get_diode_current_limits())
        response = self._get_message()
        LaserCombinerCommandParser.parse_error_message(response)
        return LaserCombinerCommandParser.parse_get_diode_current_limits(response)


    def get_diode_currents(self):
        self._send_message(CombinerLaserCommands.get_diode_currents())
        response = self._get_message()
        LaserCombinerCommandParser.parse_error_message(response)
        return LaserCombinerCommandParser.parse_get_diode_currents(response)


    def set_diode_name(self, index: int, current: str):
        self._send_message(CombinerLaserCommands.set_diode_name(index, current))
        response = self._get_message()
        LaserCombinerCommandParser.parse_error_message(response)
        LaserCombinerCommandParser.parse_response_successful(response)


    def get_diode_names(self):
        self._send_message(CombinerLaserCommands.get_diode_names())
        response = self._get_message()
        LaserCombinerCommandParser.parse_error_message(response)
        return LaserCombinerCommandParser.parse_get_diode_names(response)

    def set_enable_auto_on(self):
        self._send_message(CombinerLaserCommands.set_enable_auto_on())
        response = self._get_message()
        LaserCombinerCommandParser.parse_error_message(response)
        LaserCombinerCommandParser.parse_response_successful(response)

    def set_disable_auto_on(self):
        self._send_message(CombinerLaserCommands.set_disable_auto_on())
        response = self._get_message()
        LaserCombinerCommandParser.parse_error_message(response)
        LaserCombinerCommandParser.parse_response_successful(response)

    def set_fan_temperature(self, temperature: float):
        self._send_message(CombinerLaserCommands.set_fan_temperature(temperature))
        response = self._get_message()
        LaserCombinerCommandParser.parse_error_message(response)
        LaserCombinerCommandParser.parse_response_successful(response)

    def get_fan_temperature(self):
        self._send_message(CombinerLaserCommands.receive_settings())
        response = self._get_message()
        LaserCombinerCommandParser.parse_error_message(response)
        return LaserCombinerCommandParser.parse_laser_settings(response).fan_temperature

    def set_pin_mode(self, mode_no: int):
        self._send_message(CombinerLaserCommands.set_programmable_pin_level(mode_no))
        response = self._get_message()
        LaserCombinerCommandParser.parse_error_message(response)
        LaserCombinerCommandParser.parse_response_successful(response)

    def get_pin_mode(self):
        self._send_message(CombinerLaserCommands.get_programmable_pin_level())
        response = self._get_message()
        LaserCombinerCommandParser.parse_error_message(response)
        return LaserCombinerCommandParser.parse_laser_programmable_pin_level(response)

    def set_function_save(self):
        self._send_message(CombinerLaserCommands.function_save())
        response = self._get_message()
        LaserCombinerCommandParser.parse_error_message(response)
        LaserCombinerCommandParser.parse_response_successful(response)

    def is_laser_combiner_on_port(self) -> bool:
        laser_info = self.get_laser_info()
        if not laser_info:
            return False
        if isinstance(laser_info.firmware, str):
            parts = laser_info.firmware.split(".")
        else:
            parts = laser_info.firmware
        if not parts or len(parts) != 3:
            return False
        if len(laser_info.model) > 8 and parts[0] == "1" and parts[1] == "8":
            return True

        return False

    def get_available_lasers(self):
        available_ports = serial.tools.list_ports.comports()
        recognized_lasers = []
        for port in available_ports:
            if 'Bluetooth' in port.description:
                continue
            try:
                self.port = port.device
                if self.port is None:
                    raise ValueError("Port must be provided to connect.")
                self.ser = serial.Serial(self.port, baudrate=self.baudrate, timeout=1)
                if self.is_laser_combiner_on_port():
                    laser_info = self.get_laser_info()
                    laser = LaserOnPort(portName=port.device, model=laser_info.model, serial=laser_info.serial_no,
                                        firmware=laser_info.firmware)
                    recognized_lasers.append(laser)
                if self.ser and self.ser.is_open:
                    self.ser.close()
            except (serial.SerialException, ValueError, Exception) as e:
                print(f"Error with port {port.device}: {e}")
        return recognized_lasers
