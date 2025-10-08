from dataclasses import dataclass

@dataclass
class LaserSettings:
    diode_temperature_1: str
    diode_temperature_2: str
    set_current: str
    set_dac: str
    set_optical_power: str
    set_current_limit: str
    auto_start: str
    access_level: str
    fan_temperature: str