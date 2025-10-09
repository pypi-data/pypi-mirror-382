import hid

from maclidsensor.constants import FEATURE_REPORT_ID
from maclidsensor.constants import PRODUCT_ID
from maclidsensor.constants import USAGE
from maclidsensor.constants import USAGE_PAGE
from maclidsensor.constants import VENDOR_ID
from maclidsensor.exceptions import MacLidAngleReadError
from maclidsensor.exceptions import MacLidAngleSensorNotFoundError


class LidSensor:
    def __init__(self):
        self.device = None
        self._connect()

    def _connect(self):
        devices = hid.enumerate(VENDOR_ID, PRODUCT_ID)
        for dev_info in devices:
            if (
                dev_info.get("usage_page") == USAGE_PAGE
                and dev_info.get("usage") == USAGE
            ):

                path = dev_info["path"]
                if isinstance(path, str):
                    path = path.encode("utf-8")

                d = hid.device()
                d.open_path(path)

                # check
                try:
                    d.get_feature_report(FEATURE_REPORT_ID, 8)
                    self.device = d
                    return
                except Exception:
                    d.close()

        raise MacLidAngleSensorNotFoundError(
            "MacBook lid angle sensor not found."
        )

    def read(self):
        if not self.device:
            raise MacLidAngleSensorNotFoundError(
                "MacBook lid angle sensor not found."
            )
        try:
            data = self.device.get_feature_report(FEATURE_REPORT_ID, 8)
            if data and len(data) >= 3:
                low = data[1]
                high = data[2]
                return float((high << 8) | low)
        except Exception:
            raise MacLidAngleReadError("Unable to read lid angle.")
        return None
