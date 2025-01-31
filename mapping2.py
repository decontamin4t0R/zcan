from struct import unpack

def transform_temperature(value: list) -> float:
    parts = bytes(value[0:2])
    word = unpack('<h', parts)[0]
    return float(word)/10


def transform_air_volume(value: list) -> float:
    parts = value[0:2]
    word = unpack('<h', parts)[0]
    return float(word)

def transform_any(value: list) -> float:
    word = 0
    for n in range(len(value)):
        word += value[n]<<(n*8)
    return word

def transform_enum(enum: dict):
    def f(value: list) -> str:
        v = int(value[0])
        if v in enum:
            return enum[v]
        return "unknown"
    return f

def uint_to_bits(value):
    """Convert an unsigned integer to a list of set bits."""
    bits = []
    j = 0
    for i in range(64):
        if value & (1 << i):
            bits.append(j)
        j += 1
    return bits

def calculate_airflow_constraints(value):
    """Calculate the airflow constraints based on the bitshift value."""
    bits = uint_to_bits(value)
    if 45 not in bits:
        return []

    constraints = []
    if 2 in bits or 3 in bits:
        constraints.append("Resistance")
    if 4 in bits:
        constraints.append("PreheaterNegative")
    if 5 in bits or 7 in bits:
        constraints.append("NoiseGuard")
    if 6 in bits or 8 in bits:
        constraints.append("ResistanceGuard")
    if 9 in bits:
        constraints.append("FrostProtection")
    if 10 in bits:
        constraints.append("Bypass")
    if 12 in bits:
        constraints.append("AnalogInput1")
    if 13 in bits:
        constraints.append("AnalogInput2")
    if 14 in bits:
        constraints.append("AnalogInput3")
    if 15 in bits:
        constraints.append("AnalogInput4")
    if 16 in bits:
        constraints.append("Hood")
    if 18 in bits:
        constraints.append("AnalogPreset")
    if 19 in bits:
        constraints.append("ComfoCool")
    if 22 in bits:
        constraints.append("PreheaterPositive")
    if 23 in bits:
        constraints.append("RFSensorFlowPreset")
    if 24 in bits:
        constraints.append("RFSensorFlowProportional")
    if 25 in bits:
        constraints.append("TemperatureComfort")
    if 26 in bits:
        constraints.append("HumidityComfort")
    if 27 in bits:
        constraints.append("HumidityProtection")
    if 47 in bits:
        constraints.append("CO2ZoneX1")
    if 48 in bits:
        constraints.append("CO2ZoneX2")
    if 49 in bits:
        constraints.append("CO2ZoneX3")
    if 50 in bits:
        constraints.append("CO2ZoneX4")
    if 51 in bits:
        constraints.append("CO2ZoneX5")
    if 52 in bits:
        constraints.append("CO2ZoneX6")
    if 53 in bits:
        constraints.append("CO2ZoneX7")
    if 54 in bits:
        constraints.append("CO2ZoneX8")

    return constraints

def transform_ventilation_constraints(value: list) -> str:
    print(value)
    value = bytes(value[0:8])
    print(value)
    value = int.from_bytes(value, "little")
    print(value)
    return ", ".join(calculate_airflow_constraints(value))

device_state_arr = ["init", "normal", "filterwizard", "commissioning", "supplierfactory", "zehnderfactory", "standby", "away", "DFC"]
changing_filters_arr = ["active", "changing_filter"]
operating_mode_enum = {-1: "auto", 1: "limited manual", 5: "unlimited manual"}
bypass_mode_enum = {0: "auto", 1: "open", 2: "close"}
sensor_based_enum = {0: "disabled", 1: "active", 2:"overruling"}

mapping = {
    16: {
        "name": "device_state",
        "unit": "".join(["%s=%s" % x for x in enumerate(device_state_arr)]),
        "transformation": lambda x: (device_state_arr[int(x[0])] if int(x[0]) < len(device_state_arr) else "unknown")
    },
    17: {
        "name": "z_unknown_NwoNode_17",
        "unit": "",
        "transformation": transform_any
    },
    18: {
        "name": "changing_filters",
        "unit": "".join(["%s=%s" % x for x in enumerate(changing_filters_arr)]),
        "transformation": lambda x: (changing_filters_arr[int(x[0])] if int(x[0]) < len(changing_filters_arr) else "unknown")
    },
    33: {
        "name": "z_unknown_Value_33",
        "unit": "",
        "transformation": transform_any
    },
    49: {
        "name": "operating_mode",
        "unit": "-1=auto,1=limited_manual,5=unlimited_manual",
        "transformation": transform_enum(operating_mode_enum)
    },
    56: {
        "name": "z_unknown_Value_56",
        "unit": "",
        "transformation": transform_any
    },
    65: {
        "name": "ventilation_level",
        "unit": "level",
        "transformation": lambda x: float(x[0])
    },
    66: {
        "name": "bypass_state",
        "unit": "0=auto,1=open,2=close",
        "transformation": transform_enum(bypass_mode_enum)
    },
    67: {
        "name": "comfocool_profile",
        "unit": "",
        "transformation": lambda x: int(x[0])
    },
    72: {
        "name": "z_unknown_Value_72",
        "unit": "",
        "transformation": transform_any
    },
    81: {
        "name": "Timer1_fan_speed_next_change",
        "unit": "s",
        "transformation": transform_any
    },
    82: {
        "name": "Timer2_bypass_next_change",
        "unit": "s",
        "transformation": transform_any
    },
    83: {
        "name": "Timer3",
        "unit": "s",
        "transformation": transform_any
    },
    84: {
        "name": "Timer4",
        "unit": "s",
        "transformation": transform_any
    },
    85: {
        "name": "Timer5_comfocool_next_change",
        "unit": "s",
        "transformation": transform_any
    },
    86: {
        "name": "Timer6_supply_fan_next_change",
        "unit": "s",
        "transformation": transform_any
    },
    87: {
        "name": "Timer7_exhaust_fan_next_change",
        "unit": "s",
        "transformation": transform_any
    },
    88: {
        "name": "Timer8",
        "unit": "s",
        "transformation": transform_any
    },
    96: {
        "name": "bypass_..._ValveMsg",
        "unit": "unknown",
        "transformation": transform_any
    },
    97: {
        "name": "bypass_b_status",
        "unit": "unknown",
        "transformation": transform_air_volume
    },
    98: {
        "name": "bypass_a_status",
        "unit": "unknown",
        "transformation": transform_air_volume
    },
    115: {
        "name": "ventilator_enabled_output",
        "unit": "",
        "transformation": transform_any
    },
    116: {
        "name": "ventilator_enabled_input",
        "unit": "",
        "transformation": transform_any
    },
    117: {
        "name": "ventilator_power_percent_output",
        "unit": "%",
        "transformation": lambda x: float(x[0])
    },
    118: {
        "name": "ventilator_power_percent_input",
        "unit": "%",
        "transformation": lambda x: float(x[0])
    },
    119: {
        "name": "ventilator_air_volume_output",
        "unit": "m3",
        "transformation": transform_air_volume
    },
    120: {
        "name": "ventilator_air_volume_input",
        "unit": "m3",
        "transformation": transform_air_volume
    },
    121: {
        "name": "ventilator_speed_output",
        "unit": "rpm",
        "transformation": transform_air_volume
    },
    122: {
        "name": "ventilator_speed_input",
        "unit": "rpm",
        "transformation": transform_air_volume
    },
    128: {
        "name": "Power_consumption_actual",
        "unit": "W",
        "transformation": lambda x: float(x[0])
    },
    129: {
        "name": "Power_consumption_this_year",
        "unit": "kWh",
        "transformation": transform_air_volume
    },
    130: {
        "name": "Power_consumption_lifetime",
        "unit": "kWh",
        "transformation": transform_air_volume
    },
    144: {
        "name": "Power_PreHeater_this_year",
        "unit": "kWh",
        "transformation": transform_any
    },
    145: {
        "name": "Power_PreHeater_total",
        "unit": "kWh",
        "transformation": transform_any
    },
    146: {
        "name": "Power_PreHeater_actual",
        "unit": "W",
        "transformation": transform_any
    },
    176: {
        "name": "rf_pairing_mode",
        "unit": "0=not_running,1=running,2=done,3=failed,4=aborted",
        "transformation": transform_any
    },
    192: {
        "name": "days_until_next_filter_change",
        "unit": "days",
        "transformation": transform_air_volume
    },
    208: {
        "name": "device_temperature_unit",
        "unit": "0=celsius,1=fahrenheit",
        "transformation": transform_any
    },
    209: {
        "name": "RMOT",
        "unit": "°C",
        "transformation":transform_temperature
    },
    210: {
        "name": "heating_season_active",
        "unit": "0=inactive,1=active",
        "transformation": lambda x: "active" if int(x[0]) == 1 else "inactive"
    },
    211: {
        "name": "cooling_season_active",
        "unit": "0=inactive,1=active",
        "transformation": lambda x: "active" if int(x[0]) == 1 else "inactive"
    },
    212: {
        "name": "Target_temperature",
        "unit": "°C",
        "transformation": transform_temperature
    },
    213: {
        "name": "Power_avoided_heating_actual",
        "unit": "W",
        "transformation": transform_any
    },
    214: {
        "name": "Power_avoided_heating_this_year",
        "unit": "kWh",
        "transformation": transform_air_volume
    },
    215: {
        "name": "Power_avoided_heating_lifetime",
        "unit": "kWh",
        "transformation": transform_air_volume
    },
    216: {
        "name": "Power_avoided_cooling_actual",
        "unit": "W",
        "transformation": transform_any
    },
    217: {
        "name": "Power_avoided_cooling_this_year",
        "unit": "kWh",
        "transformation": transform_air_volume
    },
    218: {
        "name": "Power_avoided_cooling_lifetime",
        "unit": "kWh",
        "transformation": transform_air_volume
    },
    219: {
        "name": "Power_PreHeater_Target",
        "unit": "W",
        "transformation": transform_any
    },
    220: {
        "name": "temperature_inlet_before_preheater",
        "unit": "°C",
        "transformation": transform_temperature
    },
    221: {
        "name": "temperature_inlet_after_recuperator",
        "unit": "°C",
        "transformation": transform_temperature
    },
    222: {
        "name": "z_Unknown_TempHumConf_222",
        "unit": "",
        "transformation": transform_any
    },
    224: {
        "name": "device_airflow_unit",
        "unit": "1=kg/h,2=l/s,3=m3/h",
        "transformation": transform_any
    },
    225: {
        "name": "sensor_based_ventilation",
        "unit": "0=disabled, 1=active, 2=overruling",
        "transformation": transform_enum(sensor_based_enum)
    },
    226: {
        "name": "fan_speed_0_100_200_300",
        "unit": "0,100,200,300",
        "transformation": transform_any
    },
    227: {
        "name": "bypass_open",
        "unit": "%",
        "transformation": lambda x: float(x[0])
    },
    228: {
        "name": "frost_disbalance",
        "unit": "%",
        "transformation": lambda x: float(x[0])
    },
    229: {
        "name": "z_Unknown_VentConf_229",
        "unit": "",
        "transformation": transform_any
    },
    230: {
        "name": "ventilation_constraints",
        "unit": "",
        "transformation": transform_ventilation_constraints
    },
    256: {
        "name": "current_menu_mode",
        "unit": "1=basic,2=advanced,3=installer",
        "transformation": transform_any
    },
    257: {
        "name": "z_Unknown_NodeConf_257",
        "unit": "unknown",
        "transformation": transform_any
    },
    273: {
        "name": "temperature_something...",
        "unit": "°C",
        "transformation": transform_temperature
    },
    274: {
        "name": "temperature_outlet_before_recuperator",
        "unit": "°C",
        "transformation": transform_temperature
    },
    275: {
        "name": "temperature_outlet_after_recuperator",
        "unit": "°C",
        "transformation": transform_temperature
    },
    276: {
        "name": "temperature_inlet_before_preheater",
        "unit": "°C",
        "transformation": transform_temperature
    },
    277: {
        "name": "temperature_inlet_before_recuperator",
        "unit": "°C",
        "transformation": transform_temperature
    },
    278: {
        "name": "temperature_inlet_after_recuperator",
        "unit": "°C",
        "transformation": transform_temperature
    },
    289: {
        "name": "z_unknown_HumSens",
        "unit": "",
        "transformation": transform_any
    },
    290: {
        "name": "air_humidity_outlet_before_recuperator",
        "unit": "%",
        "transformation": lambda x: float(x[0])
    },
    291: {
        "name": "air_humidity_outlet_after_recuperator",
        "unit": "%",
        "transformation": lambda x: float(x[0])
    },
    292: {
        "name": "air_humidity_inlet_before_preheater",
        "unit": "%",
        "transformation": lambda x: float(x[0])
    },
    293: {
        "name": "air_humidity_inlet_before_recuperator",
        "unit": "%",
        "transformation": lambda x: float(x[0])
    },
    294: {
        "name": "air_humidity_inlet_after_recuperator",
        "unit": "%",
        "transformation": lambda x: float(x[0])
    },
    305: {
        "name": "PresSens_exhaust",
        "unit": "Pa",
        "transformation": transform_any
    },
    306: {
        "name": "PresSens_inlet",
        "unit": "Pa",
        "transformation": transform_any
    },
    337: {
        "name": "z_unknown_Value_337",
        "unit": "",
        "transformation": transform_any
    },
    344: {
        "name": "z_unknown_Value_344",
        "unit": "",
        "transformation": transform_any
    },
    369: {
        "name": "z_Unknown_AnalogInput_369",
        "unit": "V?",
        "transformation": transform_any
    },
    370: {
        "name": "z_Unknown_AnalogInput_370",
        "unit": "V?",
        "transformation": transform_any
    },
    371: {
        "name": "z_Unknown_AnalogInput_371",
        "unit": "V?",
        "transformation": transform_any
    },
    372: {
        "name": "z_Unknown_AnalogInput_372",
        "unit": "V?",
        "transformation": transform_any
    },
    385: {
        "name": "z_unknown_Value_385",
        "unit": "",
        "transformation": transform_any
    },
    400: {
        "name": "z_Unknown_PostHeater_ActualPower",
        "unit": "W",
        "transformation": transform_any
    },
    401: {
        "name": "z_Unknown_PostHeater_ThisYear",
        "unit": "kWh",
        "transformation": transform_any
    },
    402: {
        "name": "z_Unknown_PostHeater_Total",
        "unit": "kWh",
        "transformation": transform_any
    },
    418: {
        "name": "z_unknown_Value_418",
        "unit": "",
        "transformation": transform_any
    },
    513: {
        "name": "z_unknown_Value_513",
        "unit": "",
        "transformation": transform_any
    },
    514: {
        "name": "z_unknown_Value_514",
        "unit": "",
        "transformation": transform_any
    },
    515: {
        "name": "z_unknown_Value_515",
        "unit": "",
        "transformation": transform_any
    },
    516: {
        "name": "z_unknown_Value_516",
        "unit": "",
        "transformation": transform_any
    },
    517: {
        "name": "z_unknown_Value_517",
        "unit": "",
        "transformation": transform_any
    },
    518: {
        "name": "z_unknown_Value_518",
        "unit": "",
        "transformation": transform_any
    },
    519: {
        "name": "z_unknown_Value_519",
        "unit": "",
        "transformation": transform_any
    },
    520: {
        "name": "z_unknown_Value_520",
        "unit": "",
        "transformation": transform_any
    },
    521: {
        "name": "z_unknown_Value_521",
        "unit": "",
        "transformation": transform_any
    },
    522: {
        "name": "z_unknown_Value_522",
        "unit": "",
        "transformation": transform_any
    },
    523: {
        "name": "z_unknown_Value_523",
        "unit": "",
        "transformation": transform_any
    },
    16400: {
        "name": "z_unknown_Value_16400",
        "unit": "",
        "transformation": transform_any
    },
#00398041 unknown 0 0 0 0 0 0 0 0
}

command_mapping = {
    "set_ventilation_level_0": b'T1F07505180100201C00000000\r',
    "set_ventilation_level_1": b'T1F07505180100201C00000100\r',
    "set_ventilation_level_2": b'T1F07505180100201C00000200\r',
    "set_ventilation_level_3": b'T1F07505180100201C00000300\r',
    "auto_mode": b'T1F075051485150801\r', # verified (also: T1F051051485150801\r)
    "manual_mode": b'T1F07505180084150101000000\r', # verified (also: T1F051051485150801\r)
    "temperature_profile_cool": b'T0010C041101\r',
    "temperature_profile_normal": b'T0010C041100\r',
    "temperature_profile_warm": b'T0010C041102\r',
    "close_bypass": b'T00108041102\r',
    "open_bypass": b'T00108041101\r',
    "auto_bypass": b'T00108041100\r',
    "basis_menu": b"T00400041100\r",
    "extended_menu": b"T00400041101\r"
}
