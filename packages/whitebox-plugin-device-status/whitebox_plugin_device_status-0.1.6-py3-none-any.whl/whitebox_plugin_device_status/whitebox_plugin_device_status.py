import whitebox


class WhiteboxPluginDeviceStatus(whitebox.Plugin):
    name = "Device Status"

    provides_capabilities = ["device-status"]
    slot_component_map = {
        "device-status.sdr": "SDRStatus",
        "device-status.gps": "GPSStatus",
    }
    exposed_component_map = {
        "device-status": {
            "sdr": "SDRStatus",
            "gps": "GPSStatus",
        }
    }


plugin_class = WhiteboxPluginDeviceStatus
