from dataclasses import dataclass
@dataclass
class LaserOnPort:
    portName: str
    model: str
    serial: str
    firmware: str


