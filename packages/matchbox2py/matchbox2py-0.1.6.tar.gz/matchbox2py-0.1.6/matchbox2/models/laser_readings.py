from dataclasses import dataclass

@dataclass
class LaserReadings:
    diode_temperature: str
    electronics_temperature: str
    body_temperature: str
    current: str
    tec_load_1: str
    tec_load_2: str
    power_state: str
    fan_load: str
    voltage: str