from typing import Optional
from ..models.laser_info import LaserInfo
from ..models.laser_readings import LaserReadings
from ..models.laser_settings import LaserSettings

class LaserCommandParser:
    @staticmethod
    def parse_laser_info(response) -> Optional[LaserInfo]:
        try:
            lines = response.splitlines()
            if len(lines) == 5:
                if "Firmware for MatchBox 2" in response:
                    lines = response.splitlines()
                    return LaserInfo(
                        model=lines[2].replace("Laser model:", ""),
                        serial_no=lines[1].replace("Laser S/N:", ""),
                        firmware=lines[0].replace("Firmware for MatchBox 2 ", "").replace("v", "")
                    )
        except Exception:
            raise "Error parsing matchbox2 info"

    @staticmethod
    def parse_laser_readings(response) -> Optional[LaserReadings]:
        try:
            segments = response.replace("#Readings: ", "").split(' ')
            return LaserReadings(
                diode_temperature=segments[0],
                electronics_temperature=segments[1],
                body_temperature=segments[2],
                current=segments[3].replace("mA", ""),
                tec_load_1=segments[4].replace("%", ""),
                tec_load_2=segments[5].replace("%", ""),
                power_state=segments[6],
                fan_load=segments[7].replace("%", ""),
                voltage=segments[8].replace("V", ""),
            )
        except Exception:
            raise "Error parsing matchbox2 readings"

    @staticmethod
    def parse_laser_settings(response) -> Optional[LaserSettings]:
        try:
            segments = response.replace("#Settings: ", "").split(' ')
            return LaserSettings(
                diode_temperature_1=segments[0],
                diode_temperature_2=segments[1],
                set_current=segments[2],
                set_dac=segments[3],
                set_optical_power=segments[4],
                set_current_limit=segments[5],
                auto_start=segments[6],
                access_level=segments[7],
                fan_temperature=segments[8]
            )
        except Exception:
            raise "Error parsing matchbox2 settings"

    @staticmethod
    def parse_laser_access_level(response):
        if response is not None and "Access level: " in response:
            return response.replace("Access level: ", "")
        raise "Error parsing matchbox2 access level"

    @staticmethod
    def parse_laser_programmable_pin_level(response):
        if response is not None and "<" in response and ">" in response:
            return response.replace("<", "").replace(">", "")
        raise "Error parsing matchbox2 programmable pin level"

    @staticmethod
    def parse_laser_temperature_coefficient(response):
        if response is not None and "<" in response and ">" in response:
            return response.replace("<", "").replace(">", "")
        raise "Error parsing matchbox2 temperature coefficient"

    @staticmethod
    def parse_max_optical_power(response):
        try:
            if response is not None:
                max_optical_power = int(response)
                if 0 < max_optical_power <= 65535:
                    return max_optical_power
            raise "Error parsing matchbox2 max optical power"
        except Exception:
            raise "Error parsing matchbox2 max optical power"

    @staticmethod
    def parse_max_dac(response):
        try:
            if response is not None:
                max_dac = int(response)
                if 0 < max_dac <= 65535:
                    if max_dac > 8191:
                        return 8191
                    return max_dac
            raise "Error parsing matchbox2 max dac"
        except Exception:
            raise "Error parsing matchbox2 max dac"

    @staticmethod
    def parse_mode(response):
        if response is not None and response == "ACC" or response == "APC":
            return response
        raise "Error parsing matchbox2 mode"

    @staticmethod
    def parse_response_successful(response):
        if response is not None and response == "<ACK>":
            return response
        raise "Error parsing successful matchbox2 response"

    @staticmethod
    def parse_error_message(response):
        if response is not None and "<ERR 1>" in response:
            raise "Command forbiden for current access level."
        if response is not None and "<ERR 2>" in response:
            raise "Laser already on or making starting ramp-up."
        if response is not None and "<ERR 3>" in response:
            raise "Laser busy, task is not complete please wait for 1s and try again."
        if response is not None and "<ERR 4>" in response:
            raise "Arguments out of range"
        if response is not None and "<ERR 5>" in response:
            raise "Unknown command"
        if response is not None and "<ERR 6>" in response:
            raise "Laser must be enabled to execute this command"
        if response is not None and "<ERR" in response:
            raise "Unknown error"


