import requests
import bode_logger


class Requester:
    def __init__(self):
        self.count = 0

    def request(self, *args, **kwargs):
        response = requests.request(*args, **kwargs)
        self.count += 1
        return response

    def report_n_requests(self):
        bode_logger.info(f"n-requests-made:{self.count}")
