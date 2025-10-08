class CombinerLaserCommands:
    @staticmethod
    def receive_info():
        return "r i"

    @staticmethod
    def receive_settings():
        return "r s"

    @staticmethod
    def receive_readings():
        return "r r"

    @staticmethod
    def set_fan_temperature(temperature: float):
        formatted_temperature = f"{int(temperature * 100):04d}"
        return "c f "+formatted_temperature

    @staticmethod
    def set_access_level(level: int,code:int):
        return f"c u {level} {code}"

    @staticmethod
    def get_access_level():
        return "r l"

    @staticmethod
    def set_disable_power():
        return "e 0"

    @staticmethod
    def set_enable_power():
        return "e 1"

    @staticmethod
    def set_diode_enable(index: int):
        return f"L{index}E"

    @staticmethod
    def set_diode_disable(index: int):
        return f"L{index}D"

    @staticmethod
    def set_enable_auto_on():
        return "c a 1"

    @staticmethod
    def set_disable_auto_on():
        return "c a 0"

    @staticmethod
    def set_laser_warm_up_mode():
        return "e 2"

    @staticmethod
    def get_programmable_pin_level():
        return "P?"

    @staticmethod
    def set_programmable_pin_level(level: int):
        return "P" + str(level)

    @staticmethod
    def get_temperature_coefficient():
        return "TC?"

    @staticmethod
    def set_temperature_coefficient(param):
        return "TC "+str(param)

    @staticmethod
    def get_max_optical_power():
        return "r 4"

    @staticmethod
    def set_dac(dac: int):
        return "c 6 " + str(dac)

    @staticmethod
    def set_dac_max(dac: int):
        return "f 6 " + str(dac)

    @staticmethod
    def get_max_dac():
        return "r 6"

    @staticmethod
    def set_diode_current(index: int,current :int):
        return f"Lc{index} {current}"

    @staticmethod
    def get_set_diode_currents():
        return "Lc?"

    @staticmethod
    def set_diode_current_limit(index: int, current: int):
        return f"Lm{index} {current}"

    @staticmethod
    def get_diode_current_limits():
        return "Lm?"

    @staticmethod
    def get_diode_currents():
        return "Lr?"

    @staticmethod
    def set_diode_name(index: int,name :str):
        return f"Ln{index} {name}"

    @staticmethod
    def get_diode_names():
        return "Ln?"

    @staticmethod
    def get_enabled_diodes():
        return "Le"

    @staticmethod
    def reset_time_counter():
        return "tz"

    @staticmethod
    def function_save():
        return "f s"