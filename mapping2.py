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

mapping = {
    16: {
        "name": "z_unknown_NwoNode_16",
        "unit": "",
        "transformation": transform_any
    },
    17: {
        "name": "z_unknown_NwoNode_17",
        "unit": "",
        "transformation": transform_any
    },
    18: {
        "name": "z_unknown_NwoNode_18",
        "unit": "",
        "transformation": transform_any
    },
    33: {
        "name": "z_unknown_Value_33",
        "unit": "",
        "transformation": transform_any
    },
    49: {
        "name": "z_unknown_Value_49",
        "unit": "",
        "transformation": transform_any
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
        "transformation": lambda x: float(x[0])
    },
    72: {
        "name": "z_unknown_Value_72",
        "unit": "",
        "transformation": transform_any
    },
    81: {
        "name": "Timer1",
        "unit": "s",
        "transformation": transform_any
    },
    82: {
        "name": "Timer2",
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
        "name": "Timer5",
        "unit": "s",
        "transformation": transform_any
    },
    86: {
        "name": "Timer6",
        "unit": "s",
        "transformation": transform_any
    },
    87: {
        "name": "Timer7",
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
    192: {
        "name": "days_until_next_filter_change",
        "unit": "days",
        "transformation": transform_air_volume
    },
    208: {
        "name": "z_Unknown_TempHumConf_208",
        "unit": "",
        "transformation": transform_any
    },
    209: {
        "name" : "RMOT",
        "unit":"°C",
        "transformation":transform_temperature
    },
    210: {
        "name": "z_Unknown_TempHumConf_210",
        "unit": "",
        "transformation": transform_any
    },
    211: {
        "name": "z_Unknown_TempHumConf_211",
        "unit": "",
        "transformation": transform_any
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
        "name": "z_Unknown_VentConf_224",
        "unit": "",
        "transformation": transform_any
    },
    225: {
        "name": "z_Unknown_VentConf_225",
        "unit": "",
        "transformation": transform_any
    },
    226: {
        "name": "z_Unknown_VentConf_226",
        "unit": "",
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
        "name": "z_Unknown_VentConf_230",
        "unit": "",
        "transformation": transform_any
    },
    256: {
        "name": "z_Unknown_NodeConf_256",
        "unit": "unknown",
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
