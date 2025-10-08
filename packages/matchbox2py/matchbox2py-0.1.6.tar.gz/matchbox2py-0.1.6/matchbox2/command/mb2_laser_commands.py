class LaserCommands:
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
    def set_laser_off():
        return "e 0"

    @staticmethod
    def set_laser_on():
        return "e 1"

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
    def get_mode():
        return "r m"

    @staticmethod
    def reset_time_counter():
        return "tz"

    @staticmethod
    def get_optical_power_calibration_table():
        return "f g"

    @staticmethod
    def set_optical_power_calibration_parameters(calibration_mode_index, start_value, step):
        return "f o "+str(start_value)+" "+str(step) + " "+str(calibration_mode_index)

    @staticmethod
    def set_optical_power_calibration_table_element(index, power_watt):
        return "f u "+str(index) + " " + str(power_watt)

    @staticmethod
    def set_max_optical_power(optical_power:int):
        return "f 4 "+str(optical_power)

    @staticmethod
    def set_optical_power(optical_power:float):
        return "c 4 "+str(optical_power)

    @staticmethod
    def get_set_optical_power():
        return "c 4 ?"

    @staticmethod
    def set_current(current):
        return "c 3 "+str(current)

    @staticmethod
    def function_save():
        return "f s"