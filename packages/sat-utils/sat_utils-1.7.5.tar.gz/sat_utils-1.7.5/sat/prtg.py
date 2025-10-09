import requests
from requests.adapters import HTTPAdapter, Retry

from sat.logs import SATLogger

logger = SATLogger(name=__name__)


class PRTGHandler:
    def __init__(
        self,
        base_url: str,
        sensor_guid: str,
        session: requests.Session = requests.Session(),
        retry_total: int = 5,
    ):
        self.base_url = base_url
        self.sensor_guid = sensor_guid
        self.sensor_request_string = f"{self.base_url}/{self.sensor_guid}"

        self.session = session

        retries = Retry(
            total=retry_total, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504]
        )

        self.session.mount("http://", HTTPAdapter(max_retries=retries))

    def metric_to_prtg(self, value: float, text: str = None) -> bool:
        """Sends a success metric to PRTG, with an optional text field explaining the result"""
        param_dict = {"value": value}

        if text:
            param_dict["text"] = text

        response = self.session.get(self.sensor_request_string, params=param_dict)

        if response.status_code != 200:
            logger.warning(f"PRTG push failed, error code of {response.status_code}")
            return False

        return True

    def error_to_prtg(self, text: str = None) -> bool:
        """Sends an error message to PRTG for errors the application"""
        param_dict = {}

        if text:
            param_dict["text"] = text

        response = self.session.get(self.sensor_request_string, params=param_dict)

        if response.status_code != 200:
            logger.warning(f"Push to PRTG failed, error code of {response.status_code}")
            return False
        return True
