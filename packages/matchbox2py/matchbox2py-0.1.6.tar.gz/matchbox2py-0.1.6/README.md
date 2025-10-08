<p align="center">
  <a href="https://integratedoptics.com" target="_blank">
    <img src="https://integratedoptics.com/files/IO_logo.png" alt="Integrated Optics" width="200"/>
  </a>
</p>

<h1 align="center">Official MatchBox2 Python Library</h1>


---

## 🧩 Overview

**MatchBox2 Python Library** provides a simple and structured interface for controlling **Integrated Optics MatchBox2** laser modules over USB serial communication.

It offers:
- High-level API for laser operations
- Structured models for laser info, settings, and readings
- Built-in command parsing for MatchBox2 and Combiner lasers
- Support for automatic device discovery

---

## ⚙️ Installation

Install the library directly from GitHub:

```bash
python -m pip install git+https://github.com/Integrated-optics/matchbox2py.git
```

or from a local clone:

```bash
git clone https://github.com/Integrated-optics/matchbox2py.git
cd matchbox2py
python -m pip install .
```

---

## 🚀 Quickstart

### MatchBox2 Laser Example

```python
from matchbox2 import MatchBox2Laser

available_lasers = MatchBox2Laser().get_available_lasers()

if available_lasers:
    laser = MatchBox2Laser()
    laser.connect(available_lasers[0].portName)
    laser.set_laser_on()
    readings = laser.get_laser_readings()
    print(readings)
    laser.set_laser_off()
    laser.disconnect()
else:
    print("No lasers detected.")
```

### MatchBox2 Laser Combiner Example

```python
from matchbox2 import MatchBox2CombinerLaser

available_lasers = MatchBox2CombinerLaser().get_available_lasers()

if available_lasers:
    laser = MatchBox2CombinerLaser()
    laser.connect(available_lasers[0].portName)
    laser.set_enable_power()
    readings = laser.get_laser_readings()
    print(readings)

    # Enable / disable diodes
    for i in range(1, 5):
        laser.set_diode_enable(i)
    for i in range(1, 5):
        laser.set_diode_disable(i)

    laser.set_disable_power()
    laser.disconnect()
else:
    print("No lasers detected.")
```

---

## 🪪 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🌐 Links

- **Homepage:** [https://integratedoptics.com](https://integratedoptics.com)  
- **Repository:** [https://github.com/Integrated-optics/matchbox2py](https://github.com/Integrated-optics/matchbox2py)  
- **Contact:** [info@integratedoptics.com](mailto:info@integratedoptics.com)

---

<p align="center">
  <i>© 2025 Integrated Optics</i>
</p>
