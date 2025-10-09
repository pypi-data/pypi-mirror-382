class MacLidSensorError(Exception):
    pass


class MacLidAngleSensorNotFoundError(MacLidSensorError):
    pass


class MacLidAngleReadError(MacLidSensorError):
    pass
